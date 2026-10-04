from prompt_template import system_template_text, user_template_text
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from xiaohongshu_model import Xiaohongshu
import os
from search import baike_search , baidu_ai_search


#generate_xiaohongshu函数作用是串起 提示模板-模型-输出解析器的全链路
def generate_xiaohongshu(theme, openai_api_key,search_api_key):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_template_text),
        ("user", user_template_text)
    ])
    model = ChatOpenAI(model="qwen3-vl-plus",
                       api_key=openai_api_key,
                       base_url="https://ws-rf6t5d8qwnu1gjet.cn-beijing.maas.aliyuncs.com/compatible-mode/v1")
    output_parser = PydanticOutputParser(pydantic_object=Xiaohongshu)

    search_result = baike_search(theme,search_api_key)

    chain = prompt | model | output_parser
    result = chain.invoke({
        "parser_instructions": output_parser.get_format_instructions(),
        "theme": theme,
        "baike_search":search_result
    })
    #result返回类型为xiaohongshu_model里Xiaohongshu类的实例
    return result

# print(generate_xiaohongshu("大模型", os.getenv("OPENAI_API_KEY")))
