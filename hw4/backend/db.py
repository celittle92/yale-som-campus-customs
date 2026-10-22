"""Read-only access to the Campus Customs catalogue.

The database and the product images are not part of this repository: the assignment
forbids committing them. Point CAMPUS_CUSTOMS_DATA at the folder holding
``campus_customs.db`` and ``products/``, or keep the default layout described in the
README.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_NAME = "campus_customs.db"
IMAGE_DIR_NAME = "products"

# The supplied data sits outside the repository so it cannot be committed by accident,
# which means its location depends on where someone unpacked it. Rather than hard-code a
# number of levels to climb — which broke once already when the project moved a level
# deeper — look for it in each ancestor of the project folder, nearest first.
#
# "data" comes first because that is the folder name the assignment itself uses, so
# anyone who follows the layout in the brief lands on it immediately. "data hw4" is the
# name this workspace happens to use. The bare "." covers a database dropped straight
# into one of those folders.
DATA_DIR_NAMES = ("data", "data hw4", ".")
SEARCH_DEPTH = 3

# Size order is fixed by the catalogue; sorting alphabetically would read as L, M, S, XL.
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]


def _candidate_data_dirs() -> list[Path]:
    ancestors = [PROJECT_DIR, *PROJECT_DIR.parents[:SEARCH_DEPTH]]
    return [base / name for base in ancestors for name in DATA_DIR_NAMES]


@lru_cache(maxsize=1)
def data_dir() -> Path:
    configured = os.getenv("CAMPUS_CUSTOMS_DATA")
    if configured:
        candidates = [Path(configured).expanduser()]
    else:
        candidates = _candidate_data_dirs()

    for path in candidates:
        if (path / DB_NAME).is_file():
            return path.resolve()

    looked = "\n  ".join(str(p) for p in candidates)
    raise RuntimeError(
        f"{DB_NAME} not found. Set CAMPUS_CUSTOMS_DATA to the folder that holds "
        f"{DB_NAME} and {IMAGE_DIR_NAME}/. Looked in:\n  {looked}"
    )


def connect() -> sqlite3.Connection:
    """A read-only connection. The catalogue and inventory are never written."""
    con = sqlite3.connect(f"file:{data_dir() / DB_NAME}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def connect_rw() -> sqlite3.Connection:
    """A writable connection, used **only** for `users` and `chat_messages`.

    Accounts have to be written somewhere, and the assignment puts them in the supplied
    database. Catalogue and inventory reads still go through `connect()` above, so the
    product data cannot be modified even by accident.
    """
    con = sqlite3.connect(data_dir() / DB_NAME)
    con.row_factory = sqlite3.Row
    con.execute("pragma foreign_keys = on")
    return con


def _loads(raw: str | None) -> list[str]:
    """colors and search_tags are JSON arrays stored in TEXT columns."""
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except ValueError:
        return []
    return [str(v) for v in value] if isinstance(value, list) else []


# Three catalogue rows carry a generation failure instead of a description: the
# instructor's vision pass was refused by a content filter and fell back to a stub
# ("Vision blocked; filename-based stub"). They are the same three rows with an empty
# colors array. Showing that text to a shopper looks broken, so it is detected and
# replaced with an honest line — and the agent is told the description is missing
# rather than being handed a sentence that describes nothing.
_STUB_DESCRIPTION = re.compile(r"vision blocked|filename-based stub", re.IGNORECASE)
NO_DESCRIPTION = (
    "We have not written a description for this one yet — the photo is the best guide, "
    "or ask us in the shop."
)


@dataclass(frozen=True)
class Product:
    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    search_tags: list[str]
    price: float
    image_url: str
    has_written_description: bool

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Product":
        return cls(
            product_id=row["product_id"],
            name=row["name"],
            garment_type=row["garment_type"],
            description=(
                NO_DESCRIPTION
                if _STUB_DESCRIPTION.search(row["description"] or "")
                else row["description"]
            ),
            has_written_description=not _STUB_DESCRIPTION.search(row["description"] or ""),
            colors=_loads(row["colors"]),
            search_tags=_loads(row["search_tags"]),
            price=float(row["price"]),
            # Served by this backend rather than as a raw filesystem path. The version
            # marker changes when the image pipeline changes, so a browser holding the
            # old black-background copy fetches the new one instead of reusing it.
            image_url=f"/api/products/{row['product_id']}/image?v={IMAGE_PIPELINE_VERSION}",
        )


def list_products() -> list[Product]:
    with connect() as con:
        rows = con.execute("select * from catalogue order by name").fetchall()
    return [Product.from_row(r) for r in rows]


def get_product(product_id: str) -> Product | None:
    with connect() as con:
        row = con.execute(
            "select * from catalogue where product_id = ?", (product_id,)
        ).fetchone()
    return Product.from_row(row) if row else None


def get_inventory(product_id: str) -> list[dict[str, object]]:
    """Stock for one product, in catalogue size order. quantity 0 means out of stock."""
    with connect() as con:
        rows = con.execute(
            "select size, quantity from inventory where product_id = ?", (product_id,)
        ).fetchall()
    by_size = {r["size"]: int(r["quantity"]) for r in rows}
    ordered = [s for s in SIZE_ORDER if s in by_size]
    ordered += sorted(s for s in by_size if s not in SIZE_ORDER)
    return [
        {"size": s, "quantity": by_size[s], "in_stock": by_size[s] > 0} for s in ordered
    ]


class EmailAlreadyRegistered(Exception):
    """Raised when a signup uses an email that already has an account."""


def normalise_email(email: str) -> str:
    """Emails are matched case-insensitively; `users.email` has a unique index."""
    return email.strip().lower()


def get_user_by_email(email: str) -> sqlite3.Row | None:
    with connect() as con:
        return con.execute(
            "select * from users where lower(email) = ?", (normalise_email(email),)
        ).fetchone()


def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    with connect() as con:
        return con.execute("select * from users where id = ?", (user_id,)).fetchone()


def create_user(
    first_name: str, last_name: str, email: str, password_hash: str
) -> sqlite3.Row:
    """Insert a new account.

    `users.name` is NOT NULL and predates the split name columns, so all three are
    written. The caller passes an already-hashed password; this function never sees a
    plaintext one.
    """
    full_name = f"{first_name.strip()} {last_name.strip()}".strip()
    try:
        with connect_rw() as con:
            cursor = con.execute(
                "insert into users (name, email, password_hash, first_name, last_name)"
                " values (?, ?, ?, ?, ?)",
                (
                    full_name,
                    normalise_email(email),
                    password_hash,
                    first_name.strip(),
                    last_name.strip(),
                ),
            )
            user_id = cursor.lastrowid
    except sqlite3.IntegrityError as exc:
        # The unique index on email is what makes this a database answer rather than a
        # check-then-insert race.
        raise EmailAlreadyRegistered(email) from exc
    found = get_user_by_id(int(user_id))
    if found is None:  # pragma: no cover - would mean the insert vanished
        raise RuntimeError("the new account could not be read back")
    return found


def recent_messages(user_id: int, limit: int) -> list:
    """The tail of a signed-in shopper's conversation, oldest first, as PydanticAI
    message objects.

    Bounded on purpose: everything returned here is re-sent to the model on every turn
    and paid for again, so this is a recent slice rather than the whole conversation.
    """
    from pydantic_ai.messages import (
        ModelRequest,
        ModelResponse,
        TextPart,
        UserPromptPart,
    )

    with connect() as con:
        rows = con.execute(
            "select role, content from chat_messages where user_id = ?"
            " order by id desc limit ?",
            (user_id, limit),
        ).fetchall()

    history: list = []
    for row in reversed(rows):  # back to oldest-first for the model
        if row["role"] == "user":
            history.append(ModelRequest(parts=[UserPromptPart(content=row["content"])]))
        elif row["role"] == "assistant":
            history.append(ModelResponse(parts=[TextPart(content=row["content"])]))
    return history


def save_exchange(
    user_id: int, question: str, reply: str, products: list[dict[str, object]]
) -> None:
    """Write one turn to `chat_messages`.

    Decision D2: this is only ever called for a signed-in shopper. The schema enforces it
    too — `user_id` is NOT NULL with a foreign key to `users` — so an anonymous
    conversation cannot be stored even by mistake.

    `products_json` snapshots the cards as shown, matching the seeded rows, where only
    assistant messages carry it.
    """
    with connect_rw() as con:
        con.execute(
            "insert into chat_messages (user_id, role, content) values (?, 'user', ?)",
            (user_id, question),
        )
        con.execute(
            "insert into chat_messages (user_id, role, content, products_json)"
            " values (?, 'assistant', ?, ?)",
            (user_id, reply, json.dumps(products)),
        )


def stored_messages(user_id: int, limit: int = 50) -> list[dict[str, object]]:
    """A signed-in shopper's saved conversation, oldest first, for re-rendering in the
    chat panel when they come back.

    Separate from `recent_messages`, which builds PydanticAI objects for the model. This
    one returns the display shape, including the product cards snapshotted at the time.
    """
    with connect() as con:
        rows = con.execute(
            "select role, content, products_json, created_at from chat_messages"
            " where user_id = ? order by id desc limit ?",
            (user_id, limit),
        ).fetchall()

    out: list[dict[str, object]] = []
    for row in reversed(rows):
        try:
            products = json.loads(row["products_json"]) if row["products_json"] else []
        except ValueError:
            products = []
        out.append(
            {
                "role": row["role"],
                "content": row["content"],
                "products": products,
                "created_at": row["created_at"],
            }
        )
    return out


def clear_messages(user_id: int) -> int:
    """Delete one shopper's conversation. Theirs to erase, per D2."""
    with connect_rw() as con:
        cursor = con.execute("delete from chat_messages where user_id = ?", (user_id,))
        return cursor.rowcount


