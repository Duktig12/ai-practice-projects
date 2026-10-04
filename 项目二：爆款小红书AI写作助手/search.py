import requests
def baike_search(query: str, api_key: str) -> str:
    if not api_key:
        return "错误：未提供 API Key。"
    # 请替换为你自己的 API Key
    url = "https://appbuilder.baidu.com/v2/baike/lemma/get_content"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    params = {
        "search_type": "lemmaTitle",  # 按词条名检索
        "search_key": query,
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        print("状态码:", response.status_code)
        print("原始响应:", response.text[:2000])
        response.raise_for_status()
        data = response.json()

        result = data.get("result")
        if result:
            result = data.get("result", {})
            # 优先提取纯文本摘要
            summary = result.get("abstract_plain") or result.get("summary") or ""
            return f"标题: {result.get('lemma_title', query)}\n摘要: {summary[:1000]}"
        else:
            return f"未找到与 '{query}' 相关的百科条目。"
    except Exception as e:
        return f"查询百科时出错: {e}"

def baidu_ai_search(query: str, api_key: str, model: str = "ernie-5.0") -> str:
    """
    使用百度AI搜索（智能搜索生成）API进行全网实时检索并返回AI总结。
    需要环境变量 BAIDU_API_KEY。
    """
    if not api_key:
        return "错误：未设置 BAIDU_API_KEY 环境变量。"

    url = "https://qianfan.baidubce.com/v2/ai_search/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "messages": [
            {"role": "user", "content": query}
        ],
        "stream": False,
        "model": model,
        "search_source": "baidu_search_v2",  # 使用v2版本，数据更丰富
        "enable_corner_markers": True,        # 显示来源角标
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        choices = data.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "")
        return f"未找到与 '{query}' 相关的信息。原始返回: {data}"
    except requests.exceptions.Timeout:
        return "AI搜索超时，请稍后重试。"
    except Exception as e:
        return f"AI搜索出错: {e}"

# if __name__ == "__main__":
#     print("=" * 50)
#     print("测试百度百科搜索")
#     print("=" * 50)
#     result1 = baike_search("群星闪耀时")
#     print(result1)
#
#     print()
#     print("=" * 50)
#     print("测试百度AI搜索")
#     print("=" * 50)
#     result2 = baidu_ai_search("群星闪耀时")
#     print(result2)