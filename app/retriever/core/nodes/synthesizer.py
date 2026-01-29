import logging
from shared.interfaces.llm import LLMProvider
from shared.interfaces.prompts import PromptProvider
from retriever.core.state import GraphState

logger = logging.getLogger(__name__)


class SynthesizerNode:
    """Synthesizes final answer from retrieved context"""

    def __init__(self, llm: LLMProvider, prompt_provider: PromptProvider, settings: dict, prompt_name: str):
        self.llm = llm
        self.prompt_provider = prompt_provider
        self.settings = settings
        self.prompt_name = prompt_name

    def __call__(self, state: GraphState) -> dict:
        context = "\n---\n".join(state["context"])
        question = state["question"]

        if not state["context"]:
            return {"answer": "No relevant materials found in knowledge base."}

        template = self.prompt_provider.get_prompt(self.prompt_name)
        prompt = template.format(context=context, question=question)

        try:
            answer = self.llm.invoke(prompt, **self.settings)
            logger.debug(f"Generated answer ({len(answer)} chars)")
        except Exception as e:
            logger.error(f"Answer synthesis error: {e}")
            answer = "Error occurred during answer generation."

        return {"answer": answer}
