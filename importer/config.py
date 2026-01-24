import os
import re
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
env_path = os.path.join(parent_dir, '.env')

if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
        load_dotenv(stream=f, override=True)


def super_clean(text: str | None) -> str:
    if not text:
        return ""
    cleaned = re.sub(r'[^\x21-\x7E]', '', text)
    return cleaned.strip()


DB_USER: str = super_clean(os.getenv("DB_USER", "postgres"))
DB_PASS: str = super_clean(os.getenv("DB_PASSWORD", "postgres"))
DB_NAME: str = super_clean(os.getenv("DB_NAME", "postgres"))
DB_HOST: str = super_clean(os.getenv("DB_HOST", "localhost"))
DB_PORT: str = super_clean(os.getenv("DB_PORT", "5432"))

DATABASE_URL: str = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
OPENAI_API_KEY: str = super_clean(os.getenv("OPENAI_API_KEY"))
COLLECTION_NAME: str = "study_docs"
CHUNK_SIZE: int = 250
CHUNK_OVERLAP: int = 50
