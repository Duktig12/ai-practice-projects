from langchain.agents import create_agent          # 创建带持久化能力的 Agent
from langchain_openai import ChatOpenAI            # 模型（用法不变）
from langgraph.checkpoint.memory import InMemorySaver  # 内存检查点器
# 2. 全局创建一个检查点器实例
#    它的作用相当于旧版的 ConversationBufferMemory，
#    但更底层、更灵活：它在每一步执行后自动保存 Agent 的状态（包括对话历史）。
#    注意：InMemorySaver 把数据存在内存中，进程重启后丢失。
#    生产环境可换成 SqliteSaver 或 PostgresSaver 实现持久化[reference:2]。
checkpointer = InMemorySaver()
def get_chat_response(prompt: str, thread_id: str, openai_api_key: str) -> str:
    """
    带记忆的对话函数。

    参数:
        prompt:        用户输入
        thread_id:     会话标识。同一个 thread_id 会复用历史对话，
                       不同 thread_id 之间历史隔离[reference:3]。
        openai_api_key: 阿里云百炼 API Key

    返回:
        AI 的回复文本
    """

    # 3. 定义模型（和原代码完全一致，无需改动）
    model = ChatOpenAI(
        model="qwen-max",
        api_key = openai_api_key,
        base_url="https://ws-rf6t5d8qwnu1gjet.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
    )

    # 4. 创建 Agent，绑定 checkpointer
    #    create_agent 是 LangChain 1.x 中构建智能体的官方入口，
    #    它运行在 LangGraph 之上，内部自动处理消息格式和历史注入[reference:4]。
    #    tools=[] 表示这个 Agent 不需要任何工具，纯对话。
    #    system_prompt 用来设置系统角色，替代旧版 ConversationChain 的默认 prompt。
    agent = create_agent(
        model=model,
        tools=[],                      # 不需要工具
        checkpointer=checkpointer,     # 关键：传入检查点器，启用短期记忆
        system_prompt="你是一个乐于助人的助手。"  # 可选，设置系统角色
    )

    # 5. 调用 Agent
    #    注意输入格式的变化：
    #    旧版: {"input": "..."}
    #    新版: {"messages": [{"role": "user", "content": "..."}]}
    #
    #    config 中必须包含 thread_id，checkpointer 才知道该用哪个会话的历史。
    config = {"configurable": {"thread_id": thread_id}}

    result = agent.invoke(
        {"messages": [{"role": "user", "content": prompt}]},
        config = config
    )

    # 6. 提取回复文本
    #    result 是一个包含完整消息列表的字典，
    #    最后一条消息就是 AI 的回复。
    return result["messages"][-1].content
    #return result["messages"][-1].content,result
# if __name__ == "__main__":
#     API_KEY = ""   # 替换成你的真实 Key
#     THREAD_ID = "test_005"   # 同一个会话标识
#
#     print("=" * 50)
#     print("第 1 轮：告诉 AI 最喜欢的颜色是蓝色")
#     print("=" * 50)
#     reply, full_result = get_chat_response("我最喜欢的颜色是蓝色，请你记住他", THREAD_ID, API_KEY)
#     print("[AI]", reply)
#     print()
#     print("完整 result 字典：")
#     print(full_result)
#
#     print("=" * 50)
#     print("第 2 轮：问 AI 我最喜欢的颜色是什么")
#     print("=" * 50)
#     reply2, full_result2 = get_chat_response("我最喜欢的颜色是什么？", THREAD_ID, API_KEY)
#     print("[AI]", reply2)
#     print()
#     print("完整 result 字典：")
#     print(full_result2)
#
#     print("=" * 50)
#     reply, full_result = get_chat_response("我上一个问题是什么？", THREAD_ID, API_KEY)
#     print("[AI]", reply)
#     print()
#     print("完整 result 字典：")
#     print(full_result)



