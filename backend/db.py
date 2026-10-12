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
    """A read-only connection. Nothing in this app writes to the supplied database."""
    con = sqlite3.connect(f"file:{data_dir() / DB_NAME}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
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
