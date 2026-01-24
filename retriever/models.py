from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY


def get_models() -> dict[str, ChatOpenAI]:
    if not OPENAI_API_KEY:
        raise ValueError("Brak klucza OPENAI_API_KEY")

    return {
        "fast": ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=OPENAI_API_KEY
        ),
        "smart": ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            openai_api_key=OPENAI_API_KEY
        )
    }
