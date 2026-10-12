"""Structured types for the Campus Customs shop assistant.

The important one is `ChatAnswer`. The agent returns **product ids**, not product data:
the backend then looks each id up in the catalogue and builds the cards it sends to the
browser. That way a price or a size on the page always came out of the database, and the
model cannot invent a product, a price, or a colour even if it tries.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


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


class SizeStock(BaseModel):
    size: str
    quantity: int
    in_stock: bool


class ProductSummary(ProductCard):
    """Alias kept for the existing product routes."""


class ProductDetail(ProductCard):
    search_tags: list[str]
    sizes: list[SizeStock]


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


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ChatReply(BaseModel):
    """The response body the chat widget receives."""

    reply: str
    products: list[ProductCard] = Field(default_factory=list)
    saved: bool = Field(
        default=False,
        description="True when this exchange was written to chat_messages, which only "
        "happens for a signed-in shopper.",
    )
