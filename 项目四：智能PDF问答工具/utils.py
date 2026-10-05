from langchain_community.document_loaders import PyPDFium2Loader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.agents import create_agent
from langchain_core.tools import create_retriever_tool
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import SecretStr
from langchain_core.runnables import RunnableConfig
import tempfile
import os

# 全局检查点器：所有会话共享，按 thread_id 分开存储历史
checkpointer = InMemorySaver()

def qa_agent(openai_api_key, uploaded_file, question, thread_id):
    """
    RAG 问答函数（新版）。

    参数:
        openai_api_key: API Key
        uploaded_file:  Streamlit 上传的文件对象
        question:       用户问题
        thread_id:      会话标识（替代原 memory 参数）

    返回:
        AI 的回复文本
    """
    # ============================================================
    # 1. 保存上传的 PDF 到临时文件
    # ============================================================
    file_content = uploaded_file.read()

    # 用 tempfile 生成唯一文件名，避免多个用户互相覆盖
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(file_content)
        temp_pdf_path = temp_file.name

    try:
        # ============================================================
        # 2. 加载 PDF 并分割
        # ============================================================
        #loader = PyPDFLoader(temp_pdf_path)
        loader = PyPDFium2Loader(temp_pdf_path)
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=50,
            separators=["\n", "。", "！", "？", "，", "、", ""],
        )
        texts = text_splitter.split_documents(docs)

        # ============================================================
        # 3. 创建向量存储和 retriever
        # ============================================================
        embeddings_model = OpenAIEmbeddings(
            model="qwen3.7-text-embedding",
            api_key=SecretStr(openai_api_key),
            base_url="https://ws-rf6t5d8qwnu1gjet.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
            check_embedding_ctx_length=False,   # 百炼兼容模式必须加
        )
        db = FAISS.from_documents(texts, embeddings_model)
        retriever = db.as_retriever()

        # ============================================================
        # 4. 把 retriever 包装成 Tool
        # ============================================================
        retriever_tool = create_retriever_tool(
            retriever,
            "pdf_search",
            "搜索用户上传的 PDF 文档，获取与问题相关的片段。当用户询问 PDF 内容、文档细节、文件中的信息时，应调用此工具",
        )

        # ============================================================
        # 5. 创建模型
        # ============================================================
        model = ChatOpenAI(
            model="qwen-plus",
            api_key=SecretStr(openai_api_key),
            base_url="https://ws-rf6t5d8qwnu1gjet.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
        )

        # ============================================================
        # 6. 创建带记忆的 Agent
        # ============================================================
        agent = create_agent(
            model=model,
            tools=[retriever_tool],
            checkpointer=checkpointer,
            system_prompt=(
                "你是一个乐于助人的助手，可以搜索用户上传的 PDF 文档来回答问题。"
                "当用户的问题和 PDF 内容相关时，优先调用 pdf_search 工具检索。"
            ),
        )

        # ============================================================
        # 7. 调用 Agent
        # ============================================================
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

        result = agent.invoke(
            {"messages": [{"role": "user", "content": question}]},
            config=config,
        )
        # return result["messages"][-1].content
        #这里选择返回完整消息列表，目的是调用方可以获取历史消息
        return result["messages"]

    finally:
        # ============================================================
        # 8. 清理临时文件
        # ============================================================
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
