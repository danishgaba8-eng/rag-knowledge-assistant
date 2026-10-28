"""Streamlit chat UI: streamlit run app.py"""

import streamlit as st

from rag.assistant import KnowledgeAssistant
from rag.config import ROLE_ACCESS

st.set_page_config(page_title="Harbor & Pine Knowledge Assistant", page_icon="📚", layout="wide")


@st.cache_resource
def get_assistant() -> KnowledgeAssistant:
    return KnowledgeAssistant()


assistant = get_assistant()

with st.sidebar:
    st.header("Settings")
    role = st.selectbox(
        "Signed in as",
        list(ROLE_ACCESS),
        format_func={"employee": "Employee", "manager": "Manager", "hr": "HR team"}.get,
        key="role",
        help="Documents are filtered by role before retrieval, so restricted content never reaches the model.",
    )
    labels = {"all": "public", "manager": "manager-only", "hr": "HR-only"}
    st.caption(f"Can read: {', '.join(labels[a] for a in sorted(ROLE_ACCESS[role]))} documents")
    st.caption(f"Model: {assistant.provider.name}")
    st.divider()
    st.markdown("**Try asking**")
    examples = [
        "Who has to approve a $1,500 expense claim?",
        "I lost my laptop. What should I do?",
        "What service credit applies to a 3-day shipment delay?",
        "What is the salary band for a Dispatcher?",
        "Who is the CEO?",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.pending = ex
    if st.button("Clear chat", type="secondary"):
        st.session_state.messages = []

st.title("📚 Company Knowledge Assistant")
st.caption("Demo: answers staff questions from Harbor & Pine Logistics' SOPs and policies (a fictional company), "
           "with a citation for every answer.")

st.session_state.setdefault("messages", [])


def render_sources(sources: list[dict]) -> None:
    if not sources:
        return
    with st.expander(f"Sources ({len(sources)})"):
        for i, s in enumerate(sources, start=1):
            st.markdown(f"**{s['title']} › {s['section']}**  \n`{s['doc_id']}` · {s['department']} · access: {s['access']}")
            st.caption(s["text"].split("\n", 1)[-1].replace("$", "\\$"))


def md(text: str) -> str:
    # Escape $ so amounts like "$55,000 to $67,000" aren't rendered as LaTeX.
    return text.replace("$", "\\$")


ROLE_LABELS = {"employee": "Employee", "manager": "Manager", "hr": "HR team"}

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(md(msg["content"]))
        if msg.get("asked_as"):
            st.caption(f"Asked as: {ROLE_LABELS[msg['asked_as']]}")
        render_sources(msg.get("sources", []))

question = st.chat_input("Ask about leave, expenses, IT security, shipments...") or st.session_state.pop("pending", None)
if question:
    st.session_state.messages.append({"role": "user", "content": question, "asked_as": role})
    with st.chat_message("user"):
        st.markdown(md(question))
        st.caption(f"Asked as: {ROLE_LABELS[role]}")
    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            answer = assistant.ask(question, role)
        sources = [h.chunk.to_dict() for h in answer.sources]
        st.markdown(md(answer.text))
        render_sources(sources)
    st.session_state.messages.append({"role": "assistant", "content": answer.text, "sources": sources})
