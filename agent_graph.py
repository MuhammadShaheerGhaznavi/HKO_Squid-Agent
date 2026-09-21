import sys
from typing import Annotated, Any, Dict, List, Literal, Optional, Generator
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from scripts.wiki_retriever import WikiRetriever, count_tokens
from config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, LLM_MODEL,
    MAX_AGENT_ITERATIONS, TOKEN_BUDGET, LLM_TEMPERATURE,
    TOP_K_SEARCH, MAX_TOKENS_PER_PAGE,
)

_retriever = WikiRetriever()


@tool
def search_wiki(query: str) -> str: # search for wiki pages matching query
    """Search the LLM wiki for pages matching a keyword query. Returns ranked results with title, summary, type, and path. Use this first for any factual question, including visas, customs, health, and cargo. Do not use it for greetings or small talk."""
    return _retriever.search_and_format(query)


@tool
def read_page(path: str) -> str:
    """Read the full content of a wiki page by its relative path or title (e.g., 'concepts/bigtable-data-model.md' or page title 'Bigtable Data Model'). Auto-resolves titles to file paths. Use this after finding relevant pages via search_wiki."""
    return _retriever.read_page_resolved(path)


@tool
def get_related(path: str) -> str:
    """Get wiki-linked and backlinked pages related to a given page path. Use this to discover adjacent concepts for a more complete picture."""
    related = _retriever.get_related_pages(path)
    if not related:
        return f"No related pages found for '{path}'."
    lines = [f"Pages related to '{path}':"]
    for rp in related:
        entry = _retriever.get_entry(rp)
        title = entry.title if entry else rp
        lines.append(f"  - {title} (`{rp}`)")
    return "\n".join(lines)


@tool
def read_raw_source(filename: str, search: str = "", focus: str = "") -> str:
    """Read a raw source file excerpt. If 'search' is provided (e.g., 'GEN 2.7'), jumps to that AIP section via the TOC index. Optional 'focus' (e.g., 'May' or '3 May') prioritizes pages inside that section that contain the term — use it for day/month lookups in tables. Supports .md, .txt, and .pdf files."""
    return _retriever.read_raw_source(filename, search=search, focus=focus)


WIKI_TOOLS = [search_wiki, read_page, get_related, read_raw_source]


SYSTEM_PROMPT = """You are a helpful assistant for an LLM Wiki compiled from AIP Hong Kong.

The wiki covers the whole AIP, not only aircraft operations. Entry rules, visas, customs, import licences, health, cargo, abbreviations, and tables such as sunrise/sunset are in scope. Examples: GEN 1.3 (visa) and GEN 1.4 (customs and import licences).

ANSWER DIRECTLY — do not call any tools — only when the user is:
- greeting, thanking, or making small talk ("hi", "hello", "thanks", "how are you")
- asking what you can do
Reply briefly and naturally. Invite a question about the wiki when it fits.

FOR EVERY OTHER QUESTION, search before you decide whether the wiki can answer:
1. Start with `search_wiki`. Do this even when the question sounds like immigration, customs, trade, or health.
2. Use `read_page` on the most relevant 2-5 pages. Page titles are fine — they resolve to file paths.
3. Use `get_related` only when you need adjacent context.
4. Use `read_raw_source` when a wiki note is missing a critical detail (for example a yes/no that depends on a list in GEN 1.3 or GEN 1.4, or a specific day in a sunrise/sunset table) and you know the source filename or section. For calendar tables, pass search='GEN 2.7' and focus='May' (or the month/day the user asked about).
5. Then write a concise answer. Cite the wiki page title and the AIP section (shown as § GEN 3.1). Example: *"Source: Meteorological Observations at HKIA (GEN 3.1, AIP Hong Kong)"*.

RULES:
- Always finish with a written reply. Never stop after a tool call.
- Stay within 5 tool calls.
- Do not refuse a factual question before searching. Say a topic is outside the wiki only after search, and a raw-source read if the notes are incomplete, fail to cover it.
- If `read_page` returns "[Page not found]", do not retry that path. Use the suggestions, or search once more.
- If search returns nothing useful, try one alternate query, then answer with what you have.
- Do not invent AIP facts. If the wiki and the raw source do not contain the answer, say so and name the section the user should check (e.g. GEN 1.3)."""


