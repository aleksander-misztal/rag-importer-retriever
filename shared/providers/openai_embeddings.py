import logging
from typing import List
from langchain_openai import OpenAIEmbeddings
from shared.interfaces.embeddings import EmbeddingProvider

logger = logging.getLogger(__name__)


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider implementation."""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model
        self._embeddings = OpenAIEmbeddings(
            openai_api_key=api_key,
            model=model
        )
        logger.info(f"✅ OpenAI embeddings initialized: model={model}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Batch embed multiple texts."""
        try:
            logger.debug(f"Embedding {len(texts)} documents")
            vectors = self._embeddings.embed_documents(texts)
            return vectors
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise

    def embed_query(self, text: str) -> List[float]:
        """Embeds single query text."""
        try:
            vector = self._embeddings.embed_query(text)
            return vector
        except Exception as e:
            logger.error(f"Query embedding error: {e}")
            raise

    def get_dimension(self) -> int:
        """Returns vector dimension for the model."""
        if "text-embedding-3-small" in self.model:
            return 1536
        elif "text-embedding-3-large" in self.model:
            return 3072
        elif "text-embedding-ada-002" in self.model:
            return 1536
        else:
            logger.warning(f"Unknown model {self.model}, defaulting to 1536 dimensions")
            return 1536
