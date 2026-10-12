# HW4 Harness

The engineering record for Homework 4: the data model, and as later problems land, the
Pydantic models, the agent's tools, the safety rules, and the specs. It grows by one section
per problem. The verbatim prompt history lives in [`../AI_prompts.md`](../AI_prompts.md);
this file explains the engineering behind it.

**Project:** a Campus Customs customer website with a helpful chatbot. Shoppers browse
products, create an account, chat about merch, see matching items appear on the page, and
get price and stock answers that come from the supplied database rather than from the model.

**Shared setup (all problems)**

| Item | Value |
|---|---|
| Front end | React + Vite, TypeScript |
| Backend | Python FastAPI; the agent is PydanticAI |
| Data | `campus_customs.db` (SQLite 3). Never committed. |
| Product images | `products/` beside the database. Never committed. |
| Model access | Portkey, through [`../app_config.py`](../app_config.py); key read from the workspace-root `.env`, server-side only |
| Main model | `gpt-5.6-luna` (`OPENAI_MODEL`); 5.6 or 6 series, with a stronger model available for harder agent steps |
| Runtime prompts | `../prompts/<name>.md`, loaded at runtime; never inlined in Python |
| Submission | pushed to a public GitHub repo; the repo URL goes on Canvas |
| Pre-submission check | `python3 check_submission.py hw4` (offline, no API calls) |

## Contents

