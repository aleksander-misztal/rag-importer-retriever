import logging
import os
from typing import List
from langchain_postgres.vectorstores import PGVector
from langchain_core.documents import Document as LangChainDocument
from shared.interfaces.vectorstore import VectorProvider, DocumentChunk
from shared.interfaces.embeddings import EmbeddingProvider

logger = logging.getLogger(__name__)


class PGVectorStoreProvider(VectorProvider):
    """PostgreSQL + PGVector provider for import and retrieval"""

    def __init__(self, connection_url: str, collection_name: str, embedding_provider: EmbeddingProvider):
        self.connection_url = connection_url
        self.collection_name = collection_name
        self._embedding_provider = embedding_provider
        self._store = self._build_store()
        logger.info(f"PGVector initialized: collection={collection_name}")

    def _build_store(self) -> PGVector:
        return PGVector(
            connection=self.connection_url,
            embeddings=self._embedding_provider.get_embeddings(),
            collection_name=self.collection_name,
            use_jsonb=True
        )

    def search_with_metadata(self, query: str, k: int = 3) -> List[dict]:
        """Semantic search returning content + metadata for each result"""
        docs = self._store.similarity_search(query, k=k)
        return [{"content": doc.page_content, "metadata": doc.metadata} for doc in docs]

    def add_documents(self, documents: List[DocumentChunk]) -> int:
        langchain_docs = [
            LangChainDocument(page_content=doc.content, metadata=doc.metadata or {})
            for doc in documents
        ]
        self._store.add_documents(langchain_docs)
        logger.info(f"Added {len(langchain_docs)} documents to PGVector")
        return len(langchain_docs)

    def get_collection_stats(self) -> dict:
        host = self.connection_url.split("@")[1] if "@" in self.connection_url else "unknown"
        return {"collection_name": self.collection_name, "connection": host}

    def clear_collection(self) -> bool:
        try:
            self._store.delete_collection()
            self._store = self._build_store()
            logger.info(f"Cleared collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Clear collection error: {e}")
            return False

    def get_document_registry(self) -> dict:
        """Returns per-file chunk counts. Uses raw SQL — langchain_postgres has no public API for this."""
        try:
            from sqlalchemy import text
            query = text("""
                SELECT cmetadata->>'source' AS source, COUNT(*) AS chunks
                FROM langchain_pg_embedding
                WHERE collection_id = (
                    SELECT uuid FROM langchain_pg_collection WHERE name = :name
                )
                AND cmetadata->>'source' IS NOT NULL
                GROUP BY cmetadata->>'source'
            """)
            with self._store.session_maker() as session:
                rows = session.execute(query, {"name": self.collection_name}).fetchall()

            return {
                os.path.basename(row.source): {"full_path": row.source, "chunks": int(row.chunks)}
                for row in rows
                if row.source
            }
        except Exception as e:
            logger.error(f"Registry error: {e}")
            return {}
