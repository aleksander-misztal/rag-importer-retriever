import logging
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from shared.interfaces.document_loader import RawDocument
from shared.interfaces.vectorstore import DocumentChunk

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Processes documents: chunking, cleaning, metadata enrichment"""

    def __init__(self, chunk_size: int = 250, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_start_index=True,
            length_function=len
        )

        logger.info(f"DocumentProcessor init: chunk_size={chunk_size}, overlap={chunk_overlap}")

    def process(self, raw_documents: List[RawDocument]) -> List[DocumentChunk]:
        """Converts raw documents into chunks ready for embedding"""
        try:
            logger.info(f"Processing {len(raw_documents)} raw documents")

            # Convert RawDocument -> LangChain Document
            from langchain_core.documents import Document as LangChainDocument

            langchain_docs = []
            for raw_doc in raw_documents:
                doc = LangChainDocument(
                    page_content=raw_doc.content,
                    metadata=raw_doc.metadata or {}
                )
                langchain_docs.append(doc)

            # Chunking
            chunks = self._splitter.split_documents(langchain_docs)
            logger.info(f"Split into {len(chunks)} chunks")

            # Convert LangChain Document -> DocumentChunk
            document_chunks = []
            for idx, chunk in enumerate(chunks):
                metadata = {
                    **chunk.metadata,
                    "chunk_id": idx,
                    "chunk_size": len(chunk.page_content)
                }

                doc_chunk = DocumentChunk(
                    content=chunk.page_content,
                    metadata=metadata
                )
                document_chunks.append(doc_chunk)

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