- [Problem 2: The database](#problem-2-the-database)

---

## Problem 2: The database

**Source:** `campus_customs.db`, 172 KB, SQLite 3.50.4, read-only inspection with Python's
`sqlite3`. No model calls, so no Portkey credits. Nothing was written to the database.

Five tables: `catalogue`, `inventory`, `users`, `chat_messages`, and SQLite's internal
`sqlite_sequence` (autoincrement bookkeeping — not ours, never read it).

### `catalogue` — 102 products, one row each

| Field | Type | Why it matters |
|---|---|---|
| `product_id` | TEXT, primary key | Stable slug such as `basic-hoodie-big-yale`. The only safe way for the chatbot to refer to a product, and the key the front end uses to render a card. Also doubles as the image filename. |
| `name` | TEXT, not null | The display name a shopper reads on the page and in chat. Title-cased from the slug, so it reads a little mechanically (`2025 Yale Vs Harvard T Shirt`). |
| `garment_type` | TEXT, not null | The product category — but free text, and **messy** (see findings). Useful as a label, unreliable as a filter. |
| `description` | TEXT, not null | One sentence, 93–184 characters, describing colour, cut, and the graphic. The richest text in the database and the best grounding for "what does this look like" answers. |
| `colors` | TEXT holding a JSON array | The honest answer to "do you have this in pink?". Parse it; never string-match the raw text. 22 distinct colours across the catalogue. |
| `search_tags` | TEXT holding a JSON array | Curated keywords, 4–12 per product, 270 distinct. The primary surface for matching a shopper's words to products without spending a model call. |
| `image_file_path` | TEXT, not null | Relative path, always `products/<product_id>.jpg`. The backend resolves and serves it; the file itself is never committed. |
| `price` | REAL, not null | Whole dollars, no cents. The number the chatbot must read and never invent. |

### `inventory` — 612 rows, one per product-and-size

| Field | Type | Why it matters |
|---|---|---|
| `id` | INTEGER, primary key autoincrement | Row bookkeeping only. Nothing in the shop or the chat should refer to it. |
| `product_id` | TEXT, not null, FK → `catalogue` | Joins stock to the product. Every value resolves; there are no orphans. |
| `size` | TEXT, not null | One of XS, S, M, L, XL, XXL. Exactly six rows per product, so the grid is complete and a missing row means a bug, not a gap. |
| `quantity` | INTEGER, not null | Units on hand, 0–25. **Zero means out of stock in that size**, and that is the single fact the chatbot most needs to get right. |

`UNIQUE (product_id, size)` means one row per pair, so stock updates can upsert safely
rather than risking duplicate rows.

### `users` — 3 seeded accounts

| Field | Type | Why it matters |
|---|---|---|
| `id` | INTEGER, primary key autoincrement | The session identity, and what `chat_messages.user_id` points at. |
| `name` | TEXT, not null | Full display name. Redundant with `first_name` + `last_name` (see findings). |
| `email` | TEXT, not null, **unique** | The login identifier. The unique index is what makes "account already exists" a database answer rather than a race condition. |
| `password_hash` | TEXT, not null | Never leaves the backend. Format is `pbkdf2_sha256$<salt>$<64 hex chars>` — see findings, because it is not the format it looks like. |
| `created_at` | TEXT, not null, defaults to `datetime('now')` | `YYYY-MM-DD HH:MM:SS` in **UTC**, not local time. Matters for anything that displays an account age. |
| `first_name` | TEXT, nullable | Added later by `ALTER TABLE`. Lets the chatbot greet someone by first name instead of reciting their full name. |
| `last_name` | TEXT, nullable | Same addition. Nullable, so neither name field can be assumed present. |

### `chat_messages` — 22 rows, 11 exchanges

| Field | Type | Why it matters |
|---|---|---|
| `id` | INTEGER, primary key autoincrement | Chronological order. `created_at` has only second precision and a question and its answer share a timestamp, so `id` is the reliable sort key. |
| `user_id` | INTEGER, not null, FK → `users` | Scopes a conversation to one account. There is no anonymous-chat path in this schema. |
| `role` | TEXT, not null | `user` or `assistant`, evenly split. The shape PydanticAI and the OpenAI API both expect, so history can be replayed into the model directly. |
| `content` | TEXT, not null | The message text. The seeded assistant replies contain Markdown (`**$68**`, bullet lists), so the front end should render Markdown, not plain text. |
| `products_json` | TEXT, nullable | A JSON array of **whole product objects**, present on assistant rows only. This is how "matching items appear on the page" is meant to work. |
| `created_at` | TEXT, not null, defaults to `datetime('now')` | UTC timestamp for display and for ordering across sessions. |

### How the tables fit together

```text
catalogue ──1:6──> inventory        (product_id, one row per size)
users     ──1:N──> chat_messages    (user_id)
chat_messages.products_json ─ ─ ─>  a frozen copy of catalogue rows (no foreign key)
```

`products_json` is denormalised on purpose: it snapshots what the shopper was shown at the
time, so a later price change does not silently rewrite history. It also means a card
rendered from an old message can disagree with today's catalogue — the live price must be
re-read before anything is presented as current.

### Findings that change the design

1. **`garment_type` cannot be used as a filter.** 102 products carry 22 distinct spellings
   of roughly seven real categories: `hoodie` / `pullover hoodie` / `hooded sweatshirt` /
   `hooded pullover sweatshirt`, `quarter-zip pullover` / `quarter-zip pullover sweatshirt`,
   `jacket` / `fleece jacket` / `full-zip fleece jacket` / `bomber jacket`. One pair differs
   only by letter case: `short-sleeve t-shirt` (16) and `short-sleeve T-shirt` (6). A
   `WHERE garment_type = 'hoodie'` query returns 5 of the 27 hoodies. Matching has to be
   case-insensitive and substring-based, or go through `search_tags` instead.

   **Planned fix (not built yet).** A keyword rule collapses all 22 spellings into seven
   canonical categories with nothing left over — verified against the data, 102 of 102
   products mapped:

   | Canonical category | Products | Raw spellings it absorbs |
   |---|---|---|
   | Crewneck sweatshirt | 29 | `crewneck sweatshirt`, `crewneck`, `raglan crewneck sweatshirt`, `mockneck sweatshirt` |
   | Hoodie | 27 | `pullover hoodie`, `hoodie`, `full-zip hooded sweatshirt`, `hooded pullover sweatshirt`, `hooded sweatshirt` |
   | T-shirt | 25 | `short-sleeve t-shirt`, `short-sleeve T-shirt`, `heavyweight short-sleeve t-shirt`, `short-sleeve crew-neck t-shirt`, `t-shirt` |
   | Quarter-zip | 11 | `quarter-zip pullover sweatshirt`, `quarter-zip pullover` |
   | Fleece jacket | 6 | `full-zip fleece jacket`, `fleece jacket` |
   | Jacket | 2 | `bomber jacket`, `jacket` |
   | Long-sleeve shirt | 2 | `long-sleeve performance shirt`, `men's long-sleeve performance shirt` |

   This is a read-time lookup in code, not a database change: the raw `garment_type` stays
   untouched and is still what gets displayed on a product, while the canonical label drives
   filtering and browse-by-category. Nothing is written to the supplied database, and the
   mapping is deterministic plumbing — no model call, so it costs nothing to run. It lands
   with the problem that first needs category filtering rather than now.

2. **There are only seven prices, and none of them carry cents.** $32 (25 products), $45
   (5), $58 (28), $68 (23), $72 (11), $88 (2), $98 (8). Checked explicitly: 0 of 102
   products have a non-zero cents component. Useful for "what's under $50" questions, and a
   cheap sanity check — a quoted price outside those seven is a bug.

   Price does **not** follow from the category: hoodies run $45–$88 and crewnecks $45–$58,
   so a price must always be read per product, never inferred from what kind of garment it
   is.

   `price` is stored as SQLite `REAL`, a float. These particular values are exactly
   representable so nothing is wrong today, but money in floats goes bad once cents and
   multi-item totals arrive. **Decision:** read `price` as stored, never round or truncate
   it, and format it at the display boundary with two decimals (`$68.00`), so that if the
   catalogue ever gains cents the full price shows automatically and nothing has to change.
   Any future arithmetic (a cart total) uses integer cents or `Decimal`, not floats. Note
   the seeded assistant replies write prices as `**$68**`; that is the fixture's style, not
   a requirement.

3. **`colors` and `search_tags` are JSON arrays stored as TEXT.** Every row parses cleanly,
   but naive `LIKE '%navy%'` matching against the raw string works by accident and will
   eventually embarrass us. Parse with `json.loads`, or use SQLite's `json_each`.

4. **Three products have an empty `colors` array**: `benjamin-franklin-t-shirt`,
   `berkeley-sweater-fleece-jacket`, `timothy-dwight-college-crewneck`. Their colours are
   described in prose in `description` but not listed as data. The chatbot must say it does
   not have colour information for these rather than inferring it from the description or
   the photo.

5. **The password hashes are not in the format they appear to be.** The prefix says
   `pbkdf2_sha256`, which looks like Django, but Django's format has four
   `$`-separated fields including the iteration count. These have **three**: algorithm,
   salt, and a 64-character hex digest. The iteration count is not stored anywhere, so
   there is no way to recompute these hashes correctly, and we do not have the plaintext
   passwords either. **The three seeded accounts therefore cannot be logged into.** The test
   account's salt is also a fixed, human-readable string rather than a random one, which is
   a fixture smell worth not copying.

6. **`products_json` appears on all 11 assistant rows and no user rows**, sometimes as an
   empty array. The seeded data is telling us the intended contract: every assistant turn
   returns a product list, which may legitimately be empty, and the front end renders it.

7. **`users.name` duplicates `first_name` + `last_name`.** The split columns were added
   later by `ALTER TABLE` and are nullable, so `name` is the only field guaranteed to be
   populated. Write all three on signup; read `first_name` with a fallback to `name`.

8. **Stock is realistic, not uniform.** 145 of 612 size rows are zero — about 24%, spread
   evenly across sizes — but no product is out of stock in every size. So "we have it, but
   not in your size" is a common case the chatbot has to handle gracefully, and it will come
   up in testing naturally rather than needing to be staged.

### Decisions

All three questions raised by this analysis were settled by Christine on 2026-10-11.

**D1. Authentication — leave the seeded accounts alone, build signup fresh.**

The three seeded rows stay exactly as they are: readable, browsable, and still the owners of
the 22 seeded `chat_messages`. We do not guess their iteration count and we do not re-hash
them. New accounts are hashed with **Argon2id** through `pwdlib[argon2]`, which embeds its
own random salt per password.

Consequences to build for:

- A seeded account's stored hash is not a valid `pwdlib` hash, so verification will raise
  rather than return `False`. Login must catch that and return the same generic
  "invalid email or password" as any other failure — never a 500, and never a message that
  reveals which accounts are legacy. That would be a user-enumeration oracle.
- Signup still reports a duplicate email plainly, because a signup form that hides it is
  unusable. That is the standard trade-off and it is deliberate.
- No password, hash, or salt is ever logged, returned by an endpoint, or written to the
  harness or the prompt log.

**D2. Chat memory — persisted for signed-in users, never for anonymous ones.**

Signed-in: each turn appends a `user` row and an `assistant` row (with `products_json`) to
`chat_messages`, and the agent loads recent history for that `user_id` as context. History
survives logout and follows the account.

Anonymous: history lives only in the browser tab's memory for that page session. **No
cookie, no IP address, no device fingerprint, and no row written.** Christine's reasoning,
recorded as given: tracking signed-out visitors is off-putting and users dislike it. Closing
or reloading the tab discards it, and the chat panel should say so plainly — something like
"Sign in to keep your chat history" — rather than letting someone lose a conversation they
assumed was saved.

Two things that follow:

- **The schema already enforces this.** `chat_messages.user_id` is `NOT NULL` with a foreign
  key to `users`, so an anonymous conversation cannot be written without altering the
  supplied schema. No extra guard is needed; the database refuses on its own.
- **History is a recurring cost.** Everything replayed into the model is re-sent and re-paid
  on every turn, so the agent loads a bounded slice — the most recent few exchanges — not a
  user's entire history. The cap gets a number and a justification when the agent is built.

A signed-in user should be able to clear their own history. Pre-login messages are *not*
back-filled into the account on sign-in; they were never persisted, and retroactively saving
them would undo the point of D2.

**D3. Category labels — standardise at read time, later.**

The seven-category mapping in finding 1 is approved in principle. It lands with the first
problem that needs category filtering, as a read-time lookup in code: the raw `garment_type`
stays in the database untouched and still displays on the product page, while the canonical
label drives filtering and browse-by-category.
