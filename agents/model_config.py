from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(REPO_ROOT / ".env")

DEFAULT_FALLBACK_MODEL = "openrouter:tencent/hy3:free"
OMNIROUTE_BASE_URL = "http://127.0.0.1:20128/v1"
OMNIROUTE_MODEL = "auto"


def omniroute_enabled() -> bool:
    return bool(os.getenv("OMNIROUTE_API_KEY", "").strip())


def model_label() -> str:
    if omniroute_enabled():
        return f"omniroute:{OMNIROUTE_MODEL} ({OMNIROUTE_BASE_URL})"
    return DEFAULT_FALLBACK_MODEL


def workshop_model():
    api_key = os.getenv("OMNIROUTE_API_KEY", "").strip()
    if api_key:
        return ChatOpenAI(
            model=OMNIROUTE_MODEL,
            api_key=api_key,
            base_url=OMNIROUTE_BASE_URL,
            temperature=0,
        )
    return DEFAULT_FALLBACK_MODEL
