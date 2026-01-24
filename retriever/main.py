import logging
import gradio as gr
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

from graph import create_graph
from models import get_models
from langfuse.langchain import CallbackHandler

app = create_graph()
available_models = get_models()

try:
    langfuse_handler = CallbackHandler()
    logger.info("Langfuse handler zainicjalizowany")
except Exception as e:
    langfuse_handler = None
    logger.warning(f"Langfuse niedostępny: {e}")


def chat_interface(question: str) -> tuple[str, str]:
    if not available_models:
        return "Błąd: Modele nie są zainicjalizowane.", ""

    inputs = {"question": question, "models": available_models}
    run_config = {"callbacks": [langfuse_handler]} if langfuse_handler else {}

    try:
        result = app.invoke(inputs, config=run_config)
        answer = result.get("answer", "Brak odpowiedzi.")
        sources = result.get("context", [])
        sources_text = "\n\n---\n\n".join(sources) if sources else "Brak pasujących fragmentów."
        return answer, sources_text
    except Exception as e:
        logger.error(f"Błąd przetwarzania zapytania: {e}")
        if "401" in str(e):
            return "Błąd OpenAI: Nieprawidłowy klucz API.", ""
        return f"Wystąpił błąd: {str(e)}", ""


with gr.Blocks(title="RAG Retriever", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# RAG Retriever")

    with gr.Row():
        with gr.Column(scale=2):
            msg = gr.Textbox(label="Zadaj pytanie", placeholder="Wpisz tekst...", lines=2)
            submit_btn = gr.Button("Zapytaj", variant="primary")
            output_answer = gr.Textbox(label="Odpowiedź", lines=10, interactive=False)

        with gr.Column(scale=1):
            output_sources = gr.Textbox(label="Źródła", lines=15, interactive=False)

    submit_btn.click(chat_interface, inputs=[msg], outputs=[output_answer, output_sources])
    msg.submit(chat_interface, inputs=[msg], outputs=[output_answer, output_sources])

if __name__ == "__main__":
    logger.info("Retriever startuje na http://localhost:7861")
    demo.launch(server_name="0.0.0.0", server_port=7861)
