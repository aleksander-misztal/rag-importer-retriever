import logging
from typing import Any
from langchain_openai import ChatOpenAI
from shared.interfaces.llm import LLMProvider

logger = logging.getLogger(__name__)


class OpenAILLMProvider(LLMProvider):
    """OpenAI LLM provider implementation (GPT-4, GPT-4o, etc.)."""

    def __init__(self, api_key: str):
        self._api_key = api_key
        logger.info("✅ OpenAI LLM provider initialized")

    def invoke(self, prompt: str, **kwargs: Any) -> str:
        """Invokes LLM with prompt and returns response text."""
        try:
            llm = ChatOpenAI(openai_api_key=self._api_key, **kwargs)
            response = llm.invoke(prompt)
            return str(response.content)
        except Exception as e:
            logger.error(f"LLM invocation error: {e}")
            raise
