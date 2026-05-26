from dependency_injector import containers, providers
from shared.common.config import CONFIG
from shared.providers.pymupdf_loader import PyMuPDFLoaderProvider
from shared.providers.openai_embeddings import OpenAIEmbeddingProvider
from shared.providers.pgvector_store import PGVectorStoreProvider
from shared.providers.openai_llm import OpenAILLMProvider
from shared.providers.local_prompts import LocalPromptProvider
from shared.providers.document_repository import VectorDocumentRepository
from importer.services.document_processor import DocumentProcessor
from importer.services.ingestion_service import IngestionService
from retriever.core.nodes.security import SecurityNode
from retriever.core.nodes.generator import GeneratorNode
from retriever.core.nodes.executor import ExecutorNode
from retriever.core.nodes.reranker import RerankNode
from retriever.core.nodes.flatten import FlattenNode
from retriever.core.nodes.synthesizer import SynthesizerNode


class DependencyContainer(containers.DeclarativeContainer):
    """Unified DI Container for both Importer and Retriever"""

    # Shared Infrastructure Layer

    document_loader = providers.Singleton(PyMuPDFLoaderProvider)

    embedding_provider = providers.Singleton(
        OpenAIEmbeddingProvider,
        api_key=CONFIG.OPENAI_API_KEY,
        model="text-embedding-3-small"
    )

    vector_store = providers.Singleton(
        PGVectorStoreProvider,
        connection_url=CONFIG.DATABASE_URL,
        collection_name=CONFIG.COLLECTION_NAME,
        embedding_provider=embedding_provider
    )

    llm_service = providers.Singleton(
        OpenAILLMProvider,
        api_key=CONFIG.OPENAI_API_KEY
    )

    prompt_service = providers.Singleton(LocalPromptProvider)

    document_repository = providers.Singleton(
        VectorDocumentRepository,
        vector_provider=vector_store
    )

    # Importer Services

    document_processor = providers.Singleton(
        DocumentProcessor,
        chunk_size=CONFIG.CHUNK_SIZE,
        chunk_overlap=CONFIG.CHUNK_OVERLAP,
        chunking_strategy=CONFIG.CHUNKING_STRATEGY,
        embedding_provider=embedding_provider,
    )

    ingestion_service = providers.Singleton(
        IngestionService,
        document_loader=document_loader,
        document_processor=document_processor,
        vector_store=vector_store
    )

    # Retriever Nodes

    security_node = providers.Factory(
        SecurityNode,
        llm=llm_service,
        prompt_provider=prompt_service,
        settings={"model": "gpt-4o-mini", "temperature": 0.0},
        prompt_name="rag_security_check"
    )

    generator_node = providers.Factory(
        GeneratorNode,
        llm=llm_service,
        prompt_provider=prompt_service,
        settings={"model": "gpt-4o-mini", "temperature": 0.7},
        prompt_name="rag_query_generator"
    )

    executor_node = providers.Factory(
        ExecutorNode,
        document_repository=document_repository,
        k=3
    )

    reranker_node = providers.Factory(
        RerankNode,
        model_name="cross-encoder/ms-marco-MiniLM-L-6-v2",
        top_k_per_query=2,
    )

    flatten_node = providers.Factory(FlattenNode)

    synthesizer_node = providers.Factory(
        SynthesizerNode,
        llm=llm_service,
        prompt_provider=prompt_service,
        settings={"model": "gpt-4o", "temperature": 0.3},
        prompt_name="rag_final_synthesizer"
    )
