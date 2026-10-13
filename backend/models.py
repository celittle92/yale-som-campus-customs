"""Structured types for the Campus Customs shop assistant.

The important one is `ChatAnswer`. The agent returns **product ids**, not product data:
the backend then looks each id up in the catalogue and builds the cards it sends to the
browser. That way a price or a size on the page always came out of the database, and the
model cannot invent a product, a price, or a colour even if it tries.
"""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator


class ProductCard(BaseModel):
    """One product as the front end renders it. Built from a catalogue row, never from
    model output."""

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    price: float
    image_url: str


# --- What the tools hand back ------------------------------------------------------
#
# Tool results are typed rather than loose dictionaries so the model is given a stable,
# documented shape every time, and so a change to a field name is a type error here
# instead of a silently wrong answer in the chat.
#
# Two deliberate choices run through all of these:
#
# 1. Field names say what the value *is*: `price_usd`, not `price`; `colors_in_design`,
#    not `colors`. The model reads these names as part of its context, so a name that
#    carries its own units and meaning is a cheap way to prevent a wrong assumption.
# 2. Derived fields are computed here, not left to the model. `sizes_in_stock` is the
#    filtering the model would otherwise have to do itself, and arithmetic is exactly
#    where a language model is least reliable.


class SizeStock(BaseModel):
    size: str = Field(description="XS, S, M, L, XL or XXL.")
    quantity: int = Field(description="Units on hand. 0 means out of stock in this size.")
    in_stock: bool = Field(description="True when quantity is greater than zero.")


class ProductLookup(BaseModel):
    """One product as a tool reports it. Catalogue fields only — no stock."""

    product_id: str = Field(description="Use this in product_ids. Never invent one.")
    name: str
    category: str = Field(
        description="Normalised category: Crewneck sweatshirt, Hoodie, T-shirt, "
        "Quarter-zip, Fleece jacket, Jacket or Long-sleeve shirt."
    )
    garment_type: str = Field(
        description="The shop's own wording for the cut, e.g. 'full-zip hooded "
        "sweatshirt'. Use it when describing the item."
    )
    price_usd: float = Field(description="Price in US dollars. Quote it with cents.")
    colors_in_design: list[str] = Field(
        description="Colours present IN this garment's design, not colourways to choose "
        "from. Each product comes in the one colourway pictured."
    )
    description: str
    has_written_description: bool = Field(
        default=True,
        description="False for the few products with no real description recorded. When "
        "false, do not describe the garment — say we have not written one up and point "
        "to the photo.",
    )


class ProductDetails(ProductLookup):
    """A product plus its stock across every size. Catalogue and inventory combined."""

    sizes: list[SizeStock] = Field(description="All six sizes, in catalogue order.")
    sizes_in_stock: list[str] = Field(description="Sizes with quantity above zero.")
    sizes_out_of_stock: list[str] = Field(
        description="Sizes with quantity zero. Say these are unavailable if asked."
    )
    total_units_in_stock: int
    has_recorded_colors: bool = Field(
        description="False for the few products with no colours recorded. When false, "
        "say colours are not recorded rather than describing one."
    )


class SizeCheck(BaseModel):
    """The answer to 'do you have X in size Y'."""

    product_id: str
    name: str
    size: str
    in_stock: bool
    quantity: int = Field(description="Units on hand in this size. 0 means none.")
    other_sizes_in_stock: list[str] = Field(
        description="Sizes that are available, so an out-of-stock answer can offer an "
        "alternative without a second lookup."
    )


class SearchResult(BaseModel):
    """Search results, plus any spelling the search had to correct to find them."""

    products: list[ProductLookup]
    interpreted_as: str = Field(
        description="The query actually searched for, after correcting typos."
    )
    corrections: dict[str, str] = Field(
        default_factory=dict,
        description="Words that were corrected, as typed -> used. When this is not "
        "empty, tell the shopper what you searched for, e.g. \"showing crewnecks\". "
        "Never pretend they typed it correctly.",
    )
    unmatched_terms: list[str] = Field(
        default_factory=list,
        description="Words from the query that match nothing in the catalogue. These "
        "results do NOT satisfy them. If someone asks for a 'red dress' and 'dress' is "
        "here, say we do not carry dresses before showing red items — do not present "
        "these as what they asked for.",
    )


class CategoryListing(BaseModel):
    category: str
    total_in_category: int = Field(
        description="How many we carry in total, which may exceed the number shown."
    )
    products: list[ProductLookup]


class PriceSearchResult(BaseModel):
    min_price_usd: float | None
    max_price_usd: float | None
    total_matching: int
    products: list[ProductLookup]


class ShopOverview(BaseModel):
    total_products: int
    products_per_category: dict[str, int]
    sizes_carried: list[str]
    price_points_usd: list[float] = Field(
        description="Every price in the catalogue. A price outside this list is wrong."
    )


class LookupError(BaseModel):
    """Returned instead of raising, so a bad argument becomes something the agent can
    recover from and explain rather than a failed request."""

    error: str
    suggestion: str | None = None


# --- API response models -----------------------------------------------------------


class ProductSummary(ProductCard):
    """A product as `/api/products` returns it."""


class ProductDetail(ProductCard):
    """A product as `/api/products/{id}` returns it: catalogue plus stock."""

    search_tags: list[str]
    sizes: list[SizeStock]