# --- Recently viewed ---------------------------------------------------------------
#
# This is the one additive schema change to the supplied database. No existing table is
# altered and no existing row is touched; `CREATE TABLE IF NOT EXISTS` adds a table the
# assignment did not ship. Signed-out shoppers are never written here — their list lives
# in their own browser (see output/usability.md).

RECENTLY_VIEWED_LIMIT = 8

# Bump when the image pipeline changes, to invalidate browser caches.
IMAGE_PIPELINE_VERSION = 6


def ensure_schema() -> None:
    """Create the app-owned table if it is missing. Safe to call on every startup."""
    with connect_rw() as con:
        con.execute(
            """
            create table if not exists recently_viewed (
                id integer primary key autoincrement,
                user_id integer not null,
                product_id text not null,
                viewed_at text not null default (datetime('now')),
                unique (user_id, product_id),
                foreign key (user_id) references users(id),
                foreign key (product_id) references catalogue(product_id)
            )
            """
        )


def record_view(user_id: int, product_id: str) -> None:
    """Note that a signed-in shopper opened a product.

    `UNIQUE (user_id, product_id)` plus an upsert means re-opening something moves it to
    the top rather than filling the list with duplicates.
    """
    with connect_rw() as con:
        con.execute(
            "insert into recently_viewed (user_id, product_id) values (?, ?)"
            " on conflict(user_id, product_id)"
            " do update set viewed_at = datetime('now')",
            (user_id, product_id),
        )


