import logging
import psycopg2
from psycopg2.extensions import connection
from config import DATABASE_URL

logger = logging.getLogger(__name__)


def get_connection() -> connection:
    return psycopg2.connect(DATABASE_URL)


def init_vector_db() -> None:
    try:
        with get_connection() as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        logger.info("Połączono z bazą, PGVector aktywny")
    except Exception as e:
        logger.error(f"Błąd połączenia z bazą: {e}")


def clear_all_data() -> str:
    try:
        with get_connection() as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("DELETE FROM langchain_pg_embedding;")
                cur.execute("DELETE FROM langchain_pg_collection;")
        logger.info("Baza wyczyszczona")
        return "Baza została wyczyszczona."
    except Exception as e:
        logger.error(f"Błąd czyszczenia: {e}")
        return f"Błąd czyszczenia: {e}"
