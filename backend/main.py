"""Campus Customs API.

Problem 3 scope: serve the product catalogue and the product images to the front end.
Problem 5 grows this into the agent backend, so the chat route is declared here as an
explicit stub rather than being left out.
"""
from __future__ import annotations

import logging
import sqlite3
from dataclasses import asdict

from fastapi import Cookie, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_ai.exceptions import ModelHTTPError

import sessions
from agent import MAX_HISTORY_MESSAGES, build_agent, model_name
from auth import hash_password, verify_password
from db import (
    EmailAlreadyRegistered,
    create_user,
    get_inventory,
    get_product,
    get_user_by_email,
    get_user_by_id,
    image_path,
    list_products,
    recent_messages,
    save_exchange,
)

logger = logging.getLogger("campus_customs")

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
    saved: bool = False


@app.get("/api/health")
def health() -> dict[str, object]:
    """Cheap readiness check. Proves the database is reachable and reports the model the
    assistant is configured to use. Makes no model call."""
    return {
        "status": "ok",
        "products": len(list_products()),
        "model": model_name(),
    }


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
async def chat(
    request: ChatRequest,
    campus_customs_session: str | None = Cookie(default=None),
) -> ChatReply:
    """Ask the shop assistant.

    The agent returns product **ids**; the cards are built here from catalogue rows, so
    every price, colour and image on the page came out of the database rather than out of
    the model.

    Persistence follows decision D2: a signed-in shopper's turns are written to
    `chat_messages`, and a signed-out visitor's are not stored at all.
    """
    user_id = sessions.user_id_for(campus_customs_session)
    history = recent_messages(user_id, MAX_HISTORY_MESSAGES) if user_id else []

    try:
        agent = build_agent()
        result = await agent.run(request.message, message_history=history)
        answer = result.output
        # Token usage per exchange, so spend is measurable rather than guessed at.
        # One shopper question is several model calls: one to pick a tool, another to
        # answer once the result comes back. The instructions and tool schemas are
        # re-sent on each of those, which is where most of the input tokens go.
        try:
            # `usage` is a property in pydantic-ai 2.x, not a method.
            usage = result.usage
            logger.info(
                "chat usage: requests=%s input=%s output=%s total=%s",
                usage.requests,
                usage.input_tokens,
                usage.output_tokens,
                usage.total_tokens,
            )
        except Exception:  # noqa: BLE001 - never let accounting break a reply
            logger.debug("usage unavailable for this run")
    except ModelHTTPError as exc:
        # Azure's content filter rejects some messages before the model ever sees them,
        # jailbreak-shaped ones especially. That is a refusal, not an outage, so answer
        # like a refusal instead of showing the shopper a broken site. These cost no
        # tokens, since nothing was generated.
        if "content_filter" in str(exc.body or "").lower():
            logger.info("provider content filter refused a message")
            # Deliberately NOT saved to chat_messages. A filtered message would be
            # replayed as context on every later turn, so storing it would re-trigger
            # the filter and break the conversation from then on.
            return ChatReply(
                reply=(
                    "I can't help with that one. I'm here for Campus Customs merchandise "
                    "— ask me about a style, a size, or what we have in stock."
                ),
                products=[],
                saved=False,
            )
        logger.exception("the model request failed")
        raise HTTPException(
            status_code=503,
            detail="The shop assistant is unavailable right now. Please try again.",
        ) from exc
    except Exception as exc:  # noqa: BLE001 - surfaced as one clean line, logged in full
        logger.exception("chat failed")
        raise HTTPException(
            status_code=503,
            detail="The shop assistant is unavailable right now. Please try again.",
        ) from exc

    # Resolve ids against the catalogue. Anything the model made up is dropped rather
    # than shown, and the drop is logged so a prompt problem is visible.
    cards: list[dict] = []
    for product_id in answer.product_ids:
        found = get_product(product_id)
        if found is None:
            logger.warning("agent returned unknown product_id %r", product_id)
            continue
        cards.append({k: v for k, v in asdict(found).items() if k != "search_tags"})

    saved = False
    if user_id:
        save_exchange(user_id, request.message, answer.reply, cards)
        saved = True

    return ChatReply(reply=answer.reply, products=cards, saved=saved)
