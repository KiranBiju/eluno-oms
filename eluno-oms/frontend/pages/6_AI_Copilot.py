"""AI Operations Chatbot page."""

import frontend.bootstrap  # noqa: F401
import streamlit as st

from api_client import api

st.set_page_config(page_title="AI Chatbot | Eluno OMS", layout="wide")
st.title("🤖 AI Chatbot for Operations")
st.caption("Ask operational questions about orders, SLAs, inventory, and bottlenecks.")

SUGGESTIONS = [
    "Which orders are at highest risk?",
    "Show all breached orders.",
    "Which lens types cause the most delays?",
    "What inventory should be restocked?",
    "What are today's operational bottlenecks?",
    "Why is Order #1 delayed?",
]

if "copilot_messages" not in st.session_state:
    st.session_state.copilot_messages = []

for msg in st.session_state.copilot_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Ask about orders, SLAs, inventory, or bottlenecks...")

if question:
    st.session_state.copilot_messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing operational data..."):
            try:
                result = api.ask_copilot(question)
                answer = result.get("answer", "No response.")
                st.markdown(answer)
                st.session_state.copilot_messages.append({"role": "assistant", "content": answer})
            except Exception as exc:
                err = f"Copilot error: {exc}"
                st.error(err)
                st.session_state.copilot_messages.append({"role": "assistant", "content": err})

st.divider()
st.subheader("Suggested Questions")
cols = st.columns(2)
for i, suggestion in enumerate(SUGGESTIONS):
    if cols[i % 2].button(suggestion, key=f"sug_{i}"):
        st.session_state.copilot_messages.append({"role": "user", "content": suggestion})
        try:
            result = api.ask_copilot(suggestion)
            st.session_state.copilot_messages.append({
                "role": "assistant",
                "content": result.get("answer", "No response."),
            })
        except Exception as exc:
            st.session_state.copilot_messages.append({"role": "assistant", "content": str(exc)})
        st.rerun()

if st.button("Clear Chat"):
    st.session_state.copilot_messages = []
    st.rerun()
