from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
"""
generate_script获取视频的标题与脚本内容
"""
#参数：视频主题、视频时长、视频创作性、API密钥
def generate_script(subject, video_length, creativity, api_key):
    #一、创建提示模板，获取标题与脚本内容
    title_template = ChatPromptTemplate.from_messages([
        ("human", "请为'{subject}'这个主题的视频想一个吸引人的标题")
    ])
    script_template = ChatPromptTemplate.from_messages([
        ("human",
             """你是一位短视频频道的博主。根据以下标题和相关信息，为短视频频道写一个视频脚本。
             视频标题：{title}，视频时长：{duration}分钟，生成的脚本的长度尽量遵循视频时长的要求。
             要求开头抓住限球，中间提供干货内容，结尾有惊喜，脚本格式也请按照【开头、中间，结尾】分隔。
             整体内容的表达方式要尽量轻松有趣，吸引年轻人。
             """)
    ])

    # 二、定义模型
    model = ChatOpenAI(model="qwen3-vl-plus",
                       api_key=api_key,
                       base_url="https://ws-rf6t5d8qwnu1gjet.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
                       temperature=creativity)

    #创建链组装
    title_chain = title_template | model
    script_chain = script_template | model

    title = title_chain.invoke({"subject":subject}).content
    script = script_chain.invoke({"title":title, "duration":video_length}).content

    return title, script

#print(generate_script("群星闪耀时",1,0.6,"sk-ws-H.PRRYIPI.hxpk.MEUCIBljhMbjiXvE7R9n1bDIJg3X5uLUgZtyjLTdg36d6yACAiEAk030x-G8dm--FH80InZ011vC96NTLkEnh2MvnvYKvU4"))