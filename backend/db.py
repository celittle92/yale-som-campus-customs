"""Read-only access to the Campus Customs catalogue.

The database and the product images are not part of this repository: the assignment
forbids committing them. Point CAMPUS_CUSTOMS_DATA at the folder holding
``campus_customs.db`` and ``products/``, or keep the default layout described in the
README.
"""
from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
# The supplied data sits outside the repo so it cannot be committed by accident.
DEFAULT_DATA_DIR = REPO_DIR.parent / "data hw4"
DB_NAME = "campus_customs.db"
IMAGE_DIR_NAME = "products"

# Size order is fixed by the catalogue; sorting alphabetically would read as L, M, S, XL.
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]


@lru_cache(maxsize=1)
def data_dir() -> Path:
    configured = os.getenv("CAMPUS_CUSTOMS_DATA")
    path = Path(configured).expanduser() if configured else DEFAULT_DATA_DIR
    if not (path / DB_NAME).is_file():
        raise RuntimeError(
            f"{DB_NAME} not found in {path}. Set CAMPUS_CUSTOMS_DATA to the folder that "
            f"holds {DB_NAME} and {IMAGE_DIR_NAME}/."
        )
    return path.resolve()


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

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Product":
        return cls(
            product_id=row["product_id"],
            name=row["name"],
            garment_type=row["garment_type"],
            description=row["description"],
            colors=_loads(row["colors"]),
            search_tags=_loads(row["search_tags"]),
            price=float(row["price"]),
            # Served by this backend rather than as a raw filesystem path.
            image_url=f"/api/products/{row['product_id']}/image",
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


def clear_messages(user_id: int) -> int:
    """Delete one shopper's conversation. Theirs to erase, per D2."""
    with connect_rw() as con:
        cursor = con.execute("delete from chat_messages where user_id = ?", (user_id,))
        return cursor.rowcount


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
