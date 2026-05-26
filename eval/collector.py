import time
import logging
from typing import Any
from langchain_core.callbacks import BaseCallbackHandler

logger = logging.getLogger(__name__)


class MetricsCollector(BaseCallbackHandler):
    """LangChain callback that intercepts LLM calls to collect token usage, cost and latency."""

    PRICING = {
        "gpt-4o":             {"input": 2.50  / 1_000_000, "output": 10.00 / 1_000_000},
        "gpt-4o-mini":        {"input": 0.15  / 1_000_000, "output": 0.60  / 1_000_000},
        "gpt-4o-2024-08-06":  {"input": 2.50  / 1_000_000, "output": 10.00 / 1_000_000},
        "gpt-4o-mini-2024-07-18": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
    }

    def __init__(self):
        super().__init__()
        self.llm_calls: list[dict] = []
        self._t_start: float | None = None

    def on_chat_model_start(self, serialized: dict, messages: list, **kwargs: Any) -> None:
        self._t_start = time.perf_counter()

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        elapsed = time.perf_counter() - (self._t_start or time.perf_counter())
        usage: dict = {}
        model: str = "unknown"

        if response.llm_output:
            usage = response.llm_output.get("token_usage", {})
            model = response.llm_output.get("model_name", "unknown")

        input_tokens  = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

        self.llm_calls.append({
            "model":         model,
            "latency_s":     round(elapsed, 4),
            "input_tokens":  input_tokens,
            "output_tokens": output_tokens,
            "cost_usd":      self._compute_cost(model, input_tokens, output_tokens),
        })

    # ------------------------------------------------------------------
    # Aggregation helpers
    # ------------------------------------------------------------------

    def total_input_tokens(self) -> int:
        return sum(c["input_tokens"] for c in self.llm_calls)

    def total_output_tokens(self) -> int:
        return sum(c["output_tokens"] for c in self.llm_calls)

    def total_tokens(self) -> int:
        return self.total_input_tokens() + self.total_output_tokens()

    def total_cost_usd(self) -> float:
        return round(sum(c["cost_usd"] for c in self.llm_calls), 8)

    def summary(self) -> dict:
        return {
            "input_tokens":  self.total_input_tokens(),
            "output_tokens": self.total_output_tokens(),
            "total_tokens":  self.total_tokens(),
            "cost_usd":      self.total_cost_usd(),
            "llm_calls":     self.llm_calls,
        }

    # ------------------------------------------------------------------

    def _compute_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        pricing = self.PRICING.get(model)
        if not pricing:
            # fallback: try prefix match
            for key in self.PRICING:
                if model.startswith(key):
                    pricing = self.PRICING[key]
                    break
        if not pricing:
            logger.warning(f"Unknown model for pricing: {model}")
            return 0.0
        return round(
            input_tokens * pricing["input"] + output_tokens * pricing["output"],
            8,
        )
