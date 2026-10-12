import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI


PROJECT_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = PROJECT_DIR.parent
DEFAULT_OPENAI_MODEL = "gpt-5.6-luna"
DEFAULT_PORTKEY_BASE_URL = "https://api.portkey.ai/v1"


@dataclass(frozen=True)
class Settings:
    portkey_api_key: str
    model_name: str
    portkey_base_url: str
    portkey_provider: str | None
    portkey_config_id: str | None


def load_settings(model_override: str | None = None) -> Settings:
    # A project .env wins; otherwise fall back to the shared workspace .env.
    load_dotenv(PROJECT_DIR / ".env")
    load_dotenv(WORKSPACE_DIR / ".env")
    api_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise RuntimeError(
            "PORTKEY_API_KEY is missing. Add it to the workspace .env or this project's .env."
        )

    return Settings(
        portkey_api_key=api_key,
        model_name=model_override or os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
        portkey_base_url=os.getenv("PORTKEY_BASE_URL", DEFAULT_PORTKEY_BASE_URL),
        portkey_provider=os.getenv("PORTKEY_PROVIDER"),
        portkey_config_id=os.getenv("PORTKEY_CONFIG_ID"),
    )


def build_portkey_client(settings: Settings) -> AsyncOpenAI:
    headers = {"x-portkey-api-key": settings.portkey_api_key}
    if settings.portkey_provider:
        headers["x-portkey-provider"] = settings.portkey_provider
    if settings.portkey_config_id:
        headers["x-portkey-config"] = settings.portkey_config_id

    return AsyncOpenAI(
        api_key=settings.portkey_api_key,
        base_url=settings.portkey_base_url,
        default_headers=headers,
    )
