"""Campus Customs API.

Problem 3 scope: serve the product catalogue and the product images to the front end.
Problem 5 grows this into the agent backend, so the chat route is declared here as an
explicit stub rather than being left out.
"""
from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .db import get_inventory, get_product, image_path, list_products

app = FastAPI(
    title="Campus Customs API",
    description="Yale apparel catalogue for the Campus Customs storefront.",
    version="0.1.0",
)

# The Vite dev server runs on its own origin. In development it proxies /api to this
# app, so these origins are a convenience for calling the API directly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class ProductSummary(BaseModel):
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


class ProductDetail(ProductSummary):
    search_tags: list[str]
    sizes: list[SizeStock]


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ChatReply(BaseModel):
    reply: str
    products: list[ProductSummary] = []


@app.get("/api/health")
def health() -> dict[str, object]:
    """Cheap readiness check that also proves the database is reachable."""
    return {"status": "ok", "products": len(list_products())}


@app.get("/api/products", response_model=list[ProductSummary])
def products() -> list[dict]:
    return [
        {k: v for k, v in asdict(p).items() if k != "search_tags"}
        for p in list_products()
    ]


@app.get("/api/products/{product_id}", response_model=ProductDetail)
def product(product_id: str) -> dict:
    found = get_product(product_id)
    if found is None:
        raise HTTPException(status_code=404, detail="No such product")
    return {**asdict(found), "sizes": get_inventory(product_id)}


@app.get("/api/products/{product_id}/image")
def product_image(product_id: str) -> FileResponse:
    path = image_path(product_id)
    if path is None:
        raise HTTPException(status_code=404, detail="No image for that product")
    return FileResponse(path, media_type="image/jpeg")


@app.post("/api/chat", response_model=ChatReply)
def chat(request: ChatRequest) -> ChatReply:
    """Stub. Problem 5 replaces this with the PydanticAI agent.

    It answers in the shape the real endpoint will use — a reply plus the products to
    show on the page — so the front end does not change when the agent arrives.
    """
    return ChatReply(
        reply=(
            "I am not connected to the shop assistant yet. Once I am, I will be able to "
            "look up prices, sizes, and what is actually in stock."
        ),
        products=[],
    )