class AgentState(TypedDict):
    messages: Annotated[List[Any], add_messages] # The messages list keeps track of the entire conversation history, including instructions, user inputs, AI replies, and tool results
                    # Annotated[T,x] T is the Base Type and x is the custom meta data that can supplement the type hint T
    iteration_count: int


def _llm() -> ChatOpenAI:
    return ChatOpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=4096, # what this for? context window?
    )


def _decide_route(state: AgentState) -> Literal["tools", "__end__"]: # know more
    messages = state.get("messages", [])
    if not messages:
        return "__end__"

    if state.get("iteration_count", 0) >= MAX_AGENT_ITERATIONS:
        return "__end__"

    last_msg = messages[-1]
    if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
        return "tools"
    return "__end__"


def agent_node(state: AgentState) -> Dict[str, Any]:
    llm = _llm().bind_tools(WIKI_TOOLS)
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


def tool_node(state: AgentState) -> Dict[str, Any]:
    messages = state.get("messages", [])
    if not messages:
        return {"messages": []}

    last_msg = messages[-1]
    if not isinstance(last_msg, AIMessage) or not last_msg.tool_calls:
        return {"messages": []}

    tool_messages = []
    for tc in last_msg.tool_calls:
        tool_name = tc["name"]
        tool_args = tc.get("args", {})
        func = {t.name: t for t in WIKI_TOOLS}.get(tool_name) # create Temp dictionary mapping tool names to tool objects, then use .get() to retrieve the actual object 

        if func:
            try:
                result = func.invoke(tool_args)
            except Exception as e:
                result = f"Tool error: {str(e)}"
        else:
            result = f"Unknown tool: {tool_name}"

        tool_messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

    next_iter = state.get("iteration_count", 0) + 1
    return {"messages": tool_messages, "iteration_count": next_iter}


def _build_graph() -> StateGraph:
    builder = StateGraph(AgentState) # State is the memory that gets passed as the graph goes from one step to the other
        # StateGraph is the blue print object to create graph, you pass it the state schema
        # Every node in this graph will receive the current AgentState as its input, and any updates returned by a node must conform to AgentState
        # nodes take state and return updates to the state
    builder.add_node("agent", agent_node)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "agent")

    builder.add_conditional_edges(
        "agent", # start node
        _decide_route, # routing function
        {               # path mapping dictionary
            "tools": "tools",
            "__end__": END,
        },
    )

    builder.add_edge("tools", "agent")

    return builder.compile() # validates graph layout, and tunrn builder into executable CompiledGraph


_graph = _build_graph()


def stream_query_events(
    query: str, max_iterations: int = MAX_AGENT_ITERATIONS
) -> Generator[Dict[str, Any], None, None]:
    """Yield structured agent events for UI / debugging.

    Event shapes:
      {"type": "tool_call", "name": str, "args": dict, "label": str}
      {"type": "tool_result", "name": str, "content": str}
      {"type": "answer", "content": str}
      {"type": "error", "content": str}
    """
    system_msg = SystemMessage(content=SYSTEM_PROMPT)
    user_msg = HumanMessage(content=query)

    state: AgentState = {
        "messages": [system_msg, user_msg],
        "iteration_count": 0,
    }

    display_names = {
        "search_wiki": "Searching wiki",
        "read_page": "Reading page",
        "get_related": "Related pages",
        "read_raw_source": "Raw source",
    }
    pending_names: Dict[str, str] = {}  # tool_call_id → tool name
    prev_msg_count = 0

    for event in _graph.stream(state, stream_mode="values"):
        msgs = event.get("messages", [])
        if not msgs:
            continue

        it_count = event.get("iteration_count", 0)
        if it_count > max_iterations:
            yield {"type": "error", "content": "[Max iterations reached — stopping.]"}
            break

        for msg in msgs[prev_msg_count:]:
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_name = tc["name"]
                    tool_args = tc.get("args", {}) or {}
                    pending_names[tc["id"]] = tool_name
                    yield {
                        "type": "tool_call",
                        "name": tool_name,
                        "args": tool_args,
                        "label": display_names.get(tool_name, tool_name),
                    }

            elif isinstance(msg, ToolMessage):
                tool_name = pending_names.pop(msg.tool_call_id, "unknown")
                yield {
                    "type": "tool_result",
                    "name": tool_name,
                    "content": str(msg.content),
                }

            elif isinstance(msg, AIMessage) and not msg.tool_calls:
                content = str(msg.content or "").strip()
                if content:
                    yield {"type": "answer", "content": content}

        prev_msg_count = len(msgs)


