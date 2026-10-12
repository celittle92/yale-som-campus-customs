"""Tools the shop assistant can call.

Every one of these reads the catalogue. None of them calls a model, so they are free to
run and free to test. This is the only way the agent can learn a price, a colour, or a
stock level — the system prompt forbids it from answering those from memory.
"""
from __future__ import annotations

from db import get_inventory, get_product, list_products

# --- Canonical categories (decision D3 in output/harness.md) -----------------------
#
# `catalogue.garment_type` holds 22 spellings of about seven real categories, including
# one pair that differs only by letter case. Filtering on it directly returns 5 of the 27
# hoodies. This maps the raw values onto seven labels at read time; the database is not
# modified and the raw value is still what a product page displays.
#
# Order matters: the first rule whose keyword appears wins, so "full-zip fleece jacket"
# is a fleece jacket rather than a jacket, and "hooded sweatshirt" is a hoodie rather
# than a crewneck.
CATEGORY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("Fleece jacket", ("fleece jacket",)),
    ("Jacket", ("bomber jacket", "jacket")),
    ("Quarter-zip", ("quarter-zip", "quarter zip", "1/4 zip")),
    ("Hoodie", ("hoodie", "hooded")),
    ("Crewneck sweatshirt", ("crewneck", "mockneck")),
    ("Long-sleeve shirt", ("long-sleeve performance", "long sleeve performance")),
    ("T-shirt", ("t-shirt", "tee")),
]

CATEGORIES = [label for label, _ in CATEGORY_RULES]
MAX_RESULTS = 6


def canonical_category(garment_type: str) -> str:
    lowered = garment_type.lower()
    for label, keywords in CATEGORY_RULES:
        if any(keyword in lowered for keyword in keywords):
            return label
    return "Other"


def _summarise(product) -> dict[str, object]:
    """The shape a tool hands back to the model: enough to answer, nothing invented."""
    return {
        "product_id": product.product_id,
        "name": product.name,
        "category": canonical_category(product.garment_type),
        "garment_type": product.garment_type,
        "price_usd": product.price,
        "colors_in_design": product.colors,
        "description": product.description,
    }


def search_products(query: str, limit: int = MAX_RESULTS) -> list[dict[str, object]]:
    """Search the catalogue by words a shopper might use.

    Matches against the product name, its description, its curated search tags, the
    colours in its design, and its garment type. Returns at most `limit` products,
    best match first. Returns an empty list when nothing matches — which means we do
    not carry it, and the shopper should be told so.
    """
    terms = [t for t in query.lower().split() if len(t) > 1]
    if not terms:
        return []

    scored: list[tuple[int, object]] = []
    for product in list_products():
        haystacks = {
            "name": product.name.lower(),
            "tags": " ".join(product.search_tags).lower(),
            "colors": " ".join(product.colors).lower(),
            "type": product.garment_type.lower(),
            "category": canonical_category(product.garment_type).lower(),
            "description": product.description.lower(),
        }
        # Weighted so a name or tag hit beats an incidental word in the description.
        score = 0
        for term in terms:
            if term in haystacks["name"]:
                score += 5
            if term in haystacks["tags"]:
                score += 4
            if term in haystacks["category"] or term in haystacks["type"]:
                score += 3
            if term in haystacks["colors"]:
                score += 2
            if term in haystacks["description"]:
                score += 1
        if score:
            scored.append((score, product))

    scored.sort(key=lambda pair: (-pair[0], pair[1].name))
    return [_summarise(product) for _, product in scored[: max(1, min(limit, MAX_RESULTS))]]


def browse_category(category: str, limit: int = MAX_RESULTS) -> dict[str, object]:
    """List products in one of the shop's categories.

    Valid categories: Crewneck sweatshirt, Hoodie, T-shirt, Quarter-zip, Fleece jacket,
    Jacket, Long-sleeve shirt. Use this for "what hoodies do you have" style questions.
    """
    wanted = category.strip().lower()
    match = next((c for c in CATEGORIES if c.lower() == wanted), None)
    if match is None:
        # Be forgiving about "hoodies" vs "Hoodie" before giving up.
        match = next((c for c in CATEGORIES if c.lower().rstrip("s") in wanted or wanted.rstrip("s") in c.lower()), None)
    if match is None:
        return {"error": f"'{category}' is not a category we use.", "valid_categories": CATEGORIES}

    products = [p for p in list_products() if canonical_category(p.garment_type) == match]
    return {
        "category": match,
        "total_in_category": len(products),
        "showing": min(len(products), limit),
        "products": [_summarise(p) for p in products[:limit]],
    }


def get_product_details(product_id: str) -> dict[str, object]:
    """Everything about one product, including stock for every size.

    Use this before quoting a price or saying whether something is available.
    """
    product = get_product(product_id)
    if product is None:
        return {"error": f"No product with id '{product_id}'. Search first to find valid ids."}
    sizes = get_inventory(product_id)
    return {
        **_summarise(product),
        "sizes": sizes,
        "sizes_in_stock": [s["size"] for s in sizes if s["in_stock"]],
        "sizes_out_of_stock": [s["size"] for s in sizes if not s["in_stock"]],
        "has_recorded_colors": bool(product.colors),
    }


def check_size_availability(product_id: str, size: str) -> dict[str, object]:
    """Is one product available in one size? Sizes are XS, S, M, L, XL, XXL."""
    product = get_product(product_id)
    if product is None:
        return {"error": f"No product with id '{product_id}'."}
    wanted = size.strip().upper()
    for entry in get_inventory(product_id):
        if entry["size"] == wanted:
            return {
                "product_id": product_id,
                "name": product.name,
                "size": wanted,
                "in_stock": entry["in_stock"],
                "quantity": entry["quantity"],
            }
    return {
        "error": f"'{size}' is not a size we carry.",
        "sizes_we_carry": [e["size"] for e in get_inventory(product_id)],
    }


def shop_overview() -> dict[str, object]:
    """Counts, categories and the price range. Use for "what do you sell" questions."""
    products = list_products()
    prices = sorted({p.price for p in products})
    counts: dict[str, int] = {}
    for product in products:
        label = canonical_category(product.garment_type)
        counts[label] = counts.get(label, 0) + 1
    return {
        "total_products": len(products),
        "categories": counts,
        "sizes_carried": ["XS", "S", "M", "L", "XL", "XXL"],
        "price_points_usd": prices,
    }
