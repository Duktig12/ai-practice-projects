import streamlit as st
# from langchain.memory import ConversationBufferMemory
import uuid
from utils import get_chat_response

st.title("💬 通义千问")

def init_session_state():
    if "thread_id" not in st.session_state:
        # 每个浏览器会话生成一个唯一的 thread_id
        st.session_state["thread_id"] = str(uuid.uuid4())
        # 不再需要 memory 对象，历史由 checkpointer 管理
        st.session_state["messages"] = [
            {"role": "ai", "content": "你好，我是你的专属AI助手，有什么可以帮你的吗？"}
        ]

with st.sidebar:
    openai_api_key = st.text_input("请输入阿里云百炼 API密钥：", type="password")
    st.markdown("[获取阿里云百炼 API密钥](https://bailian.console.aliyun.com/cn-beijing/model/settings/api-key)")
    st.divider()
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("开启新对话"):
            #清除当前页面状态信息
            st.session_state.clear()
            #重新初始化
            init_session_state()

# if "memory" not in st.session_state:
#     st.session_state["memory"] = ConversationBufferMemory(return_messages=True)
#     st.session_state["messages"] = [{"role": "ai",
#                                      "content": "你好，我是你的AI助手，有什么可以帮你的吗？"}]

# 初始化 session_state，用于存储会话内容
init_session_state()

for message in st.session_state["messages"]:
    #展示session_state里的数据
    st.chat_message(message["role"]).write(message["content"])

#获取用户输入后回车的字符串
prompt = st.chat_input()
if prompt:
    if not openai_api_key:
        st.info("请输入你的OpenAI API Key")
        st.stop()
    st.session_state["messages"].append({"role": "human", "content": prompt})
    st.chat_message("human").write(prompt)

    with st.spinner("AI正在思考中，请稍等..."):
        response = get_chat_response(prompt, st.session_state["thread_id"],
                                     openai_api_key)
    msg = {"role": "ai", "content": response}
    st.session_state["messages"].append(msg)
    st.chat_message("ai").write(response)