"""Tools the shop assistant can call.

Every one reads `campus_customs.db`. None calls a model, so they are free to run and free
to test. This is the only way the agent can learn a description, a price or a stock level
— the instructions forbid it from answering those from memory.

Each tool returns a typed model from `models.py` rather than a loose dictionary, so the
shape handed to the agent is documented and stable, and a renamed field breaks here
instead of producing a quietly wrong answer in the chat.
"""
from __future__ import annotations

import difflib
import re
from functools import lru_cache

from db import get_inventory, get_product, list_products
from models import (
    CategoryListing,
    LookupError,
    PriceSearchResult,
    ProductDetails,
    ProductLookup,
    SearchResult,
    ShopOverview,
    SizeCheck,
    SizeStock,
)

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

# --- Themes: the three ways people actually shop -----------------------------------
#
# Residential college, varsity team, graduate school. Derived from `search_tags` so the
# home page can link straight to "everything for your college" without a second schema.
#
# The exclusions matter. "Crew" is a sport, but "crewneck", "crew neck" and "men's
# crewneck" are a collar — matching naively would file all 29 crewneck sweatshirts under
# varsity teams.
THEME_RULES: dict[str, dict[str, tuple[str, ...]]] = {
    "college": {
        "include": (
            "benjamin franklin", "berkeley", "branford", "davenport", "grace hopper",
            "jonathan edwards", "morse", "pierson", "saybrook", "timothy dwight",
            "trumbull", "silliman", "ezra stiles", "residential college",
        ),
        "exclude": (),
    },
    "team": {
        "include": (
            "baseball", "football", "hockey", "soccer", "lacrosse", "tennis",
            "basketball", "swimming", "volleyball", "golf", "track", "rugby",
            "crew", "rowing",
        ),
        "exclude": ("crewneck", "crew neck", "crew-neck"),
    },
    "school": {
        "include": (
            "school of", "law school", "divinity", "som", "medicine", "nursing",
            "architecture", "engineering", "public health", "forest school",
        ),
        "exclude": (),
    },
}

THEME_LABELS = {
    "college": "Residential colleges",
    "team": "Varsity teams",
    "school": "Graduate schools",
}


def themes_for(product) -> list[str]:
    """Which of the three shopping themes a product belongs to, if any."""
    haystack = " ".join(
        [product.name, " ".join(product.search_tags), product.description]
    ).lower()
    found: list[str] = []
    for theme, rules in THEME_RULES.items():
        cleaned = haystack
        for term in rules["exclude"]:
            cleaned = cleaned.replace(term, " ")
        if any(term in cleaned for term in rules["include"]):
            found.append(theme)
    return found
SIZES = ["XS", "S", "M", "L", "XL", "XXL"]
MAX_RESULTS = 6


def canonical_category(garment_type: str) -> str:
    lowered = garment_type.lower()
    for label, keywords in CATEGORY_RULES:
        if any(keyword in lowered for keyword in keywords):
            return label
    return "Other"


def _lookup(product) -> ProductLookup:
    """Catalogue row -> the shape the agent sees.

    `image_file_path` and `search_tags` are deliberately left out: the agent never needs
    them (the backend builds cards from the id) and every field costs tokens on every
    turn.
    """
    return ProductLookup(
        product_id=product.product_id,
        name=product.name,
        category=canonical_category(product.garment_type),
        garment_type=product.garment_type,
        price_usd=product.price,
        colors_in_design=product.colors,
        description=product.description,
        has_written_description=product.has_written_description,
    )


# --- Typo-tolerant search ----------------------------------------------------------
#
# A one-character typo used to return nothing, which made the agent say "we do not carry
# that" about products we do carry. A false statement about our own inventory is an
# accuracy failure, not just a usability one.
#
# The correction is deliberately conservative, because the opposite failure is worse: if
# fuzzy matching stretched far enough to turn a word for something we genuinely do not
# sell into something we do, the agent would confidently show the wrong thing. So a term
# is only corrected to a word that actually appears in this catalogue, and only when it
# is a close match. "dres" finds nothing, because we sell no dresses — and that honest
# empty result is the right answer.

MIN_FUZZY_LENGTH = 4  # shorter words are too easy to turn into a different real word
FUZZY_CUTOFF = 0.78


@lru_cache(maxsize=1)
def search_vocabulary() -> frozenset[str]:
    """Every word that appears anywhere searchable in the catalogue."""
    words: set[str] = set()
    for product in list_products():
        fields = [
            product.name,
            product.garment_type,
            canonical_category(product.garment_type),
            " ".join(product.colors),
            " ".join(product.search_tags),
        ]
        for text in fields:
            for word in re.split(r"[^a-z0-9]+", text.lower()):
                if len(word) > 2:
                    words.add(word)
    return frozenset(words)


def correct_terms(terms: list[str]) -> tuple[list[str], dict[str, str]]:
    """Fix typos against the catalogue's own vocabulary.

    Returns the terms to search with, and a map of what was changed. A term already in
    the vocabulary is left alone; one with no close match is also left alone, so a
    genuine "we do not sell that" still returns nothing.
    """
    vocabulary = search_vocabulary()
    used: list[str] = []
    corrections: dict[str, str] = {}
    for term in terms:
        if term in vocabulary or len(term) < MIN_FUZZY_LENGTH:
            used.append(term)
            continue
        # A substring hit means it is a real prefix like "hood" — not a typo.
        if any(term in word for word in vocabulary):
            used.append(term)
            continue
        close = difflib.get_close_matches(term, vocabulary, n=1, cutoff=FUZZY_CUTOFF)
        if close:
            corrections[term] = close[0]
            used.append(close[0])
        else:
            used.append(term)
    return used, corrections


def search_products(query: str, limit: int = MAX_RESULTS) -> SearchResult:
    """Find products by the words a shopper uses. Tolerates typos.

    Matches the product name, its curated search tags, its category and cut, the colours
    in its design, and its description. Misspellings are corrected against the
    catalogue's own vocabulary, and any correction is reported in `corrections` — tell
    the shopper what you searched for when that happens.

    Empty `products` means we genuinely do not carry it. Say so rather than guessing.
    """
    raw = [t for t in query.lower().split() if len(t) > 1]
    if not raw:
        return SearchResult(products=[], interpreted_as=query, corrections={})

    terms, corrections = correct_terms(raw)

    scored: list[tuple[int, object]] = []
    # Scoring is OR-based so natural phrasing still finds things, which means a query
    # can match on one word while another matches nothing at all. Tracking that is what
    # stops "red dress" being answered with red t-shirts as though they were dresses.
    matched_terms: set[str] = set()

    for product in list_products():
        fields = {
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
            hit = 0
            if term in fields["name"]:
                hit += 5
            if term in fields["tags"]:
                hit += 4
            if term in fields["category"] or term in fields["type"]:
                hit += 3
            if term in fields["colors"]:
                hit += 2
            if term in fields["description"]:
                hit += 1
            if hit:
                matched_terms.add(term)
            score += hit
        if score:
            scored.append((score, product))

    scored.sort(key=lambda pair: (-pair[0], pair[1].name))
    capped = max(1, min(limit, MAX_RESULTS))
    return SearchResult(
        products=[_lookup(product) for _, product in scored[:capped]],
        interpreted_as=" ".join(terms),
        corrections=corrections,
        unmatched_terms=[t for t in terms if t not in matched_terms],
    )


def browse_category(category: str, limit: int = MAX_RESULTS) -> CategoryListing | LookupError:
    """List products in one category.

    Categories: Crewneck sweatshirt, Hoodie, T-shirt, Quarter-zip, Fleece jacket, Jacket,
    Long-sleeve shirt. Use this for "what hoodies do you have" style questions.
    """
    wanted = category.strip().lower()
    match = next((c for c in CATEGORIES if c.lower() == wanted), None)
    if match is None:
        # Be forgiving about "hoodies" vs "Hoodie" before giving up.
        match = next(
            (c for c in CATEGORIES if c.lower().rstrip("s") in wanted or wanted.rstrip("s") in c.lower()),
            None,
        )
    if match is None:
        return LookupError(
            error=f"'{category}' is not a category we use.",
            suggestion=f"Valid categories: {', '.join(CATEGORIES)}.",
        )

    products = [p for p in list_products() if canonical_category(p.garment_type) == match]
    return CategoryListing(
        category=match,
        total_in_category=len(products),
        products=[_lookup(p) for p in products[:limit]],
    )


def get_product_details(product_id: str) -> ProductDetails | LookupError:
    """Full information for one product: description, price, and stock in every size.

    **Call this before quoting a price or saying whether something is available.** It is
    the authoritative source for both.
    """
    product = get_product(product_id)
    if product is None:
        return LookupError(
            error=f"No product with id '{product_id}'.",
            suggestion="Use search_products or browse_category to find valid ids.",
        )
    rows = get_inventory(product_id)
    sizes = [SizeStock(**row) for row in rows]  # type: ignore[arg-type]
    return ProductDetails(
        **_lookup(product).model_dump(),
        sizes=sizes,
        sizes_in_stock=[s.size for s in sizes if s.in_stock],
        sizes_out_of_stock=[s.size for s in sizes if not s.in_stock],
        total_units_in_stock=sum(s.quantity for s in sizes),
        has_recorded_colors=bool(product.colors),
    )


def check_size_availability(product_id: str, size: str) -> SizeCheck | LookupError:
    """Whether one product is available in one size, and how many are left.

    Use this for "do you have this in a medium" questions. Sizes are XS, S, M, L, XL and
    XXL. A quantity of 0 means out of stock in that size — say so plainly.
    """
    product = get_product(product_id)
    if product is None:
        return LookupError(
            error=f"No product with id '{product_id}'.",
            suggestion="Use search_products to find valid ids.",
        )
    rows = get_inventory(product_id)
    sizes = [SizeStock(**row) for row in rows]  # type: ignore[arg-type]
    wanted = size.strip().upper()
    available = [s.size for s in sizes if s.in_stock]

    for entry in sizes:
        if entry.size == wanted:
            return SizeCheck(
                product_id=product_id,
                name=product.name,
                size=wanted,
                in_stock=entry.in_stock,
                quantity=entry.quantity,
                # Carried so an out-of-stock answer can offer an alternative without a
                # second lookup, and without the model guessing at one.
                other_sizes_in_stock=[s for s in available if s != wanted],
            )
    return LookupError(
        error=f"'{size}' is not a size we carry.",
        suggestion=f"We carry {', '.join(SIZES)}.",
    )


def find_products_by_price(
    max_price_usd: float | None = None,
    min_price_usd: float | None = None,
    category: str | None = None,
    limit: int = MAX_RESULTS,
) -> PriceSearchResult | LookupError:
    """Find products within a price range, optionally in one category.

    Use this for "what do you have under $50" questions rather than filtering a search
    result yourself — the comparison happens here, against the real prices.
    """
    if max_price_usd is None and min_price_usd is None:
        return LookupError(
            error="Give at least one of max_price_usd or min_price_usd.",
            suggestion="For 'under $50', pass max_price_usd=50.",
        )
    if category is not None:
        match = next((c for c in CATEGORIES if c.lower().rstrip("s") in category.lower()), None)
        if match is None:
            return LookupError(
                error=f"'{category}' is not a category we use.",
                suggestion=f"Valid categories: {', '.join(CATEGORIES)}.",
            )
    else:
        match = None

    matching = []
    for product in list_products():
        if max_price_usd is not None and product.price > max_price_usd:
            continue
        if min_price_usd is not None and product.price < min_price_usd:
            continue
        if match is not None and canonical_category(product.garment_type) != match:
            continue
        matching.append(product)

    matching.sort(key=lambda p: (p.price, p.name))
    return PriceSearchResult(
        min_price_usd=min_price_usd,
        max_price_usd=max_price_usd,
        total_matching=len(matching),
        products=[_lookup(p) for p in matching[:limit]],
    )


def similar_products(product_id: str, limit: int = 8) -> list[ProductLookup]:
    """Products like this one, best match first.

    Scored on category, shared colours, shared search tags and closeness in price —
    everything from the catalogue, nothing invented. Items with no stock in any size are
    pushed down, so a recommendation is usually something a shopper can actually buy.
    """
    target = get_product(product_id)
    if target is None:
        return []

    target_category = canonical_category(target.garment_type)
    target_colors = {c.lower() for c in target.colors}
    target_tags = {t.lower() for t in target.search_tags}

    scored: list[tuple[float, object]] = []
    for product in list_products():
        if product.product_id == target.product_id:
            continue
        score = 0.0
        if canonical_category(product.garment_type) == target_category:
            score += 10
        score += 3 * len(target_colors & {c.lower() for c in product.colors})
        score += 2 * len(target_tags & {t.lower() for t in product.search_tags})
        # Closer in price is a better substitute; $0 apart scores 4, $40 apart scores 0.
        score += max(0.0, 4 - abs(product.price - target.price) / 10)
        if score <= 0:
            continue
        if not any(row["in_stock"] for row in get_inventory(product.product_id)):
            score -= 8  # still eligible, but behind anything buyable
        scored.append((score, product))

    scored.sort(key=lambda pair: (-pair[0], pair[1].name))
    return [_lookup(p) for _, p in scored[:limit]]


def shop_overview() -> ShopOverview:
    """Counts, categories, sizes and every price the shop charges.

    Use for "what do you sell" questions, and to sanity-check a price: anything not in
    `price_points_usd` is wrong.
    """
    products = list_products()
    counts: dict[str, int] = {}
    for product in products:
        label = canonical_category(product.garment_type)
        counts[label] = counts.get(label, 0) + 1
    return ShopOverview(
        total_products=len(products),
        products_per_category=counts,
        sizes_carried=SIZES,
        price_points_usd=sorted({p.price for p in products}),
    )
