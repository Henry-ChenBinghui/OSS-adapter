from .common_load_balancer import LoadBalancer, LlmInstanceEntry
from typing import List, Any

class BaseMultiComponentLLM:
    def __init__(self):
        self.llm_clients = self._init_clients("llm")
        self.analyser_clients = self._init_clients("analyser")
        self.safety_clients = self._init_clients("content_safety")
        self.llm_balancer = LoadBalancer.create("round-robin")
        self.analyser_balancer = LoadBalancer.create("round-robin")
        self.safety_balancer = LoadBalancer.create("round-robin")

    def _init_clients(self, component_type: str) -> List[LlmInstanceEntry]:
        """子类实现：返回该组件的 client 列表"""
        raise NotImplementedError

    async def answer_question(self, prompt: str, **kwargs) -> str:
        entry = self.llm_balancer.cycle(self.llm_clients)
        return await self._call_llm(entry, prompt, **kwargs)

    async def content_safety_check(self, text: str, **kwargs) -> bool:
        entry = self.safety_balancer.cycle(self.safety_clients)
        return await self._call_safety(entry, text, **kwargs)

    async def extract_document(self, file_path: str, **kwargs) -> str:
        entry = self.analyser_balancer.cycle(self.analyser_clients)
        return await self._call_analyser(entry, file_path, **kwargs)

    async def _call_llm(self, entry, prompt, **kwargs):
        raise NotImplementedError

    async def _call_safety(self, entry, text, **kwargs):
        raise NotImplementedError

    async def _call_analyser(self, entry, file_path, **kwargs):
        raise NotImplementedError 