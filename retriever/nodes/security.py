import logging
from typing import Any
from state import GraphState
from prompts import SECURITY_PROMPT

logger = logging.getLogger(__name__)


def security_node(state: GraphState) -> dict[str, Any]:
    question = state["question"]
    llm = state["models"]["fast"]

    prompt = SECURITY_PROMPT.format(question=question)

    try:
        response = llm.invoke(prompt)
        result = response.content.strip().upper()
        is_safe = result == "BEZPIECZNE"
    except Exception as e:
        logger.error(f"Błąd walidacji bezpieczeństwa: {e}")
        is_safe = False

    if not is_safe:
        logger.warning(f"Odrzucono pytanie: {question[:50]}...")
        return {"is_safe": False, "answer": "Pytanie zostało odrzucone przez filtr bezpieczeństwa."}

    return {"is_safe": True}
