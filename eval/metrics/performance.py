"""
Performance metrics: latency, token usage, cost, cost_per_correct_answer.
"""


def compute_performance(collector_summary: dict, total_latency_s: float) -> dict:
    """
    Build a performance record from MetricsCollector.summary() + wall-clock latency.
    """
    return {
        "latency_s":      round(total_latency_s, 4),
        "latency_ms":     round(total_latency_s * 1000, 1),
        "input_tokens":   collector_summary["input_tokens"],
        "output_tokens":  collector_summary["output_tokens"],
        "total_tokens":   collector_summary["total_tokens"],
        "cost_usd":       collector_summary["cost_usd"],
    }


def aggregate_performance_metrics(
    per_run: list[dict],
    correct_flags: list[bool | None],
) -> dict:
    """
    Aggregate latency, tokens, cost across runs.
    Compute cost_per_correct_answer (Ceff from thesis eq. 2.4).
    """
    latencies = [r["latency_ms"]    for r in per_run]
    tokens    = [r["total_tokens"]  for r in per_run]
    costs     = [r["cost_usd"]      for r in per_run]

    total_cost    = sum(costs)
    correct_count = sum(1 for f in correct_flags if f is True)

    return {
        "mean_latency_ms":        round(sum(latencies) / len(latencies), 1) if latencies else None,
        "mean_total_tokens":      round(sum(tokens)    / len(tokens),    1) if tokens    else None,
        "mean_cost_usd":          round(total_cost     / len(costs),     8) if costs     else None,
        "cost_per_correct_usd":   round(total_cost / correct_count, 8) if correct_count else None,
    }
