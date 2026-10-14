"""An append-only record of what the agent actually did.

Every chat turn writes one `run` entry with how it ended, preceded by one entry per tool
call the agent made and per validator retry it was sent back for. The file is
`output/audit_trail.json`, it is never cleared between runs, and nothing already written
is ever edited.

**How "append only" is enforced.** A JSON array cannot literally be appended to — the
closing bracket is in the way — so `_append` seeks to the end, truncates the `]` and the
whitespace before it, and writes the new entry followed by a fresh `]`. No byte belonging
to an existing entry is read back, rewritten or moved, and the file is valid JSON after
every write. There is no code path here that deletes, edits or reorders an entry.

**What is deliberately not recorded.** This file is committed to a public repository, so
it holds no shopper identity and no conversation text:

- not the shopper's message and not the assistant's reply — only the length of the
  question, which is enough to tell a greeting from an essay;
- not a name, an email or a user id — only whether the visitor was signed in;
- tool arguments are kept because they are the point of an audit trail, but they are
  truncated and run through a redactor first, so an email address or a card-shaped run of
  digits typed into chat cannot reach the file.
"""
from __future__ import annotations

import json
import logging
import os
import re
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools import CATALOGUE_TOOL_NAMES

logger = logging.getLogger("campus_customs.audit")

AUDIT_PATH = Path(__file__).resolve().parent.parent / "output" / "audit_trail.json"

# Arguments and result summaries are evidence, not a transcript. Long enough to show what
# was asked, short enough that the file stays readable after a few hundred turns.
MAX_FIELD = 120

# Anything shaped like contact or payment detail is removed before it is written. The
# agent has no reason to pass either to a tool; this is in case a shopper types one into
# a search box and the model echoes it into a query.
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_LONG_DIGITS = re.compile(r"\d(?:[\d \-]{9,})\d")

_LOCK = threading.Lock()


def _redact(text: str) -> str:
    text = _EMAIL.sub("[email]", text)
    return _LONG_DIGITS.sub("[digits]", text)


def _short(value: Any) -> str:
    """One compact, redacted line for an argument or a result."""
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    else:
        text = str(value)
    text = _redact(" ".join(text.split()))
    return text if len(text) <= MAX_FIELD else text[: MAX_FIELD - 1] + "…"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def new_run_id() -> str:
    """A short id tying one turn's entries together."""
    return uuid.uuid4().hex[:8]


def _append(entry: dict[str, Any]) -> None:
    """Add one entry to the array without touching the entries already in it."""
    line = json.dumps(entry, ensure_ascii=False)
    with _LOCK:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not AUDIT_PATH.exists() or AUDIT_PATH.stat().st_size == 0:
            AUDIT_PATH.write_text(f"[\n  {line}\n]\n", encoding="utf-8")
            return

        with AUDIT_PATH.open("r+b") as handle:
            handle.seek(0, os.SEEK_END)
            cut = handle.tell()

            # Walk back to the array's closing bracket, over trailing whitespace only.
            while cut > 0:
                handle.seek(cut - 1)
                char = handle.read(1)
                if char == b"]":
                    cut -= 1
                    break
                if char not in b" \t\r\n":
                    raise ValueError("audit_trail.json does not end in a JSON array")
                cut -= 1
            else:
                raise ValueError("audit_trail.json has no closing bracket")

            # And back again over the whitespace before it, so the new entry lands on the
            # line after the previous one rather than after a stray blank line.
            while cut > 0:
                handle.seek(cut - 1)
                if handle.read(1) not in b" \t\r\n":
                    break
                cut -= 1

            handle.seek(cut - 1)
            opening = handle.read(1) == b"["  # an empty array takes no leading comma
            handle.seek(cut)
            handle.truncate()
            separator = b"\n  " if opening else b",\n  "
            handle.write(separator + line.encode("utf-8") + b"\n]\n")


def record(entry: dict[str, Any]) -> None:
    """Write one entry, and never let the audit trail break a reply."""
    try:
        _append({"at": _now(), **entry})
    except Exception:  # noqa: BLE001 - a missing audit line is better than a 500
        logger.exception("could not write to the audit trail")


def record_exchange(
    run_id: str,
    *,
    stop_reason: str,
    signed_in: bool,
    question_chars: int,
    ms: int,
    result: Any = None,
) -> None:
    """Record one agent loop: each tool call and retry, then how the run ended.

    The tool calls are read back out of `result.new_messages()` rather than captured by
    wrapping the tool functions. Reading afterwards cannot change what the agent does, and
    it cannot disturb the signatures PydanticAI builds its tool schemas from — which
    wrapping would risk. `new_messages()` rather than `all_messages()`, so replayed
    history is not re-audited on every turn.
    """
    tools_called = 0
    retries = 0

    if result is not None:
        pending: dict[str, Any] = {}
        try:
            messages = result.new_messages()
        except Exception:  # noqa: BLE001
            messages = []
        for message in messages:
            for part in getattr(message, "parts", []):
                kind = getattr(part, "part_kind", "")
                if kind == "tool-call":
                    pending[getattr(part, "tool_call_id", "")] = part
                elif kind == "tool-return":
                    call = pending.pop(getattr(part, "tool_call_id", ""), None)
                    # PydanticAI delivers the agent's own answer through an internal
                    # `final_result` tool. Skip it: it is not a catalogue lookup, and its
                    # arguments *are* the reply, which this file does not keep.
                    if part.tool_name not in CATALOGUE_TOOL_NAMES:
                        continue
                    tools_called += 1
                    record(
                        {
                            "run": run_id,
                            "event": "tool",
                            "name": part.tool_name,
                            "args": _short(getattr(call, "args", "")) if call else "",
                            "result": _short(part.content),
                        }
                    )
                elif kind == "retry-prompt":
                    retries += 1
                    record(
                        {
                            "run": run_id,
                            "event": "retry",
                            "name": getattr(part, "tool_name", None) or "output_validator",
                            "result": _short(part.content),
                        }
                    )

    entry: dict[str, Any] = {
        "run": run_id,
        "event": "run",
        "signed_in": signed_in,
        "question_chars": question_chars,
        "tools_called": tools_called,
        "retries": retries,
        "stop_reason": stop_reason,
        "ms": ms,
    }

    usage = getattr(result, "usage", None)
    if usage is not None:
        entry["requests"] = getattr(usage, "requests", None)
        entry["tokens"] = getattr(usage, "total_tokens", None)

    record(entry)


def entries() -> list[dict[str, Any]]:
    """The whole trail, for tests and for reading it back."""
    if not AUDIT_PATH.exists() or AUDIT_PATH.stat().st_size == 0:
        return []
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
