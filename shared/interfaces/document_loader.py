from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass


@dataclass
class RawDocument:
    """Raw document loaded from file, abstracted from loader implementation."""
    content: str
    metadata: dict | None = None
    page_number: int | None = None


class DocumentLoaderProvider(ABC):
    """
    Strategy pattern for document loaders (PDF, DOCX, TXT, etc.).
    Enables swapping loaders without changing business logic.
    """

    @abstractmethod
    def load(self, file_path: str) -> List[RawDocument]:
        """Loads document and returns pages/sections as raw documents."""
        pass

    @abstractmethod
    def supports(self, file_extension: str) -> bool:
        """Checks if loader supports the given file extension."""
        pass
