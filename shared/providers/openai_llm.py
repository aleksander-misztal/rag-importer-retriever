import logging
from typing import Any
from langchain_openai import ChatOpenAI
from shared.interfaces.llm import LLMProvider

logger = logging.getLogger(__name__)


class OpenAILLMProvider(LLMProvider):
    """OpenAI LLM provider — reuses ChatOpenAI instances per (model, settings) key."""

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._clients: dict[tuple, ChatOpenAI] = {}
        logger.info("OpenAI LLM provider initialized")

    def invoke(self, prompt: str, **kwargs: Any) -> str:
        cache_key = tuple(sorted(kwargs.items()))
        if cache_key not in self._clients:
            self._clients[cache_key] = ChatOpenAI(openai_api_key=self._api_key, **kwargs)
        response = self._clients[cache_key].invoke(prompt)
        return str(response.content)
