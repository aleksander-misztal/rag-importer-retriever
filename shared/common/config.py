from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import re


class Settings(BaseSettings):
    """Unified configuration for RAG system (Importer + Retriever)"""

    OPENAI_API_KEY: str = Field(..., validation_alias="OPENAI_API_KEY")

    DB_USER: str = Field("postgres", validation_alias="DB_USER")
    DB_PASSWORD: str = Field("postgres", validation_alias="DB_PASSWORD")
    DB_NAME: str = Field("postgres", validation_alias="DB_NAME")
    DB_HOST: str = Field("db", validation_alias="DB_HOST")
    DB_PORT: str = Field("5432", validation_alias="DB_PORT")

    COLLECTION_NAME: str = Field("study_docs", validation_alias="COLLECTION_NAME")

    CHUNK_SIZE: int = Field(250, validation_alias="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(50, validation_alias="CHUNK_OVERLAP")

    @property
    def DATABASE_URL(self) -> str:
        user = self._clean(self.DB_USER)
        password = self._clean(self.DB_PASSWORD)
        host = self._clean(self.DB_HOST)
        port = self._clean(self.DB_PORT)
        name = self._clean(self.DB_NAME)
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"

    @staticmethod
    def _clean(text: str) -> str:
        return re.sub(r'[^\x21-\x7E]', '', text).strip()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


CONFIG = Settings()