class SignupRequest(BaseModel):
    """A create-account submission. Validated before any hashing happens."""

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)
    confirm_password: str = Field(min_length=8, max_length=256)

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, value: str, info) -> str:
        # Checked here as well as in the browser: client-side validation is a courtesy,
        # not a control.
        if value != info.data.get("password"):
            raise ValueError("The two passwords do not match.")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)


class PublicUser(BaseModel):
    """Everything about a user that is safe to send to a browser.

    `password_hash` is deliberately absent and must stay that way.
    """

    id: int
    first_name: str | None
    last_name: str | None
    name: str
    email: str


class ChatAnswer(BaseModel):
    """What the agent is required to produce. Validated by PydanticAI before we see it."""

    reply: str = Field(
        description=(
            "The answer to show the shopper, in the Campus Customs voice. Plain prose, "
            "no markdown tables. Say plainly when something is not known."
        ),
        min_length=1,
        max_length=1500,
    )
    product_ids: list[str] = Field(
        default_factory=list,
        description=(
            "Catalogue product_id values to show as cards, most relevant first. Only ids "
            "returned by a tool in this conversation. Empty when no product is relevant."
        ),
        max_length=6,
    )
    used_catalogue: bool = Field(
        default=False,
        description=(
            "True if this answer's facts came from a tool result. False for greetings, "
            "chit-chat, or a refusal."
        ),
    )
    product_match_label: str | None = Field(
        default=None,
        description=(
            "A short noun phrase naming what the products in product_ids are, as a "
            "heading: 'Hoodies', 'Navy crewnecks', 'Under $40'. Two or three words, no "
            "sentence, no count — the website adds the count itself. Leave null when "
            "product_ids is empty."
        ),
        max_length=60,
    )


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    page_path: str | None = Field(
        default=None,
        max_length=200,
        description="Where the shopper is on the site, e.g. '/products/basic-hoodie-big-"
        "yale'. The backend resolves what that means; the browser only reports the path, "
        "never the product data.",
    )


class ShopperContext(BaseModel):
    """What the agent knows about who it is talking to and what they are looking at.

    Passed as PydanticAI run dependencies and rendered into the instructions for each
    run. Built server-side from the session cookie and the page path — none of it is
    taken on trust from the browser.
    """

    signed_in: bool = False
    first_name: str | None = None
    full_name: str | None = None
    email: str | None = None

    page_path: str | None = None
    viewing_product_id: str | None = Field(
        default=None,
        description="Set when the shopper is on a product detail page. 'this' in their "
        "question almost certainly means this product.",
    )
    viewing_product_name: str | None = None

    recently_viewed: list[str] = Field(
        default_factory=list,
        description="Names of products this shopper opened recently, most recent first. "
        "Lets the agent answer 'that hoodie I was looking at'.",
    )

    def as_instructions(self) -> str:
        """Render the context as a block appended to the system instructions."""
        lines: list[str] = ["## Who you are talking to, and where they are"]

        if self.signed_in:
            lines.append(
                f"This shopper is signed in. Their name is {self.full_name}"
                f"{f' and they go by {self.first_name}' if self.first_name else ''}, "
                f"and their account email is {self.email}."
            )
            lines.append(
                "Greet them by first name if it fits naturally. Their earlier messages "
                "are in this conversation, so you may refer back to them. Do not read "
                "their email address back to them unless they ask for it."
            )
        else:
            lines.append(
                "This shopper is not signed in, so you do not know their name and their "
                "conversation is not being saved. Do not ask for personal details. If "
                "they want the conversation kept, they can log in."
            )

        if self.viewing_product_id:
            lines.append(
                f"They are currently looking at **{self.viewing_product_name}** "
                f"(`{self.viewing_product_id}`). If they say 'this', 'it', or 'this one' "
                "without naming a product, they mean this one — look it up by that id "
                "rather than asking which item they mean."
            )
        elif self.page_path:
            where = {
                "/": "the home page",
                "/products": "the full product list",
                "/about": "the about page",
            }.get(self.page_path)
            if where:
                lines.append(f"They are on {where}.")

        if self.recently_viewed:
            lines.append(
                "Products they have opened recently, most recent first: "
                + ", ".join(self.recently_viewed)
                + ". If they refer back to something they were looking at, this is "
                "probably it. Search for it by name to get its id before answering."
            )

        return "\n\n".join(lines)


class ChatHistoryMessage(BaseModel):
    """One stored turn, as the chat panel re-renders it for a returning shopper."""

    role: str
    content: str
    products: list[ProductCard] = Field(default_factory=list)
    created_at: str


class ChatReply(BaseModel):
    """The chat API contract — what `POST /api/chat` returns.

    `products` are whole catalogue rows, resolved by the backend from the ids the agent
    returned, so the front end can render cards without a second request and without
    ever seeing a price the model wrote. The same list is rendered twice: under the reply
    in the chat panel, and as a results section on the Products page.
    """

    reply: str
    products: list[ProductCard] = Field(default_factory=list)
    match_label: str | None = Field(
        default=None,
        description="Short heading for the set, e.g. 'Hoodies'. Null when there are no "
        "products.",
    )
    saved: bool = Field(
        default=False,
        description="True when this exchange was written to chat_messages, which only "
        "happens for a signed-in shopper.",
    )
