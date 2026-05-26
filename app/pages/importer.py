import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dependency_container import DependencyContainer
from shared.common.logger import setup_logger

logger = setup_logger("importer_ui")


@st.cache_resource
def get_container():
    return DependencyContainer()


def render():
    st.title("RAG Importer")
    st.caption("Import PDF documents into the vector knowledge base")

    container = get_container()
    ingestion_service = container.ingestion_service()

    tab_upload, tab_chunks, tab_stats, tab_admin = st.tabs([
        "Upload", "Chunk Viewer", "Statistics", "Admin"
    ])

    with tab_upload:
        st.subheader("Import PDF Document")
        uploaded_file = st.file_uploader("Select PDF file", type=["pdf"])

        if st.button("Import", type="primary", disabled=uploaded_file is None):
            with st.spinner("Processing..."):
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                result = ingestion_service.ingest_file(tmp_path)
                os.unlink(tmp_path)

                if result["success"]:
                    stats = result["stats"]
                    st.success(result["message"])
                    col1, col2 = st.columns(2)
                    col1.metric("Pages", stats.get("pages", 0))
                    col2.metric("Chunks", stats.get("chunks", 0))

                    if result.get("chunk_preview"):
                        st.session_state["last_chunks"] = result["chunk_preview"]
                        st.info("Go to **Chunk Viewer** tab to see chunk IDs for building your eval dataset.")
                else:
                    st.error(result["message"])

    with tab_chunks:
        st.subheader("Chunk Viewer")
        st.caption("Use chunk IDs to build your evaluation dataset (eval/dataset.json)")

        chunks = st.session_state.get("last_chunks", [])

        if not chunks:
            st.info("Upload a PDF first to see its chunks here.")
        else:
            st.write(f"**{len(chunks)} chunks** from last import:")

            search = st.text_input("Filter by content or chunk_id", placeholder="Search...")

            df = pd.DataFrame(chunks)
            df["content_preview"] = df["content"].str[:120] + "..."

            if search:
                mask = (
                    df["chunk_id"].str.contains(search, case=False, na=False) |
                    df["content"].str.contains(search, case=False, na=False)
                )
                df = df[mask]

            st.dataframe(
                df[["chunk_id", "page", "content_preview"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "chunk_id": st.column_config.TextColumn("Chunk ID", width="medium"),
                    "page": st.column_config.NumberColumn("Page", width="small"),
                    "content_preview": st.column_config.TextColumn("Content Preview", width="large"),
                }
            )

            with st.expander("Full content of selected chunk"):
                selected_id = st.selectbox("Select chunk_id", df["chunk_id"].tolist())
                if selected_id:
                    row = next((c for c in chunks if c["chunk_id"] == selected_id), None)
                    if row:
                        st.code(row["content"], language=None)

    with tab_stats:
        st.subheader("Database Statistics")

        if st.button("Refresh", type="secondary"):
            stats = ingestion_service.get_stats()
            registry = ingestion_service.get_document_registry()

            col1, col2 = st.columns(2)
            col1.write(f"**Collection:** {stats.get('collection_name', 'N/A')}")
            col2.write(f"**Connection:** {stats.get('connection', 'N/A')}")

            if registry:
                st.write("**Uploaded Documents:**")
                reg_data = [
                    {"filename": fname, "chunks": info["chunks"]}
                    for fname, info in registry.items()
                ]
                st.dataframe(pd.DataFrame(reg_data), use_container_width=True, hide_index=True)
                total = sum(info["chunks"] for info in registry.values())
                st.caption(f"Total: {len(registry)} files, {total} chunks")
            else:
                st.info("No documents uploaded yet.")

    with tab_admin:
        st.subheader("Database Management")
        st.warning("Clear operation is irreversible!")

        if st.button("Clear Database", type="primary"):
            result = ingestion_service.clear_database()
            if result["success"]:
                st.success(result["message"])
            else:
                st.error(result["message"])


render()
