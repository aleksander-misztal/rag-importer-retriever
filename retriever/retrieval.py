from langchain_postgres.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from config import DATABASE_URL, COLLECTION_NAME, OPENAI_API_KEY

_embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)


def get_vectorstore() -> PGVector:
    return PGVector(
        connection=DATABASE_URL,
        embeddings=_embeddings,
        collection_name=COLLECTION_NAME,
        use_jsonb=True
    )


def search_documents_sync(vectorstore: PGVector, query: str, k: int = 3) -> list[str]:
    docs = vectorstore.similarity_search(query, k=k)
    return [doc.page_content for doc in docs]
