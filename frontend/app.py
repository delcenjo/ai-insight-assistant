import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Insight Assistant", page_icon="")
st.title("AI Insight Assistant")
st.caption("Ask about company policies (documents) or employee data (database).")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = requests.post(f"{BACKEND_URL}/chat", json={"message": prompt}, timeout=60)
            answer = response.json().get("answer") if response.ok else f"Error {response.status_code}: {response.text}"
        except requests.RequestException as error:
            answer = f"Could not reach the backend: {error}"
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
