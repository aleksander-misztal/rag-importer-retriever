"""Generates RAG pipeline diagrams: Baseline and Multi-Query using matplotlib."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import os

OUT = os.path.join(os.path.dirname(__file__), "diagrams")
os.makedirs(OUT, exist_ok=True)

# ── shared helpers ────────────────────────────────────────────────────────────

def make_fig(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w); ax.set_ylim(0, h)
    ax.axis("off")
    fig.patch.set_facecolor("#FAFAFA")
    return fig, ax

def box(ax, x, y, w, h, label, sub="", fc="#DDEEFF", ec="#4477AA", fs=10):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12",
                                facecolor=fc, edgecolor=ec, linewidth=1.8))
    cy = y + h / 2
    if sub:
        ax.text(x+w/2, cy+0.2,  label, ha="center", va="center", fontsize=fs, fontweight="bold", color="#1a1a3e")
        ax.text(x+w/2, cy-0.22, sub,   ha="center", va="center", fontsize=8,  color="#444466", style="italic")
    else:
        ax.text(x+w/2, cy, label, ha="center", va="center", fontsize=fs, fontweight="bold", color="#1a1a3e")

def boundary(ax, x, y, w, h, label, fc="#EEF6FF", ec="#7799CC", ls="--"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2",
                                facecolor=fc, edgecolor=ec, linewidth=2.0, linestyle=ls))
    ax.text(x+0.2, y+h-0.15, label, ha="left", va="top", fontsize=9, color=ec, fontweight="bold")

def harrow(ax, x1, x2, y, label="", ec="#4477AA", lpos="above"):
    ax.annotate("", xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle="-|>", color=ec, lw=1.6))
    if label:
        dy = 0.14 if lpos == "above" else -0.22
        ax.text((x1+x2)/2, y+dy, label, ha="center", va="bottom" if lpos=="above" else "top",
                fontsize=8, color="#334466")

def varrow(ax, x, y1, y2, label="", ec="#4477AA"):
    ax.annotate("", xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle="-|>", color=ec, lw=1.6))
    if label:
        ax.text(x+0.12, (y1+y2)/2, label, ha="left", va="center", fontsize=8, color="#334466")


# ═════════════════════════════════════════════════════════════════════════════
# 1. BASELINE SEQUENTIAL RAG
# ═════════════════════════════════════════════════════════════════════════════
fig, ax = make_fig(16, 5)
ax.text(8, 4.7, "Baseline Sequential RAG", ha="center", fontsize=14,
        fontweight="bold", color="#1a1a3e")

# pipeline boundary
boundary(ax, 0.3, 0.4, 15.4, 3.9, "rag_app — Retriever")

# nodes (LR, y=1.8 center)
Y = 1.9
box(ax, 0.7,  Y, 2.0, 1.4, "Zapytanie",          fc="#FFF8E1", ec="#CC9900")
box(ax, 3.2,  Y, 2.4, 1.4, "Security Node",   "gpt-4o-mini",      fc="#C8E6C9", ec="#2E7D32")
box(ax, 6.2,  Y, 2.6, 1.4, "Embedding\n+ Search", "text-embedding-3-small\nPGVector top-k=20", fc="#EDE7F6", ec="#4527A0")
box(ax, 9.4,  Y, 2.4, 1.4, "Synthesizer",     "gpt-4o-mini",      fc="#C8E6C9", ec="#2E7D32")
box(ax, 12.5, Y, 2.4, 1.4, "Odpowiedź",           fc="#FFF8E1", ec="#CC9900")

# arrows
harrow(ax, 2.7,  3.2,  2.6, "pytanie")
harrow(ax, 5.6,  6.2,  2.6, "safe")
harrow(ax, 8.8,  9.4,  2.6, "top-k chunks")
harrow(ax, 11.8, 12.5, 2.6, "odpowiedź")

# unsafe branch
ax.annotate("", xy=(3.7, 0.4), xytext=(3.7, Y),
            arrowprops=dict(arrowstyle="-|>", color="#CC3333", lw=1.4, linestyle="dashed"))
ax.text(3.85, 0.9, "unsafe →\nodrzucone", fontsize=7.5, color="#CC3333", va="center")

plt.tight_layout()
plt.savefig(os.path.join(OUT, "01_baseline_rag.png"), dpi=180, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print("Saved: 01_baseline_rag.png")


# ═════════════════════════════════════════════════════════════════════════════
# 2. MULTI-QUERY RAG
# ═════════════════════════════════════════════════════════════════════════════
fig, ax = make_fig(18, 10)
ax.text(9, 9.7, "Multi-Query RAG", ha="center", fontsize=14,
        fontweight="bold", color="#1a1a3e")

boundary(ax, 0.3, 0.4, 17.4, 9.0, "rag_app — Retriever")

# row 1: Question → Security → Generator
box(ax, 0.7,  7.8, 2.0, 1.2, "Zapytanie",     fc="#FFF8E1", ec="#CC9900")
box(ax, 3.5,  7.8, 2.4, 1.2, "Security Node", "gpt-4o-mini", fc="#C8E6C9", ec="#2E7D32")
box(ax, 6.8,  7.8, 2.8, 1.2, "Generator Node","gpt-4o-mini\nn sub-queries", fc="#C8E6C9", ec="#2E7D32")

harrow(ax, 2.7,  3.5,  8.4, "pytanie")
harrow(ax, 5.9,  6.8,  8.4, "safe")

# fan-out lines from Generator (x=8.2, y=7.8) down to 3 sub-queries
GEN_X = 8.2
GEN_Y_BOT = 7.8
SQ_Y_TOP  = 6.4
SQ_YC     = 5.8  # center of sub-query boxes

# three sub-query columns
cols = [3.2, 7.7, 12.2]
labels_sq = ["sub-query 1", "sub-query 2", "sub-query 3"]

# fan-out: line down from generator midpoint then branches
ax.plot([GEN_X, GEN_X], [GEN_Y_BOT, 7.1], color="#2E7D32", lw=1.6)
ax.plot([cols[0]+1.0, cols[2]+1.0], [7.1, 7.1], color="#2E7D32", lw=1.6)
for cx in cols:
    ax.annotate("", xy=(cx+1.0, SQ_Y_TOP+0.8), xytext=(cx+1.0, 7.1),
                arrowprops=dict(arrowstyle="-|>", color="#2E7D32", lw=1.6))

# sub-query boxes
for i, (cx, lbl) in enumerate(zip(cols, labels_sq)):
    box(ax, cx, SQ_Y_TOP, 2.0, 0.8, lbl, fc="#DCEDC8", ec="#558B2F", fs=9)

# PGVector boxes
PV_Y = 4.2
boundary(ax, 0.5, 3.8, 16.8, 1.8, "PGVector  —  top-k=20 per sub-query", fc="#F3EEF9", ec="#4527A0", ls="-")
for cx in cols:
    box(ax, cx, PV_Y, 2.0, 0.9, "PGVector", "vector search", fc="#EDE7F6", ec="#4527A0", fs=9)
    varrow(ax, cx+1.0, SQ_Y_TOP, PV_Y+0.9)

# fan-in: converge to Flatten
FLAT_X = 7.5
FLAT_Y = 2.5
FLAT_W = 3.0
FLAT_H = 1.0

ax.plot([cols[0]+1.0, cols[2]+1.0], [PV_Y, PV_Y], color="#4527A0", lw=1.0, ls=":")
for cx in cols:
    ax.annotate("", xy=(FLAT_X + FLAT_W/2, FLAT_Y+FLAT_H), xytext=(cx+1.0, PV_Y),
                arrowprops=dict(arrowstyle="-|>", color="#4527A0", lw=1.6))

box(ax, FLAT_X, FLAT_Y, FLAT_W, FLAT_H, "Flatten + Dedup", "deduplikacja chunków", fc="#E3F2FD", ec="#1565C0")

# Flatten → Synthesizer → Answer  (centered below Flatten)
SYN_X = FLAT_X + FLAT_W/2 - 1.4   # center Synthesizer under Flatten
SYN_Y = 1.0
box(ax, SYN_X, SYN_Y, 2.8, 1.0, "Synthesizer", "gpt-4o-mini", fc="#C8E6C9", ec="#2E7D32")
box(ax, SYN_X+3.5, SYN_Y, 2.5, 1.0, "Odpowiedź", fc="#FFF8E1", ec="#CC9900")

varrow(ax, FLAT_X + FLAT_W/2, FLAT_Y, SYN_Y+1.0)
harrow(ax, SYN_X+2.8, SYN_X+3.5, SYN_Y+0.5, "odpowiedź")

# unsafe — route LEFT of PGVector boundary
SEC_CX = 3.5 + 2.4/2   # center x of Security Node
ax.plot([SEC_CX, SEC_CX], [7.8, 7.3], color="#CC3333", lw=1.4, ls="dashed")  # down from sec
ax.plot([SEC_CX, 0.9],    [7.3, 7.3], color="#CC3333", lw=1.4, ls="dashed")  # left
ax.annotate("", xy=(0.9, 0.6), xytext=(0.9, 7.3),
            arrowprops=dict(arrowstyle="-|>", color="#CC3333", lw=1.4, linestyle="dashed"))
ax.text(1.15, 3.8, "unsafe\n→ odrzucone", fontsize=7.5, color="#CC3333", va="center", ha="left")

plt.tight_layout()
plt.savefig(os.path.join(OUT, "02_multi_query_rag.png"), dpi=180, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print("Saved: 02_multi_query_rag.png")


# ═════════════════════════════════════════════════════════════════════════════
# 3. MULTI-STEP RAG (sequential / cascading)
# ═════════════════════════════════════════════════════════════════════════════
fig, ax = make_fig(18, 11)
ax.text(9, 10.7, "Multi-Step RAG", ha="center", fontsize=14,
        fontweight="bold", color="#1a1a3e")

boundary(ax, 0.3, 0.4, 17.4, 10.0, "rag_app — Retriever")

# row 1: entry
box(ax, 0.7,  8.8, 2.0, 1.1, "Zapytanie",      fc="#FFF8E1", ec="#CC9900")
box(ax, 3.3,  8.8, 2.4, 1.1, "Security Node",  "gpt-4o-mini", fc="#C8E6C9", ec="#2E7D32")
box(ax, 6.5,  8.8, 2.8, 1.1, "Decomposer",     "gpt-4o-mini\nrozkład na podpytania", fc="#C8E6C9", ec="#2E7D32")

harrow(ax, 2.7, 3.3, 9.35, "pytanie")
harrow(ax, 5.7, 6.5, 9.35, "safe")

# cascade steps
step_data = [
    (1, 7.2, "sub-query 1",          "kontekst 1"),
    (2, 5.0, "sub-query 2 + ctx 1",  "kontekst 2"),
    (3, 2.8, "sub-query 3 + ctx 1+2","kontekst 3"),
]

PV_X = 11.5
PV_W = 2.4
CTX_X = 14.5
CTX_W = 2.4

prev_ctx_y = None

for step, sq_y, sq_label, ctx_label in step_data:
    sq_h = 1.0
    sq_x = 6.5
    sq_w = 3.8

    # sub-query box
    box(ax, sq_x, sq_y, sq_w, sq_h, sq_label, fc="#DCEDC8", ec="#558B2F", fs=9)

    # PGVector
    box(ax, PV_X, sq_y, PV_W, sq_h, "PGVector", "top-k=20", fc="#EDE7F6", ec="#4527A0", fs=9)

    # context result
    box(ax, CTX_X, sq_y, CTX_W, sq_h, ctx_label, fc="#E3F2FD", ec="#1565C0", fs=9)

    # arrows: sq → PGVector → ctx
    harrow(ax, sq_x+sq_w, PV_X, sq_y+sq_h/2)
    harrow(ax, PV_X+PV_W, CTX_X, sq_y+sq_h/2)

    # arrow from Decomposer / previous ctx to this sub-query
    if step == 1:
        # from Decomposer down to sub-query 1
        dec_cx = 6.5 + 2.8/2
        ax.plot([dec_cx, dec_cx], [8.8, sq_y+sq_h], color="#2E7D32", lw=1.6)
        ax.annotate("", xy=(sq_x+sq_w/2, sq_y+sq_h),
                    xytext=(dec_cx, sq_y+sq_h),
                    arrowprops=dict(arrowstyle="-|>", color="#2E7D32", lw=1.6))
    else:
        # from previous context + vertical connector
        ax.plot([CTX_X+CTX_W/2, CTX_X+CTX_W/2], [prev_ctx_y, sq_y+sq_h],
                color="#1565C0", lw=1.4, ls=":")
        ax.annotate("", xy=(sq_x+sq_w/2, sq_y+sq_h),
                    xytext=(CTX_X+CTX_W/2, sq_y+sq_h),
                    arrowprops=dict(arrowstyle="-|>", color="#1565C0", lw=1.6))
        ax.text(CTX_X+CTX_W/2+0.1, (prev_ctx_y+sq_y+sq_h)/2,
                "informs\nnext step", fontsize=7.5, color="#1565C0", va="center")

    prev_ctx_y = sq_y

# Agregacja + Synthesizer + Odpowiedź
AGG_Y = 1.3
box(ax, 9.5,  AGG_Y, 2.4, 1.0, "Agregacja",   "łączenie kontekstów", fc="#E3F2FD", ec="#1565C0")
box(ax, 12.5, AGG_Y, 2.4, 1.0, "Synthesizer", "gpt-4o-mini",         fc="#C8E6C9", ec="#2E7D32")
box(ax, 15.4, AGG_Y, 1.8, 1.0, "Odpowiedź",   fc="#FFF8E1", ec="#CC9900")

# last ctx → agregacja
ax.plot([CTX_X+CTX_W/2, CTX_X+CTX_W/2], [prev_ctx_y, AGG_Y+1.0], color="#1565C0", lw=1.4, ls=":")
ax.annotate("", xy=(9.5+2.4/2, AGG_Y+1.0), xytext=(CTX_X+CTX_W/2, AGG_Y+1.0),
            arrowprops=dict(arrowstyle="-|>", color="#1565C0", lw=1.6))

harrow(ax, 11.9, 12.5, AGG_Y+0.5)
harrow(ax, 14.9, 15.4, AGG_Y+0.5, "odpowiedź")

# unsafe
ax.annotate("", xy=(4.5, 0.6), xytext=(4.5, 8.8),
            arrowprops=dict(arrowstyle="-|>", color="#CC3333", lw=1.4, linestyle="dashed"))
ax.text(4.65, 4.5, "unsafe\n→ odrzucone", fontsize=7.5, color="#CC3333", va="center")

plt.tight_layout()
plt.savefig(os.path.join(OUT, "03_multi_step_rag.png"), dpi=180, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print("Saved: 03_multi_step_rag.png")


# ═════════════════════════════════════════════════════════════════════════════
# 4. AGENTIC RAG (ReAct loop)
# ═════════════════════════════════════════════════════════════════════════════
fig, ax = make_fig(18, 10)
ax.text(9, 9.7, "Agentic RAG — ReAct Loop", ha="center", fontsize=14,
        fontweight="bold", color="#1a1a3e")

boundary(ax, 0.3, 0.4, 17.4, 9.0, "rag_app — Retriever")

# entry
box(ax, 0.7, 7.8, 2.0, 1.2, "Zapytanie",     fc="#FFF8E1", ec="#CC9900")
box(ax, 3.5, 7.8, 2.4, 1.2, "Security Node", "gpt-4o-mini", fc="#C8E6C9", ec="#2E7D32")
harrow(ax, 2.7, 3.5, 8.4, "pytanie")

# Agent node (central)
box(ax, 6.8, 7.2, 3.0, 1.6, "Agent LLM", "gpt-4o-mini\nReAct reasoning", fc="#C8E6C9", ec="#1B5E20", fs=11)
harrow(ax, 5.9, 6.8, 8.0, "safe")

# ReAct loop boundary
boundary(ax, 6.4, 1.5, 10.8, 5.4, "Pętla ReAct  (max 5 iteracji)",
         fc="#F9FBE7", ec="#827717")

# Think
box(ax, 7.0, 4.6, 2.6, 1.0, "Reasoning", "Co wiem? Czego brak?", fc="#F9FBE7", ec="#827717", fs=9)
# Act
box(ax, 7.0, 3.2, 2.6, 1.0, "Act", "vector_search(query, k=20)", fc="#FFF3E0", ec="#E65100", fs=9)
# PGVector
box(ax, 11.0, 3.2, 2.6, 1.0, "PGVector", "top-k=20", fc="#EDE7F6", ec="#4527A0", fs=9)
# Observe
box(ax, 11.0, 4.6, 2.6, 1.0, "Obserwacja", "nowe chunki\ndodane do kontekstu", fc="#F9FBE7", ec="#827717", fs=9)

# loop arrows: Think → Act → PGVector → Observe → back to Think
varrow(ax, 8.3, 4.6, 4.2)
harrow(ax, 9.6, 11.0, 3.7)
varrow(ax, 12.3, 4.2, 4.6)
harrow(ax, 11.0, 9.6, 5.1)

# agent → Think (enter loop)
varrow(ax, 8.3, 7.2, 5.6)

# loop back arrow (left side)
ax.plot([7.0, 6.7], [5.1, 5.1], color="#827717", lw=1.4)
ax.plot([6.7, 6.7], [5.1, 7.6], color="#827717", lw=1.4)
ax.annotate("", xy=(6.8, 7.6), xytext=(6.7, 7.6),
            arrowprops=dict(arrowstyle="-|>", color="#827717", lw=1.4))
ax.text(6.0, 6.3, "ponów\njeśli brak\nkontekstu", fontsize=7.5, color="#827717",
        ha="center", va="center")

# exit: enough context → Synthesizer
box(ax, 14.5, 5.5, 2.6, 1.2, "Synthesizer", "gpt-4o-mini", fc="#C8E6C9", ec="#2E7D32")
box(ax, 14.5, 7.8, 2.6, 1.2, "Odpowiedź",   fc="#FFF8E1", ec="#CC9900")

# Observe → exit condition
ax.annotate("", xy=(14.5, 6.1), xytext=(13.6, 5.1),
            arrowprops=dict(arrowstyle="-|>", color="#1B5E20", lw=1.6))
ax.text(14.1, 5.45, "wystarczy\nkontekstu", fontsize=7.5, color="#1B5E20", ha="center")

varrow(ax, 15.8, 6.7, 7.8, "odpowiedź")

# max iterations → force exit
box(ax, 7.5, 1.6, 3.0, 0.9, "max_iterations = 5", "wymuś syntezę", fc="#FFEBEE", ec="#B71C1C", fs=8)
ax.annotate("", xy=(14.5, 5.8), xytext=(10.5, 2.05),
            arrowprops=dict(arrowstyle="-|>", color="#B71C1C", lw=1.4, linestyle="dashed"))
ax.text(12.5, 3.6, "force exit", fontsize=7.5, color="#B71C1C", ha="center")

# unsafe
ax.annotate("", xy=(4.7, 0.6), xytext=(4.7, 7.8),
            arrowprops=dict(arrowstyle="-|>", color="#CC3333", lw=1.4, linestyle="dashed"))
ax.text(4.85, 4.2, "unsafe\n→ odrzucone", fontsize=7.5, color="#CC3333", va="center")

plt.tight_layout()
plt.savefig(os.path.join(OUT, "04_agentic_rag.png"), dpi=180, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print("Saved: 04_agentic_rag.png")
