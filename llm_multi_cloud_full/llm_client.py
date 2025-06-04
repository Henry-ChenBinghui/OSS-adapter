from llm.router import MultiCloudRouter
from typing import List, Dict

class LlmClient:
    _router = MultiCloudRouter()

    @classmethod
    async def create_embedding(cls, text: str, model: str) -> List[float]:
        return await cls._router.route("create_embedding", text=text, model=model)

    @classmethod
    async def create_completion(cls, model: str, **kwargs) -> Dict:
        return await cls._router.route("create_completion", model=model, **kwargs)
