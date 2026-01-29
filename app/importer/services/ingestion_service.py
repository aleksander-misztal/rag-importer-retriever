import logging
from typing import Any
from shared.interfaces.document_loader import DocumentLoaderProvider
from shared.interfaces.vectorstore import VectorStoreProvider
from importer.services.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class IngestionService:
    """Orchestrates document import: load -> process -> store"""

    def __init__(
        self,
        document_loader: DocumentLoaderProvider,
        document_processor: DocumentProcessor,
        vector_store: VectorStoreProvider
    ):
        self.document_loader = document_loader
        self.document_processor = document_processor
        self.vector_store = vector_store
        logger.info("IngestionService initialized")

    def ingest_file(self, file_path: str) -> dict[str, Any]:
        """Main import method - processes file from start to finish"""
        try:
            logger.info(f"=== Starting import: {file_path} ===")

            # Validate file
            if not self._validate_file(file_path):
                return {
                    "success": False,
                    "message": "Invalid file format",
                    "stats": {}
                }

            # Load document
            logger.info("Step 1/3: Loading document")
            raw_documents = self.document_loader.load(file_path)

            if not raw_documents:
                return {
                    "success": False,
                    "message": "Failed to load document",
                    "stats": {}
                }

            logger.info(f"Loaded {len(raw_documents)} pages/sections")

            # Process into chunks
            logger.info("Step 2/3: Processing document")
            chunks = self.document_processor.process(raw_documents)

            if not chunks:
                return {
                    "success": False,
                    "message": "Failed to process document",
                    "stats": {}
                }

            logger.info(f"Created {len(chunks)} chunks")

            # Save to vector store
            logger.info("Step 3/3: Saving to vector store")
            saved_count = self.vector_store.add_documents(chunks)

            logger.info(f"=== Import completed: {saved_count} documents ===")

            return {
                "success": True,
                "message": f"Successfully added {saved_count} chunks to knowledge base",
                "stats": {
                    "pages": len(raw_documents),
                    "chunks": saved_count,
                    "file_path": file_path
                }
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Import error: {error_msg}")

            # Handle specific errors
            if "401" in error_msg or "Incorrect API key" in error_msg:
                return {
                    "success": False,
                    "message": "OpenAI error (401): Invalid API key",
                    "stats": {}
                }

            if "connection" in error_msg.lower():
                return {
                    "success": False,
                    "message": "Database connection error",
                    "stats": {}
                }

            return {
                "success": False,
                "message": f"Error: {error_msg}",
                "stats": {}
            }

    def _validate_file(self, file_path: str) -> bool:
        """Validates file before import"""
        import os

        if not os.path.exists(file_path):
            logger.error(f"File does not exist: {file_path}")
            return False

        _, ext = os.path.splitext(file_path)
        if not self.document_loader.supports(ext):
            logger.error(f"Unsupported file format: {ext}")
            return False

        # Check file size (max 50MB)
        file_size = os.path.getsize(file_path)
        max_size = 50 * 1024 * 1024

        if file_size > max_size:
            logger.error(f"File too large: {file_size / 1024 / 1024:.2f}MB (max 50MB)")
            return False

        if file_size == 0:
            logger.error("File is empty")
            return False

        return True

    def get_stats(self) -> dict:
        """Returns vector store statistics"""
        try:
            return self.vector_store.get_collection_stats()
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {}

    def clear_database(self) -> dict[str, Any]:
        """Clears all documents from the database"""
        try:
            logger.info("=== Clearing database ===")
            success = self.vector_store.clear_collection()

            if success:
                return {
                    "success": True,
                    "message": "Database cleared successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to clear database"
                }
        except Exception as e:
            logger.error(f"Clear database error: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }

    def get_document_registry(self) -> dict:
        """Returns registry of uploaded documents"""
        try:
            return self.vector_store.get_document_registry()
        except Exception as e:
            logger.error(f"Registry error: {e}")
            return {}
