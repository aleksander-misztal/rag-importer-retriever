import logging
from typing import Any
from state import GraphState
from prompts import SYNTHESIZER_PROMPT

logger = logging.getLogger(__name__)


def synthesizer_node(state: GraphState) -> dict[str, Any]:
    context = "\n---\n".join(state["context"])
    question = state["question"]
    llm = state["models"]["smart"]

    if not context:
        logger.warning("Brak kontekstu do syntezy odpowiedzi")
        return {"answer": "Nie znaleziono odpowiednich dokumentów w bazie wiedzy."}

    prompt = SYNTHESIZER_PROMPT.format(context=context, question=question)

    try:
        response = llm.invoke(prompt)
        answer = response.content
        logger.debug(f"Wygenerowano odpowiedź ({len(answer)} znaków)")
    except Exception as e:
        logger.error(f"Błąd generowania odpowiedzi: {e}")
        return {"answer": "Wystąpił błąd podczas generowania odpowiedzi."}

    return {"answer": answer}