def stream_query(query: str, max_iterations: int = MAX_AGENT_ITERATIONS) -> Generator[str, None, str]:
    last_answer = ""
    emoji = {
        "search_wiki": "🔍",
        "read_page": "📖",
        "get_related": "🔗",
        "read_raw_source": "📄",
    }

    for event in stream_query_events(query, max_iterations):
        etype = event.get("type")
        if etype == "tool_call":
            args = event.get("args") or {}
            args_str = ", ".join(f"{k}={repr(v)}" for k, v in args.items())
            mark = emoji.get(event.get("name", ""), "🔧")
            yield f"\n{'─' * 50}\n"
            yield f"{mark} **{event.get('label', event.get('name'))}** `{args_str}`\n"
        elif etype == "tool_result":
            tool_output = str(event.get("content", ""))
            truncated = tool_output[:800] + "..." if len(tool_output) > 800 else tool_output
            yield f"\n{truncated}\n"
        elif etype == "answer":
            last_answer = str(event.get("content", ""))
            yield f"\n{'─' * 50}\n## Answer\n\n{last_answer}\n"
        elif etype == "error":
            yield f"{event.get('content', '')}\n"

    return last_answer


def run_query(query: str, max_iterations: int = MAX_AGENT_ITERATIONS) -> str:
    final = ""
    in_answer = False
    answer_lines = []
    for chunk in stream_query(query, max_iterations):
        if chunk.strip() == "## Answer":
            in_answer = True
            answer_lines = []
            continue
        if in_answer:
            answer_lines.append(chunk)
            final = "".join(answer_lines).strip()
        sys.stdout.write(chunk)
        sys.stdout.flush()
    return final


def structured_query(query: str, max_iterations: int = MAX_AGENT_ITERATIONS) -> Dict[str, Any]:
    """Runs the ReAct agent and returns structured data: answer, tool_calls, and sources."""
    tool_calls_collected: List[Dict[str, Any]] = []
    sources_collected: List[str] = []
    last_answer = ""
    pending_call: Optional[Dict[str, Any]] = None

    for event in stream_query_events(query, max_iterations):
        etype = event.get("type")
        if etype == "tool_call":
            pending_call = {
                "tool": event.get("name", "unknown"),
                "args": event.get("args") or {},
            }
            if pending_call["tool"] == "read_page":
                page_path = pending_call["args"].get("path", "")
                if page_path and page_path not in sources_collected:
                    sources_collected.append(page_path)
        elif etype == "tool_result":
            result_text = str(event.get("content", ""))
            result_preview = result_text[:500] + "..." if len(result_text) > 500 else result_text
            entry = pending_call or {"tool": event.get("name", "unknown"), "args": {}}
            tool_calls_collected.append({
                "tool": entry.get("tool", event.get("name", "unknown")),
                "args": entry.get("args", {}),
                "result_preview": result_preview,
            })
            pending_call = None
        elif etype == "answer":
            last_answer = str(event.get("content", "")).strip()

    return {
        "query": query,
        "answer": last_answer.strip(),
        "tool_calls": tool_calls_collected,
        "sources": sources_collected,
    }
