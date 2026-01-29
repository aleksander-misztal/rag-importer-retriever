import gradio as gr
from langfuse.langchain import CallbackHandler
from shared.common.logger import setup_logger
from dependency_container import DependencyContainer
from retriever.core.graph import create_graph

logger = setup_logger("retriever")


def create_retriever_ui(container: DependencyContainer) -> gr.Blocks:
    """Creates Gradio interface for Retriever"""

    # Build graph from DI container
    try:
        rag_app = create_graph(
            security=container.security_node(),
            generator=container.generator_node(),
            executor=container.executor_node(),
            synthesizer=container.synthesizer_node()
        )
        logger.info("LangGraph compiled successfully")
    except Exception as e:
        logger.error(f"Graph build error: {e}")
        raise

    # Initialize Langfuse tracing (optional)
    try:
        langfuse_handler = CallbackHandler()
        logger.info("Langfuse tracing active")
    except Exception as e:
        langfuse_handler = None
        logger.warning(f"Langfuse init error: {e}. Running without tracing.")

    def chat_fn(question: str):
        """Handles chat interaction"""
        if not question.strip():
            return "Please enter a question.", ""

        inputs = {"question": question}
        config = {"callbacks": [langfuse_handler]} if langfuse_handler else {}

        try:
            logger.info(f"Processing question: {question[:50]}...")
            result = rag_app.invoke(inputs, config=config)

            answer = result.get("answer", "Error: Failed to generate answer.")
            context_list = result.get("context", [])
            context_metadata = result.get("context_metadata", [])

            if context_list:
                sources_parts = []
                for i, text in enumerate(context_list):
                    # Get metadata for this chunk
                    metadata = context_metadata[i] if i < len(context_metadata) else {}
                    source_file = metadata.get("source", "Unknown")
                    page = metadata.get("page", "?")

                    # Extract filename from path
                    import os
                    filename = os.path.basename(source_file) if source_file != "Unknown" else "Unknown"

                    sources_parts.append(
                        f"Fragment {i+1} (📄 {filename}, page {page}):\n{text}"
                    )
                sources = "\n\n---\n\n".join(sources_parts)
            else:
                sources = "No matching documents in knowledge base."

            return answer, sources

        except Exception as e:
            logger.error(f"Graph execution error: {e}")
            return f"System error: {str(e)}", "No data."

    # Build UI
    with gr.Blocks(title="Pro RAG Retriever", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🤖 Professional RAG Assistant")
        gr.Markdown("Status: **Connected to PGVector & Langfuse**")

        with gr.Row():
            with gr.Column(scale=2):
                msg = gr.Textbox(
                    label="Your question",
                    placeholder="Enter your query to the knowledge base...",
                    lines=3
                )
                with gr.Row():
                    clear_btn = gr.Button("Clear")
                    submit_btn = gr.Button("Send", variant="primary")

                output_answer = gr.Textbox(
                    label="AI Answer",
                    lines=12,
                    interactive=False
                )

            with gr.Column(scale=1):
                output_sources = gr.Textbox(
                    label="Context (Sources)",
                    lines=20,
                    interactive=False
                )

        # Bind actions
        submit_btn.click(chat_fn, inputs=[msg], outputs=[output_answer, output_sources])
        msg.submit(chat_fn, inputs=[msg], outputs=[output_answer, output_sources])
        clear_btn.click(lambda: (None, None, None), outputs=[msg, output_answer, output_sources])

    return demo
