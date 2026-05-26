"""
Stability metrics across N runs of the same question.

variance    — variance of answer_quality scores across runs
              (high value = model is inconsistent)
consistency — fraction of runs that produced the same answer_quality as the mode
              (1.0 = all runs gave identical score)
"""


def _variance(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return round(sum((v - mean) ** 2 for v in values) / len(values), 6)


def _mode(values: list[int]) -> int:
    return max(set(values), key=values.count)


def compute_stability(run_generation_results: list[dict]) -> dict:
    """
    Input: list of generation dicts (one per run) for the same question.
    Each dict must have 'answer_quality' key (int or None).
    """
    qualities = [r["answer_quality"] for r in run_generation_results if r.get("answer_quality") is not None]

    if not qualities:
        return {"variance": None, "consistency": None, "n_valid_runs": 0}

    mode_val    = _mode(qualities)
    consistency = round(qualities.count(mode_val) / len(qualities), 4)
    variance    = _variance([float(q) for q in qualities])

    return {
        "variance":     variance,
        "consistency":  consistency,
        "n_valid_runs": len(qualities),
        "scores":       qualities,
    }


def aggregate_stability(per_question: list[dict]) -> dict:
    """Average variance and consistency across all questions."""
    variances     = [q["variance"]    for q in per_question if q.get("variance")    is not None]
    consistencies = [q["consistency"] for q in per_question if q.get("consistency") is not None]

    return {
        "mean_variance":     round(sum(variances)     / len(variances),     6) if variances     else None,
        "mean_consistency":  round(sum(consistencies) / len(consistencies), 4) if consistencies else None,
    }