def recently_viewed(user_id: int, limit: int = RECENTLY_VIEWED_LIMIT) -> list[str]:
    with connect() as con:
        rows = con.execute(
            "select product_id from recently_viewed where user_id = ?"
            " order by viewed_at desc, id desc limit ?",
            (user_id, limit),
        ).fetchall()
    return [r["product_id"] for r in rows]


def clear_recently_viewed(user_id: int) -> int:
    with connect_rw() as con:
        return con.execute(
            "delete from recently_viewed where user_id = ?", (user_id,)
        ).rowcount


def all_stock() -> dict[str, dict[str, int]]:
    """Every product's stock by size, in one read, for the browser-side filter."""
    with connect() as con:
        rows = con.execute("select product_id, size, quantity from inventory").fetchall()
    out: dict[str, dict[str, int]] = {}
    for row in rows:
        out.setdefault(row["product_id"], {})[row["size"]] = int(row["quantity"])
    return out


def image_path(product_id: str) -> Path | None:
    """Resolve a product's image, refusing anything that escapes the image folder.

    The stored path is user data as far as this process is concerned, so it is resolved
    and then checked against the image directory rather than trusted.
    """
    with connect() as con:
        row = con.execute(
            "select image_file_path from catalogue where product_id = ?", (product_id,)
        ).fetchone()
    if row is None:
        return None
    root = (data_dir() / IMAGE_DIR_NAME).resolve()
    candidate = (data_dir() / row["image_file_path"]).resolve()
    if not candidate.is_relative_to(root) or not candidate.is_file():
        return None
    return candidate
