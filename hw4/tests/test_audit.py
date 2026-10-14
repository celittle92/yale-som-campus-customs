"""Offline checks for the audit trail. No API key, no network, no credits.

The property that matters is append-only: an entry, once written, is never edited,
reordered or removed, and the file is valid JSON after every single write. These checks
assert that by comparing bytes before and after, not by trusting the implementation.

Everything here runs against a temporary file, so the real `output/audit_trail.json` is
never touched by the test suite.

Run from the project root:  .venv/bin/python tests/test_audit.py
"""
import json
import logging
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from pydantic_ai.models.test import TestModel  # noqa: E402

import audit  # noqa: E402
from agent import create_agent  # noqa: E402
from tools import CATALOGUE_TOOL_NAMES  # noqa: E402

failures = []


def check(name: str, condition: bool, detail: str = "") -> None:
    print(f"  {'PASS' if condition else 'FAIL'}  {name}{f'  ({detail})' if detail and not condition else ''}")
    if not condition:
        failures.append(name)


scratch = Path(tempfile.mkdtemp(prefix="audit-test-")) / "audit_trail.json"
real_path = audit.AUDIT_PATH
audit.AUDIT_PATH = scratch

print("The real trail is left alone")
check("tests write somewhere else", audit.AUDIT_PATH != real_path)

print("\nA fresh file")
check("starts empty", audit.entries() == [])
audit.record({"run": "aaaa1111", "event": "run", "stop_reason": "ok"})
check("one entry after one write", len(audit.entries()) == 1)
check("valid JSON array", isinstance(json.loads(scratch.read_text()), list))
check("the entry carries a timestamp", "at" in audit.entries()[0])
check("timestamp is UTC ISO", audit.entries()[0]["at"].endswith("Z"))

print("\nAppending never disturbs what is already there")
after_first = scratch.read_bytes()
first_entry = json.dumps(audit.entries()[0], sort_keys=True)
for index in range(1, 25):
    audit.record({"run": f"run{index:04d}", "event": "run", "stop_reason": "ok"})
    parsed = json.loads(scratch.read_text())  # must parse after *every* write
    if len(parsed) != index + 1:
        check(f"entry count after write {index}", False, f"{len(parsed)}")
        break
else:
    check("valid JSON after all 25 writes", True)
    check("entry count grew to 25", len(audit.entries()) == 25)

entries = audit.entries()
check("the first entry is byte-for-byte unchanged",
      json.dumps(entries[0], sort_keys=True) == first_entry)
# The bytes of the first entry still sit at the front of the file: only the closing
# bracket moved. Compare the prefix up to where the original entry ended.
prefix = after_first.split(b"\n]")[0]
check("the original bytes are still the start of the file", scratch.read_bytes().startswith(prefix))
check("order is preserved", [e["run"] for e in entries[1:]] == [f"run{i:04d}" for i in range(1, 25)])
check("nothing was dropped", entries[0]["run"] == "aaaa1111")

print("\nNothing personal reaches the file")
audit.record({
    "run": "bbbb2222",
    "event": "tool",
    "name": "search_products",
    "args": audit._short("query='mail me at shopper@example.com card 4111 1111 1111 1111'"),
})
written = audit.entries()[-1]["args"]
check("an email address is redacted", "@example.com" not in written and "[email]" in written)
check("a card-shaped number is redacted", "4111" not in written and "[digits]" in written)
check("the search term itself survives", "query=" in written)

long_value = audit._short("x" * 500)
check(f"long values are truncated to {audit.MAX_FIELD}", len(long_value) <= audit.MAX_FIELD)
check("truncation is marked", long_value.endswith("…"))

print("\nA real agent run is recorded, end to end")
# TestModel drives the real agent and calls every registered tool once, so this exercises
# the same reading path a live turn uses — without a model call.
before = len(audit.entries())
result = create_agent(TestModel()).run_sync("What hoodies do you have?")
audit.record_exchange(
    "cccc3333",
    stop_reason="ok",
    signed_in=False,
    question_chars=len("What hoodies do you have?"),
    ms=42,
    result=result,
)
added = audit.entries()[before:]
tool_entries = [e for e in added if e.get("event") == "tool"]
run_entries = [e for e in added if e.get("event") == "run"]

check("tool calls were recorded", len(tool_entries) >= 6, f"{len(tool_entries)}")
check("each tool entry names a tool", all(e.get("name") for e in tool_entries))
# PydanticAI delivers the answer through an internal `final_result` tool whose arguments
# are the reply itself. It must never reach the trail, or the reply text comes with it.
check("only catalogue tools are recorded",
      {e["name"] for e in tool_entries} <= set(CATALOGUE_TOOL_NAMES),
      str({e["name"] for e in tool_entries} - set(CATALOGUE_TOOL_NAMES)))
check("the output tool never appears", "final_result" not in scratch.read_text())
check("each tool entry has args and a result", all("args" in e and "result" in e for e in tool_entries))
check("exactly one run entry", len(run_entries) == 1)

run_entry = run_entries[0]
check("the run entry carries the stop reason", run_entry["stop_reason"] == "ok")
check("it counts the tool calls", run_entry["tools_called"] == len(tool_entries))
check("it records duration", run_entry["ms"] == 42)
check("it records whether the shopper was signed in", run_entry["signed_in"] is False)
check("every entry shares the run id", all(e["run"] == "cccc3333" for e in added))

print("\nThe shopper's words are not in the trail")
whole_file = scratch.read_text()
check("the question text is absent", "What hoodies do you have?" not in whole_file)
check("only its length is kept", run_entry["question_chars"] == 25)
check("no user id or email field exists", not any(
    k in e for e in audit.entries() for k in ("user_id", "email", "name_of_user", "message", "reply")
))

print("\nFailures are recorded too, not just successes")
for reason in ("content_filter", "usage_limit", "model_error", "error"):
    audit.record_exchange(
        f"dddd{reason[:4]}", stop_reason=reason, signed_in=True, question_chars=10, ms=5
    )
reasons = [e.get("stop_reason") for e in audit.entries()]
for reason in ("content_filter", "usage_limit", "model_error", "error"):
    check(f"a {reason} turn is on the record", reason in reasons)
check("a failed turn still parses", isinstance(json.loads(scratch.read_text()), list))

print("\nA broken write never breaks a reply")
# The failure is the point of this check, so silence the traceback it logs.
logging.getLogger("campus_customs.audit").setLevel(logging.CRITICAL)
audit.AUDIT_PATH = Path("/nonexistent-directory-for-this-test/audit_trail.json")
try:
    audit.record({"run": "eeee5555", "event": "run"})
    check("record() swallows a write failure", True)
except Exception as error:  # noqa: BLE001
    check("record() swallows a write failure", False, str(error))
audit.AUDIT_PATH = scratch
logging.getLogger("campus_customs.audit").setLevel(logging.NOTSET)

print("\nThe real trail on disk, if it exists, is valid and only ever grew")
audit.AUDIT_PATH = real_path
if real_path.is_file():
    live = audit.entries()
    check("output/audit_trail.json parses", isinstance(live, list))
    check("every entry has a time and a run id", all("at" in e and "run" in e for e in live))
    check("timestamps are non-decreasing", all(
        live[i]["at"] <= live[i + 1]["at"] for i in range(len(live) - 1)
    ))
    print(f"  ({len(live)} entries recorded so far)")
else:
    print("  (no trail written yet; skipped)")

print()
if failures:
    print(f"{len(failures)} check(s) failed: {failures}")
    sys.exit(1)
print("All checks passed. No model calls were made; TestModel stood in for the LLM.")
