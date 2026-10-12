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
from models import (  # noqa: E402
    ChatAnswer, ChatReply, LookupError, ProductCard, ProductDetails, ProductLookup,
)

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
for required in ["Safety rules", "Campus Customs", "colors_in_design", "product_ids", "Your voice",
                 "Your tools, and when to call them", "find_products_by_price"]:
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
    "find_products_by_price",
    "shop_overview",
]:
    check(f"{expected} was called and did not raise", expected in tool_calls)

print("\nCategory normalisation (decision D3)")
check("seven canonical categories", len(tools.CATEGORIES) == 7, str(tools.CATEGORIES))
overview = tools.shop_overview()
check("every product maps to a category", sum(overview.products_per_category.values()) == 102)
check("no product falls through to Other", "Other" not in overview.products_per_category)
check("browse finds all 27 hoodies, not the 5 that garment_type alone gives",
      tools.browse_category("hoodies").total_in_category == 27)
check("case-only duplicate is collapsed", tools.browse_category("t-shirt").total_in_category == 25)

print("\nTools fail safely on bad input")
check("unknown product id returns a LookupError, not an exception",
      isinstance(tools.get_product_details("no-such-product"), LookupError))
check("unknown size returns a LookupError",
      isinstance(tools.check_size_availability("basic-hoodie-big-yale", "XXXL"), LookupError))
check("unknown category returns a LookupError naming the valid ones",
      isinstance(tools.browse_category("pantsuit"), LookupError))
check("price search with no bounds returns a LookupError",
      isinstance(tools.find_products_by_price(), LookupError))
check("every LookupError carries a suggestion",
      all(e.suggestion for e in [
          tools.get_product_details("x"), tools.check_size_availability("basic-hoodie-big-yale", "Q"),
          tools.browse_category("pantsuit"), tools.find_products_by_price()]))
check("empty search returns nothing rather than everything",
      tools.search_products("") == [])

print("\nTools return typed results, resolvable ids, and real prices")
hits = tools.search_products("navy crewneck")
check("search returns ProductLookup objects", all(isinstance(h, ProductLookup) for h in hits))
check("every returned id resolves to a product",
      all(isinstance(tools.get_product_details(h.product_id), ProductDetails) for h in hits))
check("prices are among the seven real price points",
      all(h.price_usd in {32.0, 45.0, 58.0, 68.0, 72.0, 88.0, 98.0} for h in hits))

print("\nStock lookups agree with the database (no invented quantities)")
import sqlite3  # noqa: E402
con = sqlite3.connect(f"file:{ROOT.parent / 'data hw4' / 'campus_customs.db'}?mode=ro", uri=True)
truth = {
    (pid, size): qty
    for pid, size, qty in con.execute("select product_id, size, quantity from inventory")
}
sample = ["crew-left-chest-hoodie", "champion-reverse-weave-crewneck", "basic-hoodie-big-yale"]
mismatches = []
for pid in sample:
    details = tools.get_product_details(pid)
    for entry in details.sizes:
        if truth[(pid, entry.size)] != entry.quantity:
            mismatches.append((pid, entry.size))
    for size in details.sizes_out_of_stock:
        if truth[(pid, size)] != 0:
            mismatches.append((pid, size, "claimed out but is not"))
    for size in details.sizes_in_stock:
        if truth[(pid, size)] == 0:
            mismatches.append((pid, size, "claimed in stock but is not"))
check("every quantity matches inventory exactly", not mismatches, str(mismatches))
check("derived in/out lists partition all six sizes",
      all(len(tools.get_product_details(p).sizes_in_stock) + len(tools.get_product_details(p).sizes_out_of_stock) == 6
          for p in sample))
one = tools.check_size_availability("crew-left-chest-hoodie", "M")
check("a zero-quantity size reports in_stock False", one.in_stock is False and one.quantity == 0)
check("an out-of-stock answer offers real alternatives",
      all(truth[("crew-left-chest-hoodie", s)] > 0 for s in one.other_sizes_in_stock))

print("\nPrice filtering happens in the tool, not in the model")
cheap = tools.find_products_by_price(max_price_usd=50)
check("every result is within the bound", all(p.price_usd <= 50 for p in cheap.products))
check("total_matching counts beyond what is shown", cheap.total_matching >= len(cheap.products))
banded = tools.find_products_by_price(min_price_usd=60, max_price_usd=75)
check("a band excludes both ends correctly",
      all(60 <= p.price_usd <= 75 for p in banded.products))

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
