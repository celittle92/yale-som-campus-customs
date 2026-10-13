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
from pydantic_ai.exceptions import ModelHTTPError

import sessions
from agent import MAX_HISTORY_MESSAGES, build_agent, model_name
from auth import hash_password, verify_password
from models import (
    ChatHistoryMessage,
    ChatReply,
    LoginRequest,
    ChatRequest,
    ProductDetail,
    ProductSummary,
    PublicUser,
    ShopperContext,
    SignupRequest,
)
from db import (
    EmailAlreadyRegistered,
    all_stock,
    clear_messages,
    clear_recently_viewed,
    create_user,
    ensure_schema,
    get_inventory,
    get_product,
    get_user_by_email,
    get_user_by_id,
    image_path,
    list_products,
    recent_messages,
    recently_viewed,
    record_view,
    save_exchange,
    stored_messages,
)
from tools import similar_products

logger = logging.getLogger("campus_customs")

# The one additive table this app owns. Safe to call repeatedly.
ensure_schema()

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
        {k: v for k, v in asdict(p).items()
         if k not in ("search_tags", "has_written_description")}
        for p in list_products()
    ]


@app.get("/api/products/{product_id}", response_model=ProductDetail)
def product(
    product_id: str,
    campus_customs_session: str | None = Cookie(default=None),
) -> dict:
    found = get_product(product_id)
    if found is None:
        raise HTTPException(status_code=404, detail="No such product")
    # Opening a product page is the view that "recently viewed" records. Signed-in only.
    user_id = sessions.user_id_for(campus_customs_session)
    if user_id is not None:
        record_view(user_id, product_id)
    payload = {k: v for k, v in asdict(found).items() if k != "has_written_description"}
    return {**payload, "sizes": get_inventory(product_id)}


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


@app.get("/api/stock")
def stock_map() -> dict[str, dict[str, int]]:
    """Stock for every product and size, as `{product_id: {size: quantity}}`.

    One small request lets the Products page filter by size and hide sold-out items
    instantly in the browser, instead of 102 round trips or a server call per keystroke.
    """
    return all_stock()


@app.get("/api/products/{product_id}/similar", response_model=list[ProductSummary])
def similar(product_id: str, limit: int = 8) -> list[dict]:
    """Products like this one, for the "You might also like" row."""
    if get_product(product_id) is None:
        raise HTTPException(status_code=404, detail="No such product")
    out: list[dict] = []
    for match in similar_products(product_id, limit):
        full = get_product(match.product_id)
        if full is not None:
            out.append({k: v for k, v in asdict(full).items()
                        if k not in ("search_tags", "has_written_description")})
    return out


@app.post("/api/recently-viewed/{product_id}", status_code=204)
def note_view(
    product_id: str,
    campus_customs_session: str | None = Cookie(default=None),
) -> None:
    """Record that a signed-in shopper opened a product.

    Guests are a deliberate no-op: their list lives in their own browser and is never
    sent here. See output/usability.md.
    """
    user_id = sessions.user_id_for(campus_customs_session)
    if user_id is None:
        return
    if get_product(product_id) is None:
        raise HTTPException(status_code=404, detail="No such product")
    record_view(user_id, product_id)


@app.get("/api/recently-viewed", response_model=list[ProductSummary])
def get_recently_viewed(
    campus_customs_session: str | None = Cookie(default=None),
) -> list[dict]:
    user_id = sessions.user_id_for(campus_customs_session)
    if user_id is None:
        return []
    out: list[dict] = []
    for product_id in recently_viewed(user_id):
        found = get_product(product_id)
        if found is not None:
            out.append({k: v for k, v in asdict(found).items()
                        if k not in ("search_tags", "has_written_description")})
    return out


@app.delete("/api/recently-viewed", status_code=204)
def delete_recently_viewed(
    campus_customs_session: str | None = Cookie(default=None),
) -> None:
    user_id = sessions.user_id_for(campus_customs_session)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Log in to manage this.")
    clear_recently_viewed(user_id)


def _shopper_context(user_id: int | None, page_path: str | None) -> ShopperContext:
    """Build the agent's view of the shopper, server-side.

    The browser reports only a path. Who they are comes from the session cookie, and
    what that path means is resolved here against the catalogue — so neither the
    identity nor the product data can be forged by a crafted request body.
    """
    context = ShopperContext(page_path=page_path)

    if user_id is not None:
        row = get_user_by_id(user_id)
        if row is not None:
            context.signed_in = True
            context.first_name = row["first_name"]
            context.full_name = row["name"]
            context.email = row["email"]
            # Names, not ids: the agent reads these, and a name is what a shopper
            # would say. It searches to get the id back when it needs one.
            seen = []
            for product_id in recently_viewed(user_id):
                found = get_product(product_id)
                if found is not None:
                    seen.append(found.name)
            context.recently_viewed = seen

    # "/products/<id>" is the only path that carries meaning for the agent.
    if page_path and page_path.startswith("/products/"):
        product_id = page_path.removeprefix("/products/").strip("/")
        found = get_product(product_id) if product_id else None
        if found is not None:
            context.viewing_product_id = found.product_id
            context.viewing_product_name = found.name

    return context


@app.get("/api/chat/history", response_model=list[ChatHistoryMessage])
def chat_history(
    campus_customs_session: str | None = Cookie(default=None),
) -> list[dict[str, object]]:
    """A signed-in shopper's saved conversation, so the panel can show it on return.

    Guests get an empty list — nothing was ever stored for them.
    """
    user_id = sessions.user_id_for(campus_customs_session)
    return stored_messages(user_id) if user_id else []


@app.delete("/api/chat/history", status_code=204)
def delete_chat_history(
    campus_customs_session: str | None = Cookie(default=None),
) -> None:
    """Let a shopper erase their own conversation. Theirs to delete, per decision D2."""
    user_id = sessions.user_id_for(campus_customs_session)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Log in to manage your chat.")
    removed = clear_messages(user_id)
    logger.info("cleared %s stored messages for user %s", removed, user_id)


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
    deps = _shopper_context(user_id, request.page_path)

    try:
        agent = build_agent()
        result = await agent.run(request.message, message_history=history, deps=deps)
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
        cards.append(
            {k: v for k, v in asdict(found).items()
             if k not in ("search_tags", "has_written_description")}
        )

    saved = False
    if user_id:
        save_exchange(user_id, request.message, answer.reply, cards)
        saved = True

    return ChatReply(
        reply=answer.reply,
        products=cards,
        # Only meaningful when there is something to label.
        match_label=answer.product_match_label if cards else None,
        saved=saved,
    )
