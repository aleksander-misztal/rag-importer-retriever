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


OPENAI_API_KEY = super_clean(os.getenv("OPENAI_API_KEY"))

LANGFUSE_PUBLIC_KEY = super_clean(os.getenv("LANGFUSE_PUBLIC_KEY"))
LANGFUSE_SECRET_KEY = super_clean(os.getenv("LANGFUSE_SECRET_KEY"))

raw_host = os.getenv("LANGFUSE_HOST", "http://localhost:3000")
if "langfuse" in raw_host and "localhost" not in raw_host:
    LANGFUSE_HOST = "http://localhost:3000"
else:
    LANGFUSE_HOST = raw_host

DB_USER = super_clean(os.getenv("DB_USER", "postgres"))
DB_PASS = super_clean(os.getenv("DB_PASSWORD", "postgres"))
DB_NAME = super_clean(os.getenv("DB_NAME", "postgres"))
DB_PORT = super_clean(os.getenv("DB_PORT", "5435"))
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@localhost:{DB_PORT}/{DB_NAME}"
COLLECTION_NAME = "study_docs"
