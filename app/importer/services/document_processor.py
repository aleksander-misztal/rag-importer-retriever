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

    def __init__(
        self,
        chunk_size: int = 250,
        chunk_overlap: int = 50,
        chunking_strategy: str = "recursive",
        embedding_provider=None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunking_strategy = chunking_strategy

        if chunking_strategy == "semantic":
            if embedding_provider is None:
                raise ValueError("embedding_provider is required for semantic chunking strategy")
            from langchain_experimental.text_splitter import SemanticChunker
            embeddings = embedding_provider.get_embeddings()
            self._splitter = SemanticChunker(
                embeddings,
                breakpoint_threshold_type="percentile",
                breakpoint_threshold_amount=95,
            )
            logger.info("DocumentProcessor init: strategy=semantic")
        else:
            self._splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                add_start_index=True,
                length_function=len
            )
            logger.info(f"DocumentProcessor init: strategy=recursive, chunk_size={chunk_size}, overlap={chunk_overlap}")

    def process(self, raw_documents: List[RawDocument]) -> List[DocumentChunk]:
        """Converts raw documents into chunks ready for embedding"""
        try:
            logger.info(f"Processing {len(raw_documents)} raw documents")

            from langchain_core.documents import Document as LangChainDocument

            langchain_docs = []
            for raw_doc in raw_documents:
                doc = LangChainDocument(
                    page_content=raw_doc.content,
                    metadata=raw_doc.metadata or {}
                )
                langchain_docs.append(doc)

            chunks = self._splitter.split_documents(langchain_docs)
            logger.info(f"Split into {len(chunks)} chunks")

            # Track chunk index per (source, page) for stable human-readable IDs
            page_chunk_counters = defaultdict(int)
            document_chunks = []

            for chunk in chunks:
                source = chunk.metadata.get("source", "unknown")
                page = chunk.metadata.get("page", 0)
                stem = Path(source).stem
                local_idx = page_chunk_counters[(source, page)]
                page_chunk_counters[(source, page)] += 1

                chunk_id = f"{stem}_p{page:03d}_c{local_idx:02d}"

                metadata = {
                    **chunk.metadata,
                    "chunk_id": chunk_id,
                    "chunk_size": len(chunk.page_content),
                }

                document_chunks.append(DocumentChunk(
                    content=chunk.page_content,
                    metadata=metadata
                ))

            logger.info(f"Created {len(document_chunks)} chunks")
            return document_chunks

        except Exception as e:
            logger.error(f"Processing error: {e}")
            raise

    def validate_document(self, raw_document: RawDocument) -> bool:
        """Validates document before processing"""
        if not raw_document.content:
            logger.warning("Empty document content")
            return False

        if len(raw_document.content.strip()) < 10:
            logger.warning("Content too short")
            return False

        return True
