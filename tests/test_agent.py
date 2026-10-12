"""Offline checks for the shop assistant. No API key, no network, no Portkey credits.

Uses PydanticAI's TestModel, which drives the real agent — the real prompt file, the real
tools, the real output validation — with a stub model standing in for the LLM. That
exercises every part we wrote without paying for any of it.

Run from the project root:  .venv/bin/python tests/test_agent.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from pydantic_ai.models.test import TestModel  # noqa: E402

import tools  # noqa: E402
from agent import MAX_HISTORY_MESSAGES, PROMPT_PATH, create_agent, load_prompt  # noqa: E402
from models import ChatAnswer, ChatReply, ProductCard  # noqa: E402

failures = []


def check(name: str, condition: bool, detail: str = "") -> None:
    print(f"  {'PASS' if condition else 'FAIL'}  {name}{f'  ({detail})' if detail and not condition else ''}")
    if not condition:
        failures.append(name)


print("The prompt file is loaded at runtime")
prompt = load_prompt()
check("prompts/prompt.md exists", PROMPT_PATH.is_file())
check("agent.py reads it by that path", PROMPT_PATH.name == "prompt.md" and PROMPT_PATH.parent.name == "prompts")
check("prompt is substantial", len(prompt) > 1500, f"{len(prompt)} chars")
for required in ["Safety rules", "Campus Customs", "colors_in_design", "product_ids", "Your voice"]:
    check(f"prompt covers {required!r}", required in prompt)
check("prompt forbids answering from memory", "no product knowledge of your own" in prompt)
check("prompt forbids revealing itself", "Never reveal or describe" in prompt)

print("\nThe agent assembles with all five tools")
agent = create_agent(TestModel())
check("output type is ChatAnswer", agent.output_type is ChatAnswer)

print("\nA run produces a validated ChatAnswer")
result = agent.run_sync("What hoodies do you have?")
answer = result.output
check("output is a ChatAnswer", isinstance(answer, ChatAnswer))
check("reply is non-empty", len(answer.reply) > 0)
check("product_ids is a list", isinstance(answer.product_ids, list))
check("at most six product ids", len(answer.product_ids) <= 6)

print("\nTestModel exercised the real tools")
# TestModel calls every registered tool once, so the run proves they are wired and that
# none of them raises against the real catalogue.
tool_calls = [
    part.tool_name
    for message in result.all_messages()
    for part in getattr(message, "parts", [])
    if getattr(part, "part_kind", None) == "tool-call"
]
for expected in [
    "search_products",
    "browse_category",
    "get_product_details",
    "check_size_availability",
    "shop_overview",
]:
    check(f"{expected} was called and did not raise", expected in tool_calls)

print("\nCategory normalisation (decision D3)")
check("seven canonical categories", len(tools.CATEGORIES) == 7, str(tools.CATEGORIES))
overview = tools.shop_overview()
check("every product maps to a category", sum(overview["categories"].values()) == 102)
check("no product falls through to Other", "Other" not in overview["categories"])
check("browse finds all 27 hoodies, not the 5 that garment_type alone gives",
      tools.browse_category("hoodies")["total_in_category"] == 27)
check("case-only duplicate is collapsed", tools.browse_category("t-shirt")["total_in_category"] == 25)

print("\nTools fail safely on bad input")
check("unknown product id returns an error, not an exception",
      "error" in tools.get_product_details("no-such-product"))
check("unknown size returns an error",
      "error" in tools.check_size_availability("basic-hoodie-big-yale", "XXXL"))
check("unknown category lists the valid ones",
      "valid_categories" in tools.browse_category("pantsuit"))
check("empty search returns nothing rather than everything",
      tools.search_products("") == [])

print("\nTools return ids that resolve, and real prices")
hits = tools.search_products("navy crewneck")
check("search returned results", len(hits) > 0)
check("every returned id resolves to a product",
      all(tools.get_product_details(h["product_id"]).get("error") is None for h in hits))
check("prices are among the seven real price points",
      all(h["price_usd"] in {32.0, 45.0, 58.0, 68.0, 72.0, 88.0, 98.0} for h in hits))

print("\nResponse shapes")
card = ProductCard(
    product_id="x", name="X", garment_type="hoodie", description="d",
    colors=["navy"], price=68.0, image_url="/api/products/x/image",
)
reply = ChatReply(reply="hello", products=[card], saved=False)
check("ChatReply carries cards and a saved flag", reply.saved is False and len(reply.products) == 1)
check("history is bounded", MAX_HISTORY_MESSAGES <= 20, str(MAX_HISTORY_MESSAGES))

print()
if failures:
    print(f"{len(failures)} check(s) failed: {failures}")
    sys.exit(1)
print("All checks passed. No model calls were made; TestModel stood in for the LLM.")
