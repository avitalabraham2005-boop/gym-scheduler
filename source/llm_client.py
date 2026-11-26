"""הגדרה מרכזית של לקוח ה-LLM ושם המודל עבור המערכת."""

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)
load_dotenv()

GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_MODEL: str = "gemini-3.5-flash"
OPENAI_MODEL: str = "gpt-5.6-luna"

PROVIDER: str = (os.getenv("LLM_PROVIDER") or "gemini").strip().lower()

if PROVIDER == "openai":
    MODEL: str = OPENAI_MODEL
    _API_KEY_ENV: str = "OPENAI_API_KEY"
    _BASE_URL: str | None = None
else:
    MODEL = GEMINI_MODEL
    _API_KEY_ENV = "GEMINI_API_KEY"
    _BASE_URL = GEMINI_BASE_URL


def get_client() -> OpenAI:
    """יוצר ומחזיר לקוח OpenAI מוגדר לפי הספק הפעיל במשתני הסביבה."""
    api_key = os.getenv(_API_KEY_ENV)
    if not api_key:
        raise RuntimeError(f"Missing API key environment variable: {_API_KEY_ENV}")
    if _BASE_URL:
        return OpenAI(api_key=api_key, base_url=_BASE_URL)
    return OpenAI(api_key=api_key)
