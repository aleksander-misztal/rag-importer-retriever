import gradio as gr
from dependency_container import DependencyContainer
from shared.common.logger import setup_logger

logger = setup_logger("importer")


def create_importer_ui(container: DependencyContainer) -> gr.Blocks:
    """Creates Gradio interface for Importer"""

    ingestion_service = container.ingestion_service()

    def handle_upload(file_obj) -> str:
        """Handles file upload"""
        if file_obj is None:
            return "❌ No file selected"

        try:
            file_path = file_obj.name
            logger.info(f"Starting import: {file_path}")

            result = ingestion_service.ingest_file(file_path)

            if result["success"]:
                stats = result["stats"]
                return (
                    f"✅ {result['message']}\n\n"
                    f"📄 Pages: {stats.get('pages', 0)}\n"
                    f"📦 Chunks: {stats.get('chunks', 0)}"
                )
            else:
                return f"❌ {result['message']}"

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return f"❌ Error: {str(e)}"

    def handle_stats() -> str:
        """Displays vector store statistics and document registry"""
        try:
            stats = ingestion_service.get_stats()
            registry = ingestion_service.get_document_registry()

            output = f"📊 Statistics:\n\n"
            output += f"Collection: {stats.get('collection_name', 'N/A')}\n"
            output += f"Connection: {stats.get('connection', 'N/A')}\n\n"

            if registry:
                output += "📁 Uploaded Documents:\n\n"
                for filename, info in registry.items():
                    output += f"• {filename}: {info['chunks']} chunks\n"
                total_chunks = sum(info['chunks'] for info in registry.values())
                output += f"\n📦 Total: {len(registry)} files, {total_chunks} chunks"
            else:
                output += "No documents uploaded yet"

            return output
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return f"❌ Error: {str(e)}"

    def handle_clear() -> str:
        """Handles database clearing"""
        try:
            result = ingestion_service.clear_database()
            if result["success"]:
                return f"✅ {result['message']}"
            else:
                return f"❌ {result['message']}"
        except Exception as e:
            logger.error(f"Clear error: {e}")
            return f"❌ Error: {str(e)}"

    # Build UI
    with gr.Blocks(title="RAG Importer", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 📚 RAG Importer")
        gr.Markdown("PDF document import system to vector database")

        with gr.Tab("📤 Upload"):
            gr.Markdown("### Import PDF Document")

            file_input = gr.File(
                label="Select PDF file",
                file_types=[".pdf"],
                type="filepath"
            )

            upload_btn = gr.Button("🚀 Import", variant="primary", size="lg")

            status_output = gr.Textbox(
                label="Status",
                lines=5,
                interactive=False
            )

            upload_btn.click(
                fn=handle_upload,
                inputs=[file_input],
                outputs=[status_output]
            )

        with gr.Tab("📊 Statistics"):
            gr.Markdown("### Database Statistics & Document Registry")

            stats_btn = gr.Button("🔄 Refresh", variant="secondary")

            stats_output = gr.Textbox(
                label="Statistics & Documents",
                lines=15,
                interactive=False
            )

            stats_btn.click(
                fn=handle_stats,
                outputs=[stats_output]
            )

        with gr.Tab("⚙️ Admin"):
            gr.Markdown("### Database Management")
            gr.Markdown("⚠️ **Warning:** Clear operation is irreversible!")

            clear_btn = gr.Button("🗑️ Clear Database", variant="stop")

            admin_output = gr.Textbox(
                label="Status",
                lines=3,
                interactive=False
            )

            clear_btn.click(
                fn=handle_clear,
                outputs=[admin_output]
            )

    return demo
