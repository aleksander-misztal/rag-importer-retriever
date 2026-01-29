from abc import ABC, abstractmethod


class PromptProvider(ABC):
    """
    Strategy pattern for prompt providers (Local, Langfuse, Database, etc.).
    Enables swapping prompt sources without changing business logic.
    """

    @abstractmethod
    def get_prompt(self, name: str) -> str:
        """Retrieves prompt template by unique name."""
        pass
