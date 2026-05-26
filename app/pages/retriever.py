import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dependency_container import DependencyContainer
from retriever.core.graph import create_graph
from shared.common.config import CONFIG
from shared.common.logger import setup_logger

logger = setup_logger("retriever_ui")


@st.cache_resource
def get_rag_app():
    container = DependencyContainer()

    reranker = container.reranker_node() if CONFIG.RERANKING_ENABLED else None
    flatten = None if CONFIG.RERANKING_ENABLED else container.flatten_node()

    rag_app = create_graph(
        security=container.security_node(),
        generator=container.generator_node(),
        executor=container.executor_node(),
        synthesizer=container.synthesizer_node(),
        reranker=reranker,
        flatten=flatten,
    )

    mode = "reranker" if CONFIG.RERANKING_ENABLED else "flatten"
    logger.info(f"RAG graph compiled (mode={mode})")
    return rag_app


def render():
    st.title("RAG Retriever")
    mode_label = "Reranker ON" if CONFIG.RERANKING_ENABLED else "Reranker OFF"
    st.caption(f"Ask questions about your documents  |  {mode_label}")

    rag_app = get_rag_app()

    question = st.text_area("Your question", placeholder="Ask anything about your knowledge base...", height=100)

    if st.button("Ask", type="primary", disabled=not question.strip()):
        with st.spinner("Thinking..."):
            try:
                result = rag_app.invoke({"question": question})

                answer = result.get("answer", "No answer generated.")
                context_list = result.get("context", [])
                context_metadata = result.get("context_metadata", [])

                st.subheader("Answer")
                st.write(answer)

                if context_list:
                    with st.expander(f"Sources ({len(context_list)} chunks)"):
                        for i, (text, meta) in enumerate(zip(context_list, context_metadata)):
                            chunk_id = meta.get("chunk_id", f"chunk_{i}")
                            page = meta.get("page", "?")
                            source = os.path.basename(meta.get("source", "Unknown"))
                            st.markdown(f"**{chunk_id}** — {source}, page {page}")
                            st.code(text, language=None)
                            if i < len(context_list) - 1:
                                st.divider()
                else:
                    st.info("No matching documents found in knowledge base.")

            except Exception as e:
                logger.error(f"RAG error: {e}")
                st.error(f"Error: {str(e)}")


render()
