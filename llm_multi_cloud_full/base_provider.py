from abc import ABC, abstractmethod
from typing import List, Dict

class BaseLlmProvider(ABC):
    @abstractmethod
    async def create_embedding(self, text: str, model: str) -> List[float]:
        pass

    @abstractmethod
    async def create_completion(self, model: str, **kwargs) -> Dict:
        pass
