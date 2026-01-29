from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """
    Strategy pattern for LLM providers (OpenAI, Anthropic, Azure, etc.).
    Enables swapping providers without changing business logic.
    """

    @abstractmethod
    def invoke(self, prompt: str, **kwargs: Any) -> str:
        """Invokes LLM with prompt and returns response text."""
        pass
