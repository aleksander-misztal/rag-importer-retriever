import streamlit as st

st.set_page_config(
    page_title="RAG System",
    page_icon="📚",
    layout="wide",
)

importer_page = st.Page("pages/importer.py", title="Importer", icon="📤")
retriever_page = st.Page("pages/retriever.py", title="Retriever", icon="🤖")

pg = st.navigation([importer_page, retriever_page])
pg.run()
