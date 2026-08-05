import streamlit as st
from agent_graph import stream_query, MAX_AGENT_ITERATIONS
from scripts.wiki_retriever import WikiRetriever

st.set_page_config(page_title="LLM Wiki Query Agent", page_icon="📚", layout="wide")


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

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and msg.get("tool_calls"):
            with st.expander("Reasoning steps", expanded=False):
                for tc in msg["tool_calls"]:
                    st.caption(tc)
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question about the wiki..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status = st.status("Searching wiki...", expanded=False)
        answer_placeholder = st.empty()

        tool_calls_log = []
        answer_text = ""

        for chunk in stream_query(prompt):
            stripped = chunk.strip()

            if stripped.startswith("[Tool Call]"):
                label = stripped[len("[Tool Call] "):]
                tool_calls_log.append(label)
                status.update(label=f"Running: {label.split('(')[0]}", state="running")

            elif stripped.startswith("[Tool Result]"):
                result_text = stripped[len("[Tool Result]"):].strip()
                if len(result_text) > 120:
                    result_text = result_text[:120] + "..."
                tool_name = tool_calls_log[-1].split("(")[0] if tool_calls_log else "tool"
                status.update(label=f"Got results from: {tool_name}", state="running")

            elif stripped.startswith("[Max iterations"):
                status.update(label=stripped, state="error")

            elif stripped:
                if answer_text == "":
                    status.update(label="Synthesizing answer...", state="running")
                answer_text += chunk
                answer_placeholder.markdown(answer_text)

        status.update(label="Complete", state="complete")
        if answer_text:
            answer_placeholder.markdown(answer_text)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer_text
            if answer_text
            else "I couldn't find enough information in the wiki to answer that question.",
            "tool_calls": tool_calls_log,
        })
