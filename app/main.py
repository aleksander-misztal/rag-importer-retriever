import gradio as gr
from fastapi import FastAPI
from shared.common.logger import setup_logger
from dependency_container import DependencyContainer
from importer.ui import create_importer_ui
from retriever.ui import create_retriever_ui

logger = setup_logger("app")

def create_app():
    """Main application with two Gradio endpoints"""

    logger.info("=== Initializing Unified RAG Application ===")

    # Initialize DI Container
    container = DependencyContainer()
    logger.info("✅ DI Container initialized")

    # Create FastAPI app
    app = FastAPI(title="RAG Application")

    # Create Gradio interfaces
    importer_ui = create_importer_ui(container)
    retriever_ui = create_retriever_ui(container)

    # Mount Gradio apps
    app = gr.mount_gradio_app(app, importer_ui, path="/importer")
    app = gr.mount_gradio_app(app, retriever_ui, path="/retriever")

    logger.info("✅ Gradio interfaces mounted:")
    logger.info("   - Importer: http://0.0.0.0:7860/importer")
    logger.info("   - Retriever: http://0.0.0.0:7860/retriever")

    return app

if __name__ == "__main__":
    import uvicorn

    app = create_app()
    logger.info("🚀 Starting server on http://0.0.0.0:7860")
    uvicorn.run(app, host="0.0.0.0", port=7860)
