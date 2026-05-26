"""
LLM-as-a-judge for generation quality.

answer_quality scale (from thesis):
  0 — incorrect / doesn't answer
  1 — partially correct, incomplete or imprecise
  2 — mostly correct, minor omissions
  3 — fully correct, complete and precise

faithfulness:
  0 — hallucination detected (answer contains info not in context)
  1 — answer is fully grounded in the retrieved context

Answers with quality >= 2 are considered "correct" for cost_per_correct_answer.
"""

import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

CORRECTNESS_THRESHOLD = 2

JUDGE_PROMPT = """\
You are an expert evaluator of RAG (Retrieval-Augmented Generation) system outputs.

## Question
{question}

## Retrieved context (source chunks)
{context}

## System answer
{answer}

---

Evaluate the system answer on two dimensions:

1. **answer_quality** (integer 0–3):
   - 0: incorrect — does not answer the question or contains significant factual errors
   - 1: partially correct — contains correct elements but is incomplete or imprecise
   - 2: mostly correct — answers the question but omits some important information
   - 3: fully correct — complete, precise and consistent with the sources

2. **faithfulness** (integer 0 or 1):
   - 0: the answer contains information NOT present in the retrieved context (hallucination)
   - 1: the answer is fully grounded in the provided context

Respond ONLY with valid JSON, no explanation:
{{"answer_quality": <int>, "faithfulness": <int>}}"""


class GenerationJudge:
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model  = model

    def evaluate(
        self,
        question: str,
        answer: str,
        context: list[str],
    ) -> dict:
        context_text = "\n\n---\n\n".join(context) if context else "(no context retrieved)"
        prompt = JUDGE_PROMPT.format(
            question=question,
            context=context_text,
            answer=answer,
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content
            parsed = json.loads(raw)

            quality     = int(parsed.get("answer_quality", 0))
            faithfulness = int(parsed.get("faithfulness", 0))

            return {
                "answer_quality":  quality,
                "faithfulness":    faithfulness,
                "is_correct":      quality >= CORRECTNESS_THRESHOLD,
                "judge_model":     self.model,
                "input_tokens":    response.usage.prompt_tokens,
                "output_tokens":   response.usage.completion_tokens,
                "cost_usd":        self._cost(response.usage.prompt_tokens, response.usage.completion_tokens),
            }

        except Exception as e:
            logger.error(f"Judge error: {e}")
            return {
                "answer_quality":  None,
                "faithfulness":    None,
                "is_correct":      None,
                "judge_model":     self.model,
                "input_tokens":    0,
                "output_tokens":   0,
                "cost_usd":        0.0,
            }

    def _cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = {"gpt-4o": (2.50, 10.00), "gpt-4o-mini": (0.15, 0.60)}
        key = self.model if self.model in pricing else "gpt-4o"
        inp, out = pricing[key]
        return round(input_tokens * inp / 1_000_000 + output_tokens * out / 1_000_000, 8)


def aggregate_generation_metrics(per_question: list[dict]) -> dict:
    """Average answer_quality and faithfulness; compute % correct."""
    qualities    = [q["answer_quality"]  for q in per_question if q.get("answer_quality")  is not None]
    faithfulness = [q["faithfulness"]    for q in per_question if q.get("faithfulness")     is not None]
    correct      = [q["is_correct"]      for q in per_question if q.get("is_correct")       is not None]

    return {
        "mean_answer_quality":  round(sum(qualities)    / len(qualities),    4) if qualities    else None,
        "mean_faithfulness":    round(sum(faithfulness) / len(faithfulness), 4) if faithfulness else None,
        "pct_correct":          round(sum(correct)      / len(correct),      4) if correct      else None,
    }
