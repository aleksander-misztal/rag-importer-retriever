import logging
from pathlib import Path
from collections import defaultdict
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from shared.interfaces.document_loader import RawDocument
from shared.interfaces.vectorstore import DocumentChunk

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Processes documents: chunking, cleaning, metadata enrichment"""

    def __init__(self, chunk_size: int = 250, chunk_overlap: int = 50, **kwargs):
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_start_index=True,
            length_function=len
        )
        logger.info(f"DocumentProcessor: chunk_size={chunk_size}, overlap={chunk_overlap}")

    def process(self, raw_documents: List[RawDocument]) -> List[DocumentChunk]:
        """Converts raw documents into chunks ready for embedding"""
        try:
            from langchain_core.documents import Document as LangChainDocument

            langchain_docs = [
                LangChainDocument(page_content=doc.content, metadata=doc.metadata or {})
                for doc in raw_documents
            ]

            chunks = self._splitter.split_documents(langchain_docs)
            logger.info(f"Split into {len(chunks)} chunks")

            page_chunk_counters = defaultdict(int)
            document_chunks = []

            for chunk in chunks:
                source = chunk.metadata.get("source", "unknown")
                page = chunk.metadata.get("page", 0)
                stem = Path(source).stem
                local_idx = page_chunk_counters[(source, page)]
                page_chunk_counters[(source, page)] += 1

                chunk_id = f"{stem}_p{page:03d}_c{local_idx:02d}"

                document_chunks.append(DocumentChunk(
                    content=chunk.page_content,
                    metadata={**chunk.metadata, "chunk_id": chunk_id, "chunk_size": len(chunk.page_content)}
                ))

            return document_chunks

        except Exception as e:
            logger.error(f"Processing error: {e}")
            raise

    def validate_document(self, raw_document: RawDocument) -> bool:
        if not raw_document.content or len(raw_document.content.strip()) < 10:
            return False
        return True
