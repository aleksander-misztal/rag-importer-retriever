import logging
from typing import List, Union
from langchain_postgres.vectorstores import PGVector
from langchain_core.documents import Document as LangChainDocument
from shared.interfaces.vectorstore import VectorProvider, DocumentChunk
from shared.interfaces.embeddings import EmbeddingProvider

logger = logging.getLogger(__name__)


class PGVectorStoreProvider(VectorProvider):
    """Unified PostgreSQL + PGVector provider for both import and retrieval"""

    def __init__(
        self,
        connection_url: str,
        collection_name: str,
        embedding_provider: EmbeddingProvider
    ):
        self.connection_url = connection_url
        self.collection_name = collection_name
        self.embedding_provider = embedding_provider

        self._store = PGVector(
            connection=connection_url,
            embeddings=embedding_provider._embeddings,
            collection_name=collection_name,
            use_jsonb=True
        )

        logger.info(f"✅ PGVector initialized: collection={collection_name}")

    def search(self, query: str, k: int = 3) -> List[str]:
        """Semantic document search"""
        try:
            docs = self._store.similarity_search(query, k=k)
            return [doc.page_content for doc in docs]
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def search_with_metadata(self, query: str, k: int = 3) -> List[dict]:
        """Semantic document search with metadata"""
        try:
            docs = self._store.similarity_search(query, k=k)
            results = []
            for doc in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
            return results
        except Exception as e:
            logger.error(f"Search with metadata error: {e}")
            return []

    def add_documents(self, documents: Union[List[DocumentChunk], List[LangChainDocument]]) -> int:
        """Adds documents to vector store"""
        try:
            langchain_docs = []
            for doc in documents:
                if isinstance(doc, DocumentChunk):
                    langchain_doc = LangChainDocument(
                        page_content=doc.content,
                        metadata=doc.metadata or {}
                    )
                    langchain_docs.append(langchain_doc)
                else:
                    langchain_docs.append(doc)

            logger.info(f"Adding {len(langchain_docs)} documents to PGVector")
            self._store.add_documents(langchain_docs)
            logger.info(f"✅ Added {len(langchain_docs)} documents")
            return len(langchain_docs)
        except Exception as e:
            logger.error(f"Add documents error: {e}")
            raise

    def get_collection_stats(self) -> dict:
        """Returns collection statistics"""
        return {
            "collection_name": self.collection_name,
            "connection": self.connection_url.split("@")[1] if "@" in self.connection_url else "unknown"
        }

    def clear_collection(self) -> bool:
        """Clears all documents from the collection"""
        try:
            self._store.delete_collection()
            logger.info(f"✅ Cleared collection: {self.collection_name}")

            # Reinitialize the store
            self._store = PGVector(
                connection=self.connection_url,
                embeddings=self.embedding_provider._embeddings,
                collection_name=self.collection_name,
                use_jsonb=True
            )
            return True
        except Exception as e:
            logger.error(f"Clear collection error: {e}")
            return False

    def get_document_registry(self) -> dict:
        """Returns registry of uploaded documents with chunk counts"""
        try:
            from sqlalchemy import text
            import os

            # Query database directly using raw SQL
            query = text("""
                SELECT
                    cmetadata->>'source' as source,
                    COUNT(*) as chunks
                FROM langchain_pg_embedding
                WHERE cmetadata->>'source' IS NOT NULL
                GROUP BY cmetadata->>'source'
            """)

            with self._store.session_maker() as session:
                results = session.execute(query).fetchall()

            registry = {}
            for row in results:
                if row.source:
                    filename = os.path.basename(row.source)
                    registry[filename] = {
                        "full_path": row.source,
                        "chunks": int(row.chunks)
                    }

            logger.info(f"Registry: found {len(registry)} files")
            return registry
        except Exception as e:
            logger.error(f"Registry error: {e}")
            return {}
