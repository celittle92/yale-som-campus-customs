"""Campus Customs API.

Problem 3 scope: serve the product catalogue and the product images to the front end.
Problem 5 grows this into the agent backend, so the chat route is declared here as an
explicit stub rather than being left out.
"""
from __future__ import annotations

import sqlite3
from dataclasses import asdict

from fastapi import Cookie, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, Field, field_validator

from . import sessions
from .auth import hash_password, verify_password
from .db import (
    EmailAlreadyRegistered,
    create_user,
    get_inventory,
    get_product,
    get_user_by_email,
    get_user_by_id,
    image_path,
    list_products,
)

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
    allow_credentials=True,  # the session cookie
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


class SignupRequest(BaseModel):
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


def _public_user(row: sqlite3.Row) -> PublicUser:
    return PublicUser(
        id=row["id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        name=row["name"],
        email=row["email"],
    )


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=sessions.COOKIE_NAME,
        value=token,
        httponly=True,  # JavaScript cannot read it, so XSS cannot steal the session.
        samesite="lax",
        # Development runs on http://localhost. Set this to True behind HTTPS.
        secure=False,
        path="/",
    )


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


@app.post("/api/auth/signup", response_model=PublicUser, status_code=201)
def signup(request: SignupRequest, response: Response) -> PublicUser:
    """Create an account. The plaintext password is hashed here and never stored."""
    password_hash = hash_password(request.password)
    try:
        row = create_user(
            request.first_name, request.last_name, str(request.email), password_hash
        )
    except EmailAlreadyRegistered:
        # Signup tells the truth about a taken email, because a signup form that hides
        # it is unusable. Login, below, deliberately does not.
        raise HTTPException(
            status_code=409,
            detail="An account with that email already exists. Try logging in.",
        ) from None
    _set_session_cookie(response, sessions.create(int(row["id"])))
    return _public_user(row)


@app.post("/api/auth/login", response_model=PublicUser)
def login(request: LoginRequest, response: Response) -> PublicUser:
    """Verify a password by re-hashing it. The stored value is never reversed."""
    row = get_user_by_email(str(request.email))
    # One generic message whether the email is unknown or the password is wrong, so the
    # endpoint cannot be used to discover which addresses have accounts.
    failure = HTTPException(status_code=401, detail="Invalid email or password.")
    if row is None:
        # Spend the work anyway, so a missing account does not answer faster than a
        # wrong password and leak the difference through timing.
        verify_password(request.password, hash_password("timing equaliser"))
        raise failure
    if not verify_password(request.password, row["password_hash"]):
        raise failure
    _set_session_cookie(response, sessions.create(int(row["id"])))
    return _public_user(row)


@app.post("/api/auth/logout", status_code=204)
def logout(
    response: Response,
    campus_customs_session: str | None = Cookie(default=None),
) -> None:
    sessions.destroy(campus_customs_session)
    response.delete_cookie(sessions.COOKIE_NAME, path="/")


@app.get("/api/auth/me", response_model=PublicUser | None)
def me(campus_customs_session: str | None = Cookie(default=None)) -> PublicUser | None:
    """Who is signed in, if anyone. Returns null rather than 401 so the front end can
    render a signed-out page without treating it as an error."""
    user_id = sessions.user_id_for(campus_customs_session)
    if user_id is None:
        return None
    row = get_user_by_id(user_id)
    return _public_user(row) if row else None


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
