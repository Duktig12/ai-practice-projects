import streamlit as st
from utils import qa_agent
import uuid


st.title("📑 AI智能PDF问答工具")

with st.sidebar:
    openai_api_key = st.text_input("请输入阿里云百炼 API密钥：", type="password")
    st.markdown("[获取阿里云百炼 API密钥](https://bailian.console.aliyun.com/cn-beijing/model/settings/api-key)")

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = str(uuid.uuid4())

uploaded_file = st.file_uploader("上传你的PDF文件：", type="pdf")
question = st.text_input("对PDF的内容进行提问", disabled=not uploaded_file)

if uploaded_file and question and not openai_api_key:
    st.info("请输入你的OpenAI API密钥")

if uploaded_file and question and openai_api_key:
    with st.spinner("AI正在思考中，请稍等..."):
        response = qa_agent(openai_api_key, uploaded_file, question,
                            st.session_state["thread_id"])
    st.write("### 答案")
    st.write(response[-1].content)
    st.session_state["chat_history"] = response

if "chat_history" in st.session_state:
    with st.expander("历史消息"):
        for i in range(0, len(st.session_state["chat_history"]), 2):
            human_message = st.session_state["chat_history"][i]
            ai_message = st.session_state["chat_history"][i+1]
            st.write(human_message.content)
            st.write(ai_message.content)
            if i < len(st.session_state["chat_history"]) - 2:
                st.divider()
