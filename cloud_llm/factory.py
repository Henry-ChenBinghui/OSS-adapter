import os
from .base_multi_component import BaseMultiComponentLLM
from .types import CloudProvider
from .azure import AzureCloudLLM
from .aws import AWSCloudLLM
from .gcp import GCPCloudLLM

CLOUD_PROVIDER_ENV = "CLOUD_PROVIDER"

class CloudLLMFactory:
    @staticmethod
    def get_llm() -> 'BaseMultiComponentLLM':
        provider = os.environ.get(CLOUD_PROVIDER_ENV, CloudProvider.AZURE).lower()
        if provider == CloudProvider.AZURE:
            return AzureCloudLLM()
        elif provider == CloudProvider.AWS:
            return AWSCloudLLM()
        elif provider == CloudProvider.GCP:
            return GCPCloudLLM()
        else:
            raise ValueError(f"不支持的云服务提供商: {provider}") 