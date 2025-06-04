from openai.lib.azure import AsyncAzureOpenAI
from typing import List, Dict
from llm.base_provider import BaseLlmProvider

class AzureLlmProvider(BaseLlmProvider):
    def __init__(self, client: AsyncAzureOpenAI):
        self.client = client

    async def create_embedding(self, text: str, model: str) -> List[float]:
        result = await self.client.embeddings.create(model=model, input=[text])
        return result.data[0].embedding

    async def create_completion(self, model: str, **kwargs) -> Dict:
        return await self.client.chat.completions.create(model=model, **kwargs)
