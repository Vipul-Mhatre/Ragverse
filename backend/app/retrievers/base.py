from abc import ABC, abstractmethod


class Retriever(ABC):
    @abstractmethod
    async def retrieve(self, query: str, docs: list[dict], top_k: int = 5) -> list[dict]:
        raise NotImplementedError
