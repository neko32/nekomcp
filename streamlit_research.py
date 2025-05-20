import asyncio
import json
from os import getenv

import streamlit as st
from langchain_ollama.llms import OllamaLLM
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient

async def main():
    st.title("🐈🐈Make Cat Great Always🐈🐈")

    mcp_version = "20250520_01"
    mcp_conf_path = f"{getenv("NEKOKAN_CONF_DIR")}/mcpserver/{mcp_version}/nekokanmcp.json"

    with open(mcp_conf_path, "r") as fd:
        mcp_conf = json.load(fd)

    mcp_cl = MultiServerMCPClient(mcp_conf["mcpServers"])
    tools = await mcp_cl.get_tools()

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

        # llm = OllamaLLM(model = "llama3.1", temperature=1.0)
        llm = ChatOpenAI(
            api_key = "ollama",
            model = "llama3.1",
            temperature=1.,
            base_url = "http://localhost:11434/v1"
        )
        
        while True:
            ai_resp = await llm.bind_tools(tools).ainvoke(messages)

            messages.append(ai_resp)

            if isinstance(ai_resp.content, str):
                with st.chat_message("ai"):
                    st.write(ai_resp.content)
            elif isinstance(ai_resp.content, list):
                for content in ai_resp.content:
                    if(content["type"] == "text"):
                        with st.chat_message("ai"):
                            st.write(content["text"])
            
            if ai_resp.tool_calls:
                for tool_call in ai_resp.tool_calls:
                    sel_tool = {tool.name.lower(): tool for tool in tools}[
                        tool_call["name"].lower()
                    ]
                    tool_msg = await sel_tool.ainvoke(tool_call)
                    messages.append(tool_msg)
            else:
                break



asyncio.run(main())