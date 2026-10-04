import streamlit as st
from utils import generate_xiaohongshu


st.header("爆款小红书AI写作助手 ✏️")
#st.sidebar创建侧边栏
with st.sidebar:
    openai_api_key = st.text_input("请输入阿里云百炼 API密钥：", type="password")
    st.markdown("[获取阿里云百炼 API密钥](https://bailian.console.aliyun.com/cn-beijing/model/settings/api-key)")
    search_api_key = st.text_input("请输入百度智能云 API密钥：", type="password")
    st.markdown("[获取百度智能云 API密钥](https://console.bce.baidu.com/ai-search/qianfan/ais/console/apiKey)")
theme = st.text_input("主题")
submit = st.button("开始写作")

if submit and not openai_api_key:
    st.info("请输入你的阿里云百炼 API密钥")
    st.stop()
if submit and not theme:
    st.info("请输入生成内容的主题")
    st.stop()
if submit and not search_api_key:
    st.info("没有提供百度搜索API，可能导致AI结果失真")
if submit:
    with st.spinner("AI正在努力创作中，请稍等..."):
        result = generate_xiaohongshu(theme, openai_api_key, search_api_key)
    st.divider()
    left_column, right_column = st.columns(2)
    with left_column:
        st.markdown("##### 小红书标题1")
        st.write(result.titles[0])
        st.markdown("##### 小红书标题2")
        st.write(result.titles[1])
        st.markdown("##### 小红书标题3")
        st.write(result.titles[2])
        st.markdown("##### 小红书标题4")
        st.write(result.titles[3])
        st.markdown("##### 小红书标题5")
        st.write(result.titles[4])
    with right_column:
        st.markdown("##### 小红书正文")
        st.write(result.content)
    with st.expander("百度搜索结果 👀"):
        st.info(result.search_result)
