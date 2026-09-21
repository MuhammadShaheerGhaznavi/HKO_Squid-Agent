import json

import streamlit as st

from agent_graph import stream_query_events
from scripts.wiki_retriever import WikiRetriever

st.set_page_config(page_title="LLM Wiki Query Agent", page_icon="📚", layout="wide")

# How much of each tool result to show in the Reasoning expander
RESULT_PREVIEW_CHARS = 6000

EMOJI = {
    "search_wiki": "🔍",
    "read_page": "📖",
    "get_related": "🔗",
    "read_raw_source": "📄",
}


@st.cache_resource
def get_retriever() -> WikiRetriever:
    """Cached across Streamlit re-runs — loaded once, reused forever."""
    return WikiRetriever()


@st.cache_data
def get_wiki_stats(_retriever: WikiRetriever) -> dict:
    by_type = {}
    for e in _retriever._entries_list:
        by_type[e.type] = by_type.get(e.type, 0) + 1
    return by_type


def _format_args(args: dict) -> str:
    if not args:
        return "(no args)"
    return ", ".join(f"{k}={json.dumps(v, ensure_ascii=False)}" for k, v in args.items())


def _preview_result(content: str, limit: int = RESULT_PREVIEW_CHARS) -> str:
    text = content or ""
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n\n… truncated ({len(text)} chars total; showing first {limit})"


def render_reasoning(steps: list, *, expanded: bool = False, key: str | None = None):
    if not steps:
        return
    expander_kwargs = {"expanded": expanded}
    if key is not None:
        expander_kwargs["key"] = key
    with st.expander(f"Reasoning steps ({len(steps)})", **expander_kwargs):
        for i, step in enumerate(steps, 1):
            stype = step.get("type")
            if stype == "tool_call":
                name = step.get("name", "tool")
                mark = EMOJI.get(name, "🔧")
                label = step.get("label") or name
                st.markdown(f"**{i}. {mark} {label}**")
                st.code(_format_args(step.get("args") or {}), language="text")
            elif stype == "tool_result":
                name = step.get("name", "tool")
                content = step.get("content") or ""
                empty = not content.strip()
                st.markdown(
                    f"**↳ Result from `{name}`**"
                    + (" — ⚠️ empty / no content" if empty else f" — {len(content)} chars")
                )
                st.code(_preview_result(content), language="text")
            elif stype == "error":
                st.error(step.get("content", "Unknown error"))
            st.divider()


retriever = get_retriever()
stats = get_wiki_stats(retriever)

st.title("LLM Wiki Query Agent")
st.caption("Ask questions about the knowledge base — the agent searches, reads, and synthesizes answers from the wiki.")

with st.sidebar:
    st.header("Wiki Overview")
    st.metric("Indexed Entries", len(retriever._entries_list))

    for t, count in sorted(stats.items()):
        st.caption(f"**{t}s**: {count}")

    st.divider()
    st.subheader("Quick Search")
    quick_query = st.text_input("Search wiki entries", key="sidebar_search")
    if quick_query:
        results = retriever.hybrid_search(quick_query, top_k=5)
        if results:
            for r in results:
                st.write(f"**{r.entry.title}**")
                st.caption(f"`{r.entry.path}` — score: {r.score:.3f}")
        else:
            st.caption("No matches.")

    st.divider()
    st.caption("Using DeepSeek API via LangGraph ReAct agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            render_reasoning(
                msg.get("reasoning") or [],
                expanded=False,
                key=f"hist_reason_{idx}",
            )
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question about the wiki..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status = st.status("Thinking...", expanded=True)
        reason_box = st.empty()
        answer_placeholder = st.empty()

        reasoning_steps: list = []
        answer_text = ""
        open_call = None

        for event in stream_query_events(prompt):
            etype = event.get("type")

            if etype == "tool_call":
                open_call = {
                    "type": "tool_call",
                    "name": event.get("name", "tool"),
                    "args": event.get("args") or {},
                    "label": event.get("label") or event.get("name", "tool"),
                }
                reasoning_steps.append(open_call)
                status.update(
                    label=f"Running: {open_call['label']}",
                    state="running",
                    expanded=True,
                )
                with reason_box.container():
                    render_reasoning(
                        reasoning_steps,
                        expanded=True,
                        key=f"live_reason_{len(reasoning_steps)}",
                    )

            elif etype == "tool_result":
                reasoning_steps.append({
                    "type": "tool_result",
                    "name": event.get("name") or (open_call or {}).get("name", "tool"),
                    "content": event.get("content") or "",
                })
                open_call = None
                status.update(label="Got tool result…", state="running", expanded=True)
                with reason_box.container():
                    render_reasoning(
                        reasoning_steps,
                        expanded=True,
                        key=f"live_reason_{len(reasoning_steps)}",
                    )

            elif etype == "answer":
                answer_text = (event.get("content") or "").strip()
                status.update(label="Writing answer...", state="running", expanded=False)
                answer_placeholder.markdown(answer_text)

            elif etype == "error":
                reasoning_steps.append({
                    "type": "error",
                    "content": event.get("content") or "Unknown error",
                })
                status.update(label="Error", state="error", expanded=True)
                with reason_box.container():
                    render_reasoning(reasoning_steps, expanded=True, key="live_reason")

        status.update(label="Complete", state="complete", expanded=False)
        with reason_box.container():
            render_reasoning(reasoning_steps, expanded=False, key="final_reason")

        if not answer_text:
            answer_text = "I couldn't find enough information in the wiki to answer that question."
        answer_placeholder.markdown(answer_text)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer_text,
            "reasoning": reasoning_steps,
        })
