from pydantic import BaseModel, Field
from typing import List

class Xiaohongshu(BaseModel):
    titles: List[str] = Field(description="小红书的5个标题", min_length=5, max_length=5)
    content: str = Field(description="小红书的正文内容")
    search_result: str = Field(description="百度的搜索结果")