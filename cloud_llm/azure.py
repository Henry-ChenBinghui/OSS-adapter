from .base_multi_component import BaseMultiComponentLLM
from .common_load_balancer import LlmInstanceEntry, LlmStatus
import llm._llm_client_factory as azure_factory
import llm._llm_client_models as azure_models
import os

class AzureCloudLLM(BaseMultiComponentLLM):
    def _init_clients(self, component_type):
        # 这里用环境变量和LlmComponentType创建client池
        # 仅示例，实际可根据你的配置灵活调整
        from azure.identity.aio import DefaultAzureCredential
        credential = DefaultAzureCredential()
        # 组件类型映射
        type_map = {
            "llm": azure_models.LlmComponentType.LLM,
            "analyser": azure_models.LlmComponentType.ANALYSER,
            "content_safety": azure_models.LlmComponentType.CONTENT_SAFETY,
        }
        # 假设用ALLOWED_MODELS等环境变量
        options = []
        for k, v in os.environ.items():
            if k.endswith("_API_BASE") and component_type in k.lower():
                options.append(azure_models.LlmInstance(endpoint=v, component=type_map[component_type]))
        # 用工厂创建client
        clients = []
        for _, client in azure_factory.LlmClientFactory.create(options, credential):
            clients.append(LlmInstanceEntry(client=client, instance=None, status=LlmStatus.ACTIVE))
        return clients if clients else []

    async def _call_llm(self, entry, prompt, **kwargs):
        model = kwargs.get("model", None)
        result = await entry.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return result["choices"][0]["message"]["content"]

    async def _call_safety(self, entry, text, **kwargs):
        result = await entry.client.analyze_text(text)
        return getattr(result, "is_safe", True)

    async def _call_analyser(self, entry, file_path, **kwargs):
        with open(file_path, "rb") as f:
            import io
            data = io.BytesIO(f.read())
        poller = await entry.client.begin_analyze_document(
            model_id="prebuilt-layout",
            body=data,
            output_content_format="text"
        )
        result = await poller.result()
        return getattr(result, "content", "") 