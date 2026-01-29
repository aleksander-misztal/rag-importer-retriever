import logging
from shared.interfaces.llm import LLMProvider
from shared.interfaces.prompts import PromptProvider
from retriever.core.state import GraphState

logger = logging.getLogger(__name__)


class SecurityNode:
    """Validates question safety using LLM"""

    def __init__(self, llm: LLMProvider, prompt_provider: PromptProvider, settings: dict, prompt_name: str):
        self.llm = llm
        self.prompt_provider = prompt_provider
        self.settings = settings
        self.prompt_name = prompt_name

    def __call__(self, state: GraphState) -> dict:
        question = state["question"]

        template = self.prompt_provider.get_prompt(self.prompt_name)
        prompt = template.format(question=question)

        try:
            response = self.llm.invoke(prompt, **self.settings)
            result = response.strip().upper()
            is_safe = "SAFE" in result
        except Exception as e:
            logger.error(f"Security validation error: {e}")
            is_safe = False

        if not is_safe:
            logger.warning(f"Rejected question: {question[:50]}...")
            return {
                "is_safe": False,
                "answer": "Question rejected by security filter."
            }

        return {"is_safe": True}
