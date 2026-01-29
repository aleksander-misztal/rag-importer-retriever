import logging
from typing import List
from langchain_community.document_loaders import PyMuPDFLoader
from shared.interfaces.document_loader import DocumentLoaderProvider, RawDocument

logger = logging.getLogger(__name__)


class PyMuPDFLoaderProvider(DocumentLoaderProvider):
    """PDF document loader using PyMuPDF"""

    def load(self, file_path: str) -> List[RawDocument]:
        """Loads PDF and returns list of pages as RawDocuments"""
        try:
            logger.info(f"Loading PDF: {file_path}")

            loader = PyMuPDFLoader(file_path)
            langchain_docs = loader.load()

            # Convert to domain objects with source metadata
            raw_documents = []
            for idx, doc in enumerate(langchain_docs):
                raw_doc = RawDocument(
                    content=doc.page_content,
                    metadata={
                        "source": file_path,
                        "page": doc.metadata.get("page", idx),
                        **doc.metadata
                    },
                    page_number=doc.metadata.get("page", idx)
                )
                raw_documents.append(raw_doc)

            logger.info(f"✅ Loaded {len(raw_documents)} pages from PDF")
            return raw_documents

        except Exception as e:
            logger.error(f"PDF loading error {file_path}: {e}")
            raise

    def supports(self, file_extension: str) -> bool:
        """Returns True for .pdf files"""
        return file_extension.lower() in ['.pdf']
