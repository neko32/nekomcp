import asyncio

import streamlit as st
from langchain_ollama.llms import OllamaLLM
from langchain_core.messages import AIMessage, HumanMessage

async def main():
    st.title("🐈🐈Make Cat Great Always🐈🐈")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    messages = st.session_state.messages

    for msg in messages:
        with st.chat_message(msg.type):
            st.write(msg.content)

    if prompt := st.chat_input():
        with st.chat_message("human"):
            st.write(prompt)

        messages.append(HumanMessage(prompt))

        llm = OllamaLLM(model = "llama3.1", temperature=1.0)
        ai_resp = await llm.ainvoke(messages)

        messages.append(ai_resp)

        with st.chat_message("ai"):
            st.write(ai_resp)



asyncio.run(main())