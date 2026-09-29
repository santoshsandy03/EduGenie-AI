import logging
import os

from dotenv import load_dotenv

load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = (os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite") or "gemini-3.1-flash-lite").strip()

USE_LOCAL_EXPLAIN_MODEL = os.getenv("USE_LOCAL_EXPLAIN_MODEL", "false").lower() == "true"

logger = logging.getLogger("EduGenie")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def is_configured() -> bool:
    return bool(GEMINI_API_KEY)
