"""
RAG Chatbot UI — Streamlit frontend.
Single page: document upload + chat. Calls FastAPI backend.
"""

import streamlit as st
from api_client import send_chat_message


def main():
    st.set_page_config(page_title="RAG Chatbot", page_icon="💬", layout="centered")
    st.title("RAG Chatbot")

    with st.sidebar:
        st.title("RAG Chatbot")
        st.write(
            "This is a chatbot that uses a RAG pipeline to answer questions about the documents uploaded."
        )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Ask me anything about the documents"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        response = send_chat_message(prompt)
        st.session_state.messages.append(
            {"role": "assistant", "content": response["answer"]}
        )
        with st.chat_message("assistant"):
            st.write(response["answer"])


if __name__ == "__main__":
    main()
