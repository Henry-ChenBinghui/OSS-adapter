from .base_multi_component import BaseMultiComponentLLM
from .common_load_balancer import LlmInstanceEntry, LlmStatus

class GCPCloudLLM(BaseMultiComponentLLM):
    def _init_clients(self, component_type):
        # TODO: 用GCP SDK创建client池
        return []

    async def _call_llm(self, entry, prompt, **kwargs):
        raise NotImplementedError("GCP LLM回答功能待实现")

    async def _call_safety(self, entry, text, **kwargs):
        raise NotImplementedError("GCP 内容安全鉴定功能待实现")

    async def _call_analyser(self, entry, file_path, **kwargs):
        raise NotImplementedError("GCP 文档提取功能待实现") 