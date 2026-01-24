import logging
from typing import Any
from state import GraphState
from prompts import GENERATOR_PROMPT

logger = logging.getLogger(__name__)


def generator_node(state: GraphState) -> dict[str, Any]:
    question = state["question"]
    llm = state["models"]["fast"]

    prompt = GENERATOR_PROMPT.format(question=question)

    try:
        response = llm.invoke(prompt)
        queries = [q.strip() for q in response.content.split("\n") if q.strip()]
        queries.append(question)
        logger.debug(f"Wygenerowano {len(queries)} wariantów zapytania")
    except Exception as e:
        logger.error(f"Błąd generowania zapytań: {e}")
        queries = [question]

    return {"sub_queries": queries}
