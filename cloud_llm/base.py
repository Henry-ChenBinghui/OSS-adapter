from abc import ABC, abstractmethod
from typing import Any

class BaseCloudLLM(ABC):
    @abstractmethod
    async def answer_question(self, prompt: str, **kwargs) -> str:
        """LLM回答问题"""
        pass

    @abstractmethod
    async def content_safety_check(self, text: str, **kwargs) -> bool:
        """内容安全鉴定"""
        pass

    @abstractmethod
    async def extract_document(self, file_path: str, **kwargs) -> str:
        """文档提取"""
        pass 