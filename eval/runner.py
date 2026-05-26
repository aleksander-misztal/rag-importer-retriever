"""
Evaluation runner.

Usage:
    PYTHONPATH=app python eval/runner.py --arch baseline --runs 5

Results are saved to eval/results/{arch}_{timestamp}.json
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Make app/ and project root importable
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from dependency_container import DependencyContainer
from retriever.core.graph import create_graph
from shared.common.config import CONFIG

from eval.collector import MetricsCollector
from eval.metrics.retrieval import compute_retrieval_metrics, aggregate_retrieval_metrics
from eval.metrics.generation import GenerationJudge, aggregate_generation_metrics
from eval.metrics.performance import compute_performance, aggregate_performance_metrics
from eval.stability.analyzer import compute_stability, aggregate_stability

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

RESULTS_DIR = Path(__file__).parent / "results"
DATASET_PATH = Path(__file__).parent / "dataset" / "questions.json"
RETRIEVAL_K = 10  # evaluate at top-10 (after reranker)


def load_dataset() -> list[dict]:
    with open(DATASET_PATH) as f:
        return json.load(f)


def build_rag(container: DependencyContainer):
    if CONFIG.RERANKING_ENABLED:
        return create_graph(
            security=container.security_node(),
            generator=container.generator_node(),
            executor=container.executor_node(),
            synthesizer=container.synthesizer_node(),
            reranker=container.reranker_node(),
        )
    return create_graph(
        security=container.security_node(),
        generator=container.generator_node(),
        executor=container.executor_node(),
        synthesizer=container.synthesizer_node(),
        flatten=container.flatten_node(),
    )


def run_single(rag, question: str) -> tuple[dict, MetricsCollector, float]:
    """Invoke the RAG pipeline once, return (state, collector, latency_s)."""
    collector = MetricsCollector()
    t0 = time.perf_counter()
    state = rag.invoke(
        {"question": question},
        config={"callbacks": [collector]},
    )
    latency = time.perf_counter() - t0
    return state, collector, latency


def evaluate(arch_name: str, n_runs: int) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    dataset = load_dataset()
    container = DependencyContainer()
    rag = build_rag(container)
    judge = GenerationJudge(api_key=CONFIG.OPENAI_API_KEY, model=CONFIG.JUDGE_MODEL)

    logger.info(f"Starting eval: arch={arch_name}, runs={n_runs}, questions={len(dataset)}")

    all_question_results = []

    for q in dataset:
        qid      = q["id"]
        question = q["question"]
        gt_ids   = [cid for cid in q.get("relevant_chunk_ids", []) if cid != "PLACEHOLDER"]

        logger.info(f"[{qid}] Running {n_runs} runs...")

        runs = []
        for run_idx in range(n_runs):
            state, collector, latency = run_single(rag, question)

            retrieved_ids = [m.get("chunk_id", "") for m in state.get("context_metadata", [])]
            answer        = state.get("answer", "")
            context       = state.get("context", [])

            retrieval   = compute_retrieval_metrics(retrieved_ids, gt_ids, k=RETRIEVAL_K) if gt_ids else {}
            performance = compute_performance(collector.summary(), latency)
            generation  = judge.evaluate(question, answer, context)

            runs.append({
                "run":        run_idx,
                "answer":     answer,
                "retrieved_ids": retrieved_ids,
                "retrieval":  retrieval,
                "generation": generation,
                "performance": performance,
            })

            logger.info(
                f"  run {run_idx+1}/{n_runs} — quality={generation['answer_quality']} "
                f"faithful={generation['faithfulness']} latency={performance['latency_ms']}ms"
            )

        stability = compute_stability([r["generation"] for r in runs])

        all_question_results.append({
            "id":       qid,
            "question": question,
            "runs":     runs,
            "stability": stability,
        })

    # Aggregate across questions (use first run for retrieval/performance, all for stability)
    first_runs = [q["runs"][0] for q in all_question_results]

    agg_retrieval   = aggregate_retrieval_metrics([r["retrieval"]   for r in first_runs if r.get("retrieval")])
    agg_generation  = aggregate_generation_metrics([r["generation"] for r in first_runs])
    agg_performance = aggregate_performance_metrics(
        [r["performance"] for r in first_runs],
        [r["generation"]["is_correct"] for r in first_runs],
    )
    agg_stability = aggregate_stability([q["stability"] for q in all_question_results])

    total_judge_cost = sum(
        run["generation"]["cost_usd"]
        for q in all_question_results
        for run in q["runs"]
    )

    output = {
        "meta": {
            "arch":         arch_name,
            "n_runs":       n_runs,
            "n_questions":  len(dataset),
            "reranking":    CONFIG.RERANKING_ENABLED,
            "judge_model":  CONFIG.JUDGE_MODEL,
            "retrieval_k":  RETRIEVAL_K,
            "timestamp":    datetime.now(timezone.utc).isoformat(),
        },
        "aggregate": {
            "retrieval":   agg_retrieval,
            "generation":  agg_generation,
            "performance": agg_performance,
            "stability":   agg_stability,
            "total_judge_cost_usd": round(total_judge_cost, 6),
        },
        "questions": all_question_results,
    }

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = RESULTS_DIR / f"{arch_name}_{ts}.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logger.info(f"Results saved to {out_path}")
    _print_summary(output)


def _print_summary(output: dict) -> None:
    agg = output["aggregate"]
    meta = output["meta"]
    print(f"\n{'='*50}")
    print(f"  arch={meta['arch']}  runs={meta['n_runs']}  q={meta['n_questions']}")
    print(f"{'='*50}")
    if agg["retrieval"]:
        r = agg["retrieval"]
        print(f"  Retrieval   recall={r.get('mean_recall')}  precision={r.get('mean_precision')}  fpr={r.get('mean_fpr')}  coverage={r.get('mean_coverage')}")
    g = agg["generation"]
    print(f"  Generation  quality={g.get('mean_answer_quality')}  faithful={g.get('mean_faithfulness')}  %correct={g.get('pct_correct')}")
    p = agg["performance"]
    print(f"  Performance latency={p.get('mean_latency_ms')}ms  tokens={p.get('mean_total_tokens')}  cost={p.get('mean_cost_usd')}$  cost/correct={p.get('cost_per_correct_usd')}$")
    s = agg["stability"]
    print(f"  Stability   variance={s.get('mean_variance')}  consistency={s.get('mean_consistency')}")
    print(f"  Judge cost  {agg['total_judge_cost_usd']}$")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arch", default="baseline", help="Architecture name (used in output filename)")
    parser.add_argument("--runs", type=int, default=5, help="Number of runs per question")
    args = parser.parse_args()

    evaluate(arch_name=args.arch, n_runs=args.runs)
