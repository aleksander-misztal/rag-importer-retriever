from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import re


class Settings(BaseSettings):
    """Unified configuration for RAG system (Importer + Retriever)"""

    # OpenAI
    OPENAI_API_KEY: str = Field(..., validation_alias="OPENAI_API_KEY")

    # Langfuse (optional monitoring)
    LANGFUSE_PUBLIC_KEY: str = Field("", validation_alias="LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY: str = Field("", validation_alias="LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST: str = Field("https://cloud.langfuse.com", validation_alias="LANGFUSE_HOST")

    # Database (PostgreSQL + PGVector)
    DB_USER: str = Field("postgres", validation_alias="DB_USER")
    DB_PASSWORD: str = Field("postgres", validation_alias="DB_PASSWORD")
    DB_NAME: str = Field("postgres", validation_alias="DB_NAME")
    DB_HOST: str = Field("db", validation_alias="DB_HOST")
    DB_PORT: str = Field("5432", validation_alias="DB_PORT")

    # Collection config
    COLLECTION_NAME: str = Field("study_docs", validation_alias="COLLECTION_NAME")

    # Chunking parameters (for Importer)
    CHUNK_SIZE: int = Field(250, validation_alias="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(50, validation_alias="CHUNK_OVERLAP")
    CHUNKING_STRATEGY: str = Field("recursive", validation_alias="CHUNKING_STRATEGY")  # "recursive" | "semantic"

    # Retrieval
    RERANKING_ENABLED: bool = Field(True, validation_alias="RERANKING_ENABLED")

    # Evaluation
    JUDGE_MODEL: str = Field("gpt-4o", validation_alias="JUDGE_MODEL")

    @property
    def DATABASE_URL(self) -> str:
        """Generates full database connection URL"""
        user = self._clean(self.DB_USER)
        password = self._clean(self.DB_PASSWORD)
        host = self._clean(self.DB_HOST)
        port = self._clean(self.DB_PORT)
        name = self._clean(self.DB_NAME)

        return f"postgresql://{user}:{password}@{host}:{port}/{name}"

    @staticmethod
    def _clean(text: str) -> str:
        """Removes invisible characters from environment variables"""
        if not text:
            return ""
        cleaned = re.sub(r'[^\x21-\x7E]', '', text)
        return cleaned.strip()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Singleton instance
CONFIG = Settings()
