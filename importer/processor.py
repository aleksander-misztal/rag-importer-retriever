import logging
from typing import Any
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector
from config import DATABASE_URL, COLLECTION_NAME, CHUNK_SIZE, CHUNK_OVERLAP, OPENAI_API_KEY

logger = logging.getLogger(__name__)

_embeddings: OpenAIEmbeddings | None = None


def get_embeddings() -> OpenAIEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    return _embeddings


def get_vectorstore() -> PGVector:
    return PGVector(
        connection=DATABASE_URL,
        embeddings=get_embeddings(),
        collection_name=COLLECTION_NAME,
        use_jsonb=True,
    )


def ingest_pdf(file_obj: Any | None) -> str:
    if file_obj is None:
        return "Nie wybrano pliku."

    if not OPENAI_API_KEY:
        logger.error("Brak klucza OPENAI_API_KEY")
        return "Błąd: Brak klucza OPENAI_API_KEY w konfiguracji."

    try:
        filename: str = file_obj.name
        logger.info(f"Rozpoczynam przetwarzanie: {filename}")

        loader = PyPDFLoader(filename)
        docs = loader.load()
        logger.info(f"Załadowano {len(docs)} stron")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            add_start_index=True
        )
        chunks = text_splitter.split_documents(docs)
        logger.info(f"Podzielono na {len(chunks)} fragmentów")

        vectorstore = get_vectorstore()
        vectorstore.add_documents(chunks)
        logger.info("Dokumenty zapisane w bazie")

        return f"Dodano {len(chunks)} fragmentów do bazy wiedzy."

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Błąd przetwarzania: {error_msg}")

        if "utf-8" in error_msg.lower():
            return "Błąd kodowania znaków. Sprawdź czy plik jest w UTF-8."

        if "401" in error_msg:
            return "Błąd OpenAI (401): Nieprawidłowy klucz API."

        return f"Wystąpił błąd: {error_msg}"
