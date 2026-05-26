"""
Retrieval quality metrics.

All functions are pure — no I/O, no side effects.
"""


def compute_retrieval_metrics(
    retrieved_ids: list[str],
    ground_truth_ids: list[str],
    k: int,
) -> dict:
    """
    Compute Recall@k, Precision@k, FPR and Coverage for a single question.

    retrieved_ids   — ordered list of chunk_ids returned by the pipeline
    ground_truth_ids — chunk_ids that contain the correct answer
    k               — cut-off (evaluate only the first k retrieved ids)
    """
    retrieved_at_k = retrieved_ids[:k]
    retrieved_set  = set(retrieved_at_k)
    gt_set         = set(ground_truth_ids)

    if not gt_set:
        return {"recall": None, "precision": None, "fpr": None, "coverage": None, "k": k}

    correct = retrieved_set & gt_set

    recall    = len(correct) / len(gt_set)
    precision = len(correct) / len(retrieved_set) if retrieved_set else 0.0
    fpr       = (len(retrieved_set) - len(correct)) / len(retrieved_set) if retrieved_set else 0.0
    coverage  = 1 if correct == gt_set else 0

    return {
        "recall":    round(recall,    4),
        "precision": round(precision, 4),
        "fpr":       round(fpr,       4),
        "coverage":  coverage,
        "k":         k,
    }


def aggregate_retrieval_metrics(per_question: list[dict]) -> dict:
    """Average metrics across all questions (ignores None values)."""
    keys = ["recall", "precision", "fpr", "coverage"]
    result = {}
    for key in keys:
        values = [q[key] for q in per_question if q.get(key) is not None]
        result[f"mean_{key}"] = round(sum(values) / len(values), 4) if values else None
    return result
