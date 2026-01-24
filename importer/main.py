import logging
import gradio as gr
from database import init_vector_db, clear_all_data
from processor import ingest_pdf

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

init_vector_db()

with gr.Blocks(title="RAG Importer") as demo:
    gr.Markdown("# RAG Importer")

    with gr.Tab("Upload"):
        f_input = gr.File(label="PDF", file_types=[".pdf"])
        btn = gr.Button("Importuj", variant="primary")
        out = gr.Textbox(label="Status")
        btn.click(ingest_pdf, inputs=[f_input], outputs=[out])

    with gr.Tab("Admin"):
        clr_btn = gr.Button("Wyczyść Bazę", variant="stop")
        clr_btn.click(clear_all_data, outputs=[out])

if __name__ == "__main__":
    logger.info("Importer startuje na http://localhost:7860")
    demo.launch(server_name="0.0.0.0", server_port=7860, theme=gr.themes.Soft())
