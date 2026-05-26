"""Generates Importer pipeline diagram using Python diagrams library."""
import os
os.environ["PATH"] += ":/usr/local/bin"

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.client import User
from diagrams.programming.language import Python
from diagrams.generic.storage import Storage
from diagrams.generic.place import Datacenter

OUTPUT = os.path.join(os.path.dirname(__file__), "diagrams", "importer_pipeline")
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

graph_attr = {
    "fontsize": "13",
    "bgcolor": "white",
    "pad": "0.6",
    "splines": "ortho",
    "nodesep": "1.0",
    "ranksep": "0.8",
}

node_attr = {
    "fontsize": "11",
}

with Diagram(
    "Importer Pipeline — Recursive Chunking",
    filename=OUTPUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
    node_attr=node_attr,
):
    pdf = Storage("PDF File")

    with Cluster("rag_app — Importer", graph_attr={"margin": "40"}):
        loader    = Python("PyMuPDF Loader\n[tekst per strona]")
        splitter  = Python("RecursiveCharacter\nTextSplitter\n[size=250, overlap=50]")
        meta      = Python("Metadata Enrichment\n[chunk_id · source\npage · chunk_size]")
        embedder  = Python("OpenAI Embeddings\n[text-embedding-3-small]")

    with Cluster("rag_db", graph_attr={"margin": "40"}):
        pgvector  = PostgreSQL("PostgreSQL\n+ PGVector\n[study_docs]")

    pdf >> Edge(label="upload") >> loader
    loader >> Edge(label="raw pages") >> splitter
    splitter >> Edge(label="chunks") >> meta
    meta >> Edge(label="enriched chunks") >> embedder
    embedder >> Edge(label="vectors + metadata") >> pgvector

print(f"Saved: {OUTPUT}.png")
