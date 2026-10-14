"""The Campus Customs shop assistant, as a PydanticAI agent.

Wiring only. The instructions live in `prompts/prompt.md` and are read at runtime; the
tools live in `tools.py`; the output shape lives in `models.py`. Nothing in this file
decides what the assistant says.

The model is reached through Portkey, using the key loaded by `app_config.py`. The key is
read server-side and never leaves this process.
"""
from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.usage import UsageLimits

from app_config import DEFAULT_OPENAI_MODEL, build_portkey_client, load_settings
from db import get_product, list_products
from models import ChatAnswer, ShopperContext
from tools import CATALOGUE_TOOLS

HERE = Path(__file__).resolve().parent
PROMPT_PATH = HERE / "prompts" / "prompt.md"

# Christine's standing instruction (2026-10-12): stay on gpt-5.6-luna. It is the cheap
# model and a full day of building HW4 cost about $0.008 on it. There is deliberately no
# fallback and no escalation path here — switching to a stronger model for "harder steps"
# is a decision she makes, not something the code does on its own.

# Everything replayed into the model is re-sent and re-paid on every turn, so the agent
# sees a bounded slice of the conversation rather than its whole history.
MAX_HISTORY_MESSAGES = 10

# Latency settings (Problem 9). The shopper was waiting around five seconds per message.
#
# `openai_reasoning_effort` is the big one: these models reason internally before
# answering, and that is most of the "thinking" pause. This assistant's job is
# lookup-and-report — the tools do the counting, filtering and price comparison in
# Python — so it does not need a large reasoning budget to be correct.
#
# Nothing here touches accuracy: the grounding rules, the safety section and the
# requirement to read every price and stock figure from a tool are unchanged, and the
# test suite is re-run after the change to confirm it.
LATENCY_SETTINGS = OpenAIResponsesModelSettings(
    openai_reasoning_effort="low",
    # Replies are a few sentences; the cap stops a runaway answer costing time and money.
    max_tokens=800,
    # Several lookups in one turn go out together rather than one after another.
    parallel_tool_calls=True,
)

# Hard limits on a single turn, enforced by PydanticAI rather than by the instructions.
#
# A tool-calling loop can in principle keep going: call a tool, read the result, decide it
# needs another, repeat. The instructions ask for restraint; this makes it a rule. A
# normal turn is two or three model requests and one to three tool calls, so these ceilings
# are roughly double the usual and are only reached by something that has gone wrong.
#
# Exceeding one raises `UsageLimitExceeded`, which the chat route turns into an honest
# "I could not work that out" rather than an endless, billable loop.
LOOP_LIMITS = UsageLimits(
    request_limit=6,       # model calls per shopper message
    tool_calls_limit=10,   # database lookups per shopper message
    total_tokens_limit=40_000,
)


@lru_cache(maxsize=1)
def known_prices() -> frozenset[float]:
    """Every price the shop charges. The catalogue has seven; anything else is wrong."""
    return frozenset(p.price for p in list_products())


def load_prompt() -> str:
    """Read the system prompt from disk. Not cached, so editing the file during
    development takes effect on the next request rather than needing a restart."""
    return PROMPT_PATH.read_text(encoding="utf-8")


def create_agent(model) -> Agent[ShopperContext, ChatAnswer]:
    """Assemble the agent around a given model.

    Separate from `build_agent` so tests can pass PydanticAI's `TestModel` and exercise
    the whole wiring — prompt, tools, output validation — without an API key and without
    spending a single credit.
    """
    agent = Agent(
        model,
        deps_type=ShopperContext,
        output_type=ChatAnswer,
        instructions=load_prompt,  # re-read per run, so prompt edits land immediately
        retries=2,
        model_settings=LATENCY_SETTINGS,
    )

    @agent.output_validator
    def grounded_in_the_catalogue(answer: ChatAnswer) -> ChatAnswer:
        """Machine-check the answer against the database before the shopper sees it.

        The instructions tell the agent to read every fact from a tool. This enforces it
        rather than trusting it: if the answer fails, `ModelRetry` sends it back to fix
        its own mistake, with the reason. Nothing unverified reaches the page.

        Two checks, both cheap and high-precision:

        1. **Every product id must exist.** An invented id would otherwise be silently
           dropped, leaving a reply that talks about a product with no card beside it.
        2. **Every price quoted with cents must be a real catalogue price.** The
           catalogue has exactly seven price points, so `$71.00` is provably wrong. Only
           amounts written with cents are checked, because the instructions require
           quoted prices to carry them while ranges ("under $50") do not — so a bound a
           shopper asked about is never mistaken for a claimed price.
        """
        unknown = [pid for pid in answer.product_ids if get_product(pid) is None]
        if unknown:
            raise ModelRetry(
                f"These product ids do not exist: {', '.join(unknown)}. "
                "Use only ids returned by a tool in this conversation, and call a tool "
                "again if you need them."
            )

        real_prices = {f"{p:.2f}" for p in known_prices()}
        quoted = set(re.findall(r"\$(\d+\.\d{2})", answer.reply))
        invented = sorted(quoted - real_prices)
        if invented:
            raise ModelRetry(
                f"You quoted {', '.join('$' + p for p in invented)}, which is not a "
                "price this shop charges. Call get_product_details and quote the "
                "price_usd it returns."
            )

        return answer

    @agent.instructions
    def shopper_context(ctx: RunContext[ShopperContext]) -> str:
        """Who is chatting and what they are looking at, rebuilt on every run.

        This is the deps pattern: the context is passed into `agent.run(deps=...)` and
        rendered here, rather than being concatenated onto the shopper's message. That
        keeps it out of the saved conversation and out of anything the shopper can
        overwrite by typing.
        """
        # A run without deps is treated as an anonymous visitor rather than failing.
        # The safe default is "we know nothing about you", never a crash mid-chat.
        return (ctx.deps or ShopperContext()).as_instructions()

    # Tools read the catalogue and cost nothing to call. The model may call several in
    # one turn; each is a database read, not a model call.
    for tool in CATALOGUE_TOOLS:
        agent.tool_plain(tool)

    return agent


@lru_cache(maxsize=1)
def build_agent() -> Agent[ShopperContext, ChatAnswer]:
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
