"""Generates Evaluator pipeline diagram using matplotlib."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "diagrams", "evaluator_pipeline.png")
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

W, H = 20, 12
fig, ax = plt.subplots(figsize=(W, H))
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")
fig.patch.set_facecolor("#FAFAFA")

# ── helpers ──────────────────────────────────────────────────────────────────

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

def harrow(ax, x1, x2, y, label="", ec="#4477AA"):
    ax.annotate("", xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle="-|>", color=ec, lw=1.6))
    if label:
        ax.text((x1+x2)/2, y+0.12, label, ha="center", va="bottom", fontsize=8, color="#334466")

def varrow(ax, x, y1, y2, label="", ec="#4477AA"):
    ax.annotate("", xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle="-|>", color=ec, lw=1.6))
    if label:
        ax.text(x+0.12, (y1+y2)/2, label, ha="left", va="center", fontsize=8, color="#334466")

# ═══════════════════════════════════════════════════════════════════════════
# LAYOUT GRID
# Col A: x=0.2  w=2.6   — inputs + runner
# Col B: x=3.2  w=9.2   — loop area
#   Col B1: x=3.7  w=3.0  — RAG + collector
#   Col B2: x=7.1  w=2.8  — PGVector + OpenAI
# Col C: x=13.0 w=3.8   — metric boxes (right)
# Bottom: y=0.3..2.5    — stability + JSON
# ═══════════════════════════════════════════════════════════════════════════

# ── title ────────────────────────────────────────────────────────────────────
ax.text(W/2, 11.65, "Evaluator Pipeline", ha="center", fontsize=15,
        fontweight="bold", color="#1a1a3e")

# ── Col A: inputs & runner ────────────────────────────────────────────────────
box(ax, 0.2, 9.7,  2.6, 0.9, "questions.json", "100 pytań + ground truth",
    fc="#FFF8E1", ec="#CC9900")
box(ax, 0.2, 8.5,  2.6, 0.9, ".env / config", "architektura · model · k",
    fc="#FFF8E1", ec="#CC9900")
box(ax, 0.2, 5.8,  2.6, 1.8, "Eval Runner", "orchestracja\npętla pytań",
    fc="#E3F2FD", ec="#1565C0", fs=11)

harrow(ax, 2.8, 3.2, 10.15)  # questions → outer loop (via right)
ax.plot([2.8, 2.8], [8.95, 10.15], color="#CC9900", lw=1.6)   # down from questions
harrow(ax, 2.8, 3.2, 8.95)   # config → outer loop
ax.plot([2.8, 2.8], [8.5,  8.95], color="#CC9900", lw=1.6)    # up from config
# inputs → runner vertical
varrow(ax, 1.5, 9.7,  7.6)
varrow(ax, 1.5, 8.5,  7.6)

# ── runner → loop ────────────────────────────────────────────────────────────
harrow(ax, 2.8, 3.5, 6.7, "  invoke()")

# ── Col B: outer loop ─────────────────────────────────────────────────────────
boundary(ax, 3.2, 0.3, 9.2, 11.0, "dla każdego pytania  ×100",
         fc="#F5FAFF", ec="#5588BB")

# inner loop
boundary(ax, 3.7, 3.8, 6.2, 6.6, "dla każdego run  ×5",
         fc="#EBF5EB", ec="#2E7D32")

# RAG Pipeline
box(ax, 4.0, 8.5, 2.8, 1.4, "RAG Pipeline", "invoke(question)\ngpt-4o-mini",
    fc="#C8E6C9", ec="#2E7D32")

# MetricsCollector (below RAG)
box(ax, 4.0, 6.7, 2.8, 1.4, "MetricsCollector", "[LangChain callback]\ntokeny · latency · koszt",
    fc="#DCEDC8", ec="#558B2F")

# PGVector (right of RAG)
box(ax, 7.2, 8.5, 2.0, 1.4, "PGVector", "vector search\ntop-k=20",
    fc="#EDE7F6", ec="#4527A0")

# OpenAI in pipeline (right of collector)
box(ax, 7.2, 6.7, 2.0, 1.4, "OpenAI API", "gpt-4o-mini\nsec·gen·synth",
    fc="#F3E5F5", ec="#6A1B9A")

# arrows inside inner loop
harrow(ax, 6.8, 7.2, 9.2, "", "#2E7D32")   # RAG → PGVector
varrow(ax, 5.4, 8.5, 8.1)                  # RAG → Collector
harrow(ax, 6.8, 7.2, 7.4, "", "#2E7D32")   # Collector → OpenAI

# ── per-run results → right column ───────────────────────────────────────────
# vertical bus line at x=12.5
bus_x = 12.5

# from RAG → bus (chunk_ids + answer)
ax.annotate("", xy=(bus_x, 9.2), xytext=(9.2, 9.2),
            arrowprops=dict(arrowstyle="-|>", color="#1565C0", lw=1.6))
ax.text(10.8, 9.35, "chunk_ids + answer", ha="center", fontsize=8, color="#334466")

# from MetricsCollector → bus (metrics)
ax.annotate("", xy=(bus_x, 7.4), xytext=(9.2, 7.4),
            arrowprops=dict(arrowstyle="-|>", color="#558B2F", lw=1.6))
ax.text(10.8, 7.55, "latency · tokens · cost", ha="center", fontsize=8, color="#334466")

# ── Col C: metric boxes ───────────────────────────────────────────────────────
box(ax, 13.0, 9.0, 3.8, 1.5, "Retrieval Metrics", "recall · precision\nFPR · coverage",
    fc="#E3F2FD", ec="#1565C0")
box(ax, 13.0, 7.0, 3.8, 1.5, "LLM Judge", "gpt-4o\nquality 0-3 · faithfulness",
    fc="#FBE9E7", ec="#BF360C")
box(ax, 13.0, 5.0, 3.8, 1.5, "Performance", "latency · tokens\ncost_usd · cost/correct",
    fc="#E8F5E9", ec="#2E7D32")

# bus → metric boxes
harrow(ax, bus_x, 13.0, 9.75, "", "#1565C0")
ax.text(bus_x+0.1, 9.95, "vs ground truth", fontsize=8, color="#1565C0")
harrow(ax, bus_x, 13.0, 7.75, "", "#BF360C")
ax.text(bus_x+0.1, 7.95, "answer + context", fontsize=8, color="#BF360C")
harrow(ax, bus_x, 13.0, 5.75, "", "#2E7D32")
ax.text(bus_x+0.1, 5.95, "collector.metrics", fontsize=8, color="#2E7D32")

# vertical bus line (visual)
ax.plot([bus_x, bus_x], [7.4, 9.2], color="#888888", lw=1.4, ls=":")

# ── Stability (after all 5 runs) ──────────────────────────────────────────────
box(ax, 4.0, 1.5, 3.5, 1.5, "Stability Analyzer", "variance · consistency\npo 5 runs",
    fc="#FFF3E0", ec="#E65100")

# metric boxes → stability: right-angle path down then left
# vertical line at x=17.2 from y=5.0 down to y=2.25, then left to stability
ax.plot([16.8, 16.8], [5.0, 2.25], color="#E65100", lw=1.6)         # down
ax.annotate("", xy=(7.5, 2.25), xytext=(16.8, 2.25),
            arrowprops=dict(arrowstyle="-|>", color="#E65100", lw=1.6))  # left
ax.text(12.5, 2.45, "agregacja 5 runs", ha="center", fontsize=8, color="#E65100")

# ── JSON output ───────────────────────────────────────────────────────────────
box(ax, 4.0, 0.2, 3.5, 1.0, "results / arch_timestamp.json", "",
    fc="#FFF8E1", ec="#CC9900", fs=10)

varrow(ax, 5.75, 1.5, 1.2)

# ── legend ───────────────────────────────────────────────────────────────────
legend = [
    mpatches.Patch(fc="#C8E6C9", ec="#2E7D32",  label="RAG pipeline"),
    mpatches.Patch(fc="#E3F2FD", ec="#1565C0",  label="Retrieval Metrics (no LLM)"),
    mpatches.Patch(fc="#FBE9E7", ec="#BF360C",  label="LLM Judge (gpt-4o)"),
    mpatches.Patch(fc="#E8F5E9", ec="#2E7D32",  label="Performance"),
    mpatches.Patch(fc="#FFF3E0", ec="#E65100",  label="Stability (po 5 runs)"),
    mpatches.Patch(fc="#FFF8E1", ec="#CC9900",  label="Input / Output"),
]
ax.legend(handles=legend, loc="lower right", fontsize=9,
          framealpha=0.9, edgecolor="#AAAACC", fancybox=True)

plt.tight_layout()
plt.savefig(OUTPUT, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"Saved: {OUTPUT}")
