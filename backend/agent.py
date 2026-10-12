"""The Campus Customs shop assistant, as a PydanticAI agent.

Wiring only. The instructions live in `prompts/prompt.md` and are read at runtime; the
tools live in `tools.py`; the output shape lives in `models.py`. Nothing in this file
decides what the assistant says.

The model is reached through Portkey, using the key loaded by `app_config.py`. The key is
read server-side and never leaves this process.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

from app_config import DEFAULT_OPENAI_MODEL, build_portkey_client, load_settings
from models import ChatAnswer
from tools import (
    browse_category,
    check_size_availability,
    find_products_by_price,
    get_product_details,
    search_products,
    shop_overview,
)

HERE = Path(__file__).resolve().parent
PROMPT_PATH = HERE / "prompts" / "prompt.md"

# Christine's standing instruction (2026-10-12): stay on gpt-5.6-luna. It is the cheap
# model and a full day of building HW4 cost about $0.008 on it. There is deliberately no
# fallback and no escalation path here — switching to a stronger model for "harder steps"
# is a decision she makes, not something the code does on its own.

# Everything replayed into the model is re-sent and re-paid on every turn, so the agent
# sees a bounded slice of the conversation rather than its whole history.
MAX_HISTORY_MESSAGES = 10


def load_prompt() -> str:
    """Read the system prompt from disk. Not cached, so editing the file during
    development takes effect on the next request rather than needing a restart."""
    return PROMPT_PATH.read_text(encoding="utf-8")


def create_agent(model) -> Agent[None, ChatAnswer]:
    """Assemble the agent around a given model.

    Separate from `build_agent` so tests can pass PydanticAI's `TestModel` and exercise
    the whole wiring — prompt, tools, output validation — without an API key and without
    spending a single credit.
    """
    agent = Agent(
        model,
        output_type=ChatAnswer,
        instructions=load_prompt,  # re-read per run, so prompt edits land immediately
        retries=2,
    )

    # Tools read the catalogue and cost nothing to call. The model may call several in
    # one turn; each is a database read, not a model call.
    for tool in (
        search_products,
        browse_category,
        get_product_details,
        check_size_availability,
        find_products_by_price,
        shop_overview,
    ):
        agent.tool_plain(tool)

    return agent


@lru_cache(maxsize=1)
def build_agent() -> Agent[None, ChatAnswer]:
    """The production agent, constructed once per process.

    `gpt-6-luna` and friends reject tool definitions on the chat-completions endpoint, so
    this uses the Responses API, which handles tool calling across the 5.6 and 6 series.
    """
    settings = load_settings()
    return create_agent(
        OpenAIResponsesModel(
            settings.model_name,
            provider=OpenAIProvider(openai_client=build_portkey_client(settings)),
        )
    )


def model_name() -> str:
    """The model the agent will actually use.

    Resolved through `load_settings()` rather than reading the environment directly, so
    this cannot disagree with the agent — a project `.env` is only visible after
    `load_dotenv` has run, and reading `os.environ` before then would report the default
    while the agent used something else.
    """
    try:
        return load_settings().model_name
    except RuntimeError:
        # No key configured; report the default rather than failing a health check.
        return os.getenv("OPENAI_MODEL") or DEFAULT_OPENAI_MODEL
