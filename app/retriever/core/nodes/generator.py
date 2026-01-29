import logging
from shared.interfaces.llm import LLMProvider
from shared.interfaces.prompts import PromptProvider
from retriever.core.state import GraphState

logger = logging.getLogger(__name__)


class GeneratorNode:
    """Generates multiple query variants for better retrieval"""

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
            queries = [q.strip() for q in response.split("\n") if q.strip()]
            queries.append(question)
            logger.debug(f"Generated {len(queries)} query variants")
        except Exception as e:
            logger.error(f"Query generation error: {e}")
            queries = [question]

        return {"sub_queries": queries}
