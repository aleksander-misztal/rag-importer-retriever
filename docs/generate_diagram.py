"""Generates RAG System Architecture diagram using matplotlib."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "diagrams", "system_architecture.png")
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

W, H = 22, 11
fig, ax = plt.subplots(figsize=(W, H))
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")
fig.patch.set_facecolor("#FAFAFA")

# ── helpers ───────────────────────────────────────────────────────────────────

def box(ax, x, y, w, h, label, sub="", fc="#DDEEFF", ec="#4477AA", fs=10):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12",
                                facecolor=fc, edgecolor=ec, linewidth=1.8))
    cy = y + h / 2
    if sub:
        ax.text(x+w/2, cy+0.22, label, ha="center", va="center", fontsize=fs, fontweight="bold", color="#1a1a3e")
        ax.text(x+w/2, cy-0.24, sub,   ha="center", va="center", fontsize=8,  color="#444466", style="italic")
    else:
        ax.text(x+w/2, cy, label, ha="center", va="center", fontsize=fs, fontweight="bold", color="#1a1a3e")

def boundary(ax, x, y, w, h, label, fc="#EEF6FF", ec="#7799CC", ls="--"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2",
                                facecolor=fc, edgecolor=ec, linewidth=2.0, linestyle=ls))
    ax.text(x+0.25, y+h-0.18, label, ha="left", va="top", fontsize=9, color=ec, fontweight="bold")

def harrow(ax, x1, x2, y, label="", ec="#4477AA", lbl_dy=0.13):
    ax.annotate("", xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle="-|>", color=ec, lw=1.5))
    if label:
        ax.text((x1+x2)/2, y+lbl_dy, label, ha="center", va="bottom", fontsize=7.5, color="#334466")

def varrow(ax, x, y1, y2, label="", ec="#4477AA"):
    ax.annotate("", xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle="-|>", color=ec, lw=1.5))
    if label:
        ax.text(x+0.12, (y1+y2)/2, label, ha="left", va="center", fontsize=7.5, color="#334466")

# ── title ─────────────────────────────────────────────────────────────────────
ax.text(W/2, 10.6, "RAG Evaluation System — Architektura", ha="center", fontsize=15,
        fontweight="bold", color="#1a1a3e")

# ── Docker Compose boundary ───────────────────────────────────────────────────
boundary(ax, 3.5, 0.4, 14.5, 9.6, "Docker Compose", fc="#F5FAFF", ec="#5588BB")

# ── rag_app boundary ─────────────────────────────────────────────────────────
boundary(ax, 4.1, 1.2, 10.0, 8.2, "rag_app", fc="#EBF5EB", ec="#2E7D32")

# ── rag_db boundary ──────────────────────────────────────────────────────────
boundary(ax, 14.5, 3.5, 3.0, 4.0, "rag_db", fc="#EDE7F6", ec="#4527A0")

# ── Researcher ────────────────────────────────────────────────────────────────
box(ax, 0.3, 7.5, 2.6, 1.2, "Researcher", fc="#FFF8E1", ec="#CC9900", fs=11)

# ── rag_app nodes ─────────────────────────────────────────────────────────────
box(ax, 4.8, 7.5, 3.0, 1.2, "Streamlit", "Web App", fc="#C8E6C9", ec="#2E7D32", fs=10)
box(ax, 4.8, 5.5, 3.0, 1.2, "Importer",  "PDF → chunks → PGVector", fc="#DCEDC8", ec="#558B2F", fs=10)
box(ax, 4.8, 3.5, 3.0, 1.2, "Retriever", "RAG Pipeline", fc="#B3E5FC", ec="#0277BD", fs=10)
box(ax, 4.8, 1.5, 3.0, 1.2, "Eval Runner", "orchestracja ewaluacji", fc="#FFF3E0", ec="#E65100", fs=10)

# ── PGVector ──────────────────────────────────────────────────────────────────
box(ax, 14.8, 4.8, 2.4, 1.4, "PostgreSQL", "+ PGVector", fc="#EDE7F6", ec="#4527A0", fs=10)

# ── OpenAI ────────────────────────────────────────────────────────────────────
box(ax, 19.0, 4.5, 2.6, 2.2, "OpenAI API", "embeddings\ngpt-4o-mini\ngpt-4o judge", fc="#FCE4EC", ec="#880E4F", fs=10)

# ── Researcher → Streamlit ────────────────────────────────────────────────────
harrow(ax, 2.9, 4.8, 8.1, "HTTP")

# ── Streamlit → Importer / Retriever ─────────────────────────────────────────
varrow(ax, 6.3, 7.5, 6.7)   # Streamlit → Importer
varrow(ax, 6.3, 5.5, 4.7)   # Importer → Retriever (layout spacing)
varrow(ax, 6.3, 6.7, 5.5, "upload PDF")
varrow(ax, 6.3, 5.5, 4.7, "query")

# ── Importer → PGVector ───────────────────────────────────────────────────────
harrow(ax, 7.8, 14.8, 5.5, "store chunks", ec="#558B2F")

# ── Retriever → PGVector ──────────────────────────────────────────────────────
harrow(ax, 7.8, 14.8, 4.15, "vector search", ec="#0277BD")

# ── Importer → OpenAI ────────────────────────────────────────────────────────
# right angle: up then right
ax.plot([7.8, 18.0], [6.1, 6.1], color="#558B2F", lw=1.5)
ax.annotate("", xy=(19.0, 5.8), xytext=(18.0, 5.8),
            arrowprops=dict(arrowstyle="-|>", color="#558B2F", lw=1.5))
ax.plot([18.0, 18.0], [5.8, 6.1], color="#558B2F", lw=1.5)
ax.text(13.0, 6.25, "text-embedding-3-small", ha="center", fontsize=7.5, color="#558B2F")

# ── Retriever → OpenAI ───────────────────────────────────────────────────────
harrow(ax, 7.8, 19.0, 5.0, "gpt-4o-mini", ec="#0277BD")

# ── EvalRunner → Retriever ───────────────────────────────────────────────────
varrow(ax, 6.3, 3.5, 2.7, "invoke()", ec="#E65100")

# ── EvalRunner → OpenAI ──────────────────────────────────────────────────────
ax.plot([7.8, 18.0], [2.1, 2.1], color="#E65100", lw=1.5)
ax.annotate("", xy=(19.0, 4.5), xytext=(19.0, 2.1),
            arrowprops=dict(arrowstyle="-|>", color="#E65100", lw=1.5))
ax.text(13.0, 1.85, "judge gpt-4o", ha="center", fontsize=7.5, color="#E65100")

# ── legend ────────────────────────────────────────────────────────────────────
legend = [
    mpatches.Patch(fc="#C8E6C9", ec="#2E7D32",  label="Web App (Streamlit)"),
    mpatches.Patch(fc="#DCEDC8", ec="#558B2F",  label="Importer"),
    mpatches.Patch(fc="#B3E5FC", ec="#0277BD",  label="Retriever (RAG)"),
    mpatches.Patch(fc="#FFF3E0", ec="#E65100",  label="Eval Runner"),
    mpatches.Patch(fc="#EDE7F6", ec="#4527A0",  label="PostgreSQL + PGVector"),
    mpatches.Patch(fc="#FCE4EC", ec="#880E4F",  label="OpenAI API"),
]
ax.legend(handles=legend, loc="lower right", fontsize=9,
          framealpha=0.9, edgecolor="#AAAACC", fancybox=True)

plt.tight_layout()
plt.savefig(OUTPUT, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"Saved: {OUTPUT}")
