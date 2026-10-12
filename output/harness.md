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
- [Problem 3: The website](#problem-3-the-website)
- [Problem 4: Accounts and login](#problem-4-accounts-and-login)

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
   salt, and a 64-character hex digest. The test account's salt is also a fixed,
   human-readable string rather than a random one, which is a fixture smell worth not
   copying.

   > **Superseded in Problem 4.** This finding originally concluded that the seeded
   > accounts could not be logged into, since the iteration count cannot be recovered from
   > the string. The count is not missing — the assignment specifies it (120,000) rather
   > than storing it. Verified against the seeded row. The accounts work; see
   > [Problem 4](#problem-4-accounts-and-login).

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
*(Partly superseded in Problem 4 — see below.)*

The three seeded rows stay exactly as they are: readable, browsable, and still the owners of
the 22 seeded `chat_messages`. We do not re-hash them.

> **Superseded:** the Argon2id half of this decision is void. It rested on the seeded
> hashes being unverifiable, which Problem 4 disproved. The assignment specifies
> PBKDF2-HMAC-SHA256 at 120,000 iterations and requires signup and login to share
> settings, so **both** paths use PBKDF2 and `pwdlib[argon2]` was dropped from
> `requirements.txt`. There is no legacy-hash branch, because there is no legacy format.

What survives unchanged:

- Signup reports a duplicate email plainly, because a signup form that hides it is
  unusable. Login stays deliberately vague for the opposite reason.
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

---

## Problem 3: The website

**Built:** a React + Vite + TypeScript storefront and the FastAPI backend that feeds it.
No model calls anywhere in this problem, so no Portkey credits were spent.

### Shape of it

```text
backend/
  main.py     FastAPI routes
  db.py       read-only SQLite access
frontend/src/
  App.tsx            routing, layout, footer
  api.ts             every call to the backend, and price formatting
  types.ts           the shapes the API returns
  components/        NavBar, ProductCard, ChatPanel
  pages/             Home, Products, ProductDetail, About, LogIn, CreateAccount
```

### The API

| Route | Returns |
|---|---|
| `GET /api/health` | Status plus the product count, which also proves the database is reachable |
| `GET /api/products` | All 102 products for the grid |
| `GET /api/products/{id}` | One product with search tags and stock for all six sizes |
| `GET /api/products/{id}/image` | The product photo as JPEG |
| `POST /api/chat` | Stub until Problem 5, answering in the shape the agent will use |

Three decisions worth recording:

1. **Images are served by product id, not by path.** `catalogue.image_file_path` is data,
   and a route that takes a filename is a path-traversal invitation. `db.image_path()`
   looks the row up, resolves the path, and refuses anything that does not land inside the
   image folder. Verified: a product id of `../../etc/passwd` returns `None`, and the route
   answers 404.
2. **The database is opened read-only** (`file:...?mode=ro`). Nothing in this project can
   write to the supplied data, by construction rather than by discipline.
3. **The chat stub returns the real response shape** — a reply plus a product list — so
   Problem 5 replaces the implementation without the front end changing.

### The front end

- **Vite proxies `/api` to the backend**, so the browser sees one origin. No CORS dance, no
  backend URL in the bundle, and — the point that matters — no path by which a Portkey key
  could end up in client code.
- **Prices format with two decimals** via `formatPrice`, per the Problem 2 decision.
- **Size order is XS, S, M, L, XL, XXL**, fixed in `db.SIZE_ORDER`. Sorting alphabetically
  would have read L, M, S, XL, XS, XXL.
- **Out-of-stock sizes are struck through and labelled "out"** rather than hidden, so a
  shopper learns their size is gone on the page instead of at checkout.
- **Products with no recorded colours say so.** The three products from finding 4 render
  "We do not have colours recorded for this item" rather than inferring a colour.
- **The chat panel tells signed-out visitors their chat is not saved**, which is decision
  D2 surfaced in the interface rather than left as a silent backend behaviour.
- **Accounts are deliberately inert.** The Log In and Create Account forms are laid out and
  labelled but disabled, and say so. Nothing typed into them is stored or sent, because
  authentication has not been built yet.

### Voice and research

`yalebulldogblue.com` was read once for what the business is, what it sells, and how its
navigation is organised. **No sentence, heading, or asset was copied.** The page copy here
is written in Christine's voice — direct, informational, conversational, and aimed at what
the reader is trying to do.

The copy is also grounded in our own catalogue rather than invented: 102 styles, XS–XXL,
$32–$98, and the residential colleges, varsity teams and graduate schools that actually
appear in `search_tags`. One fact came from the research and nothing else did: the store
address, 57 Broadway, New Haven.

### Look

The workspace's warm editorial theme — cream ground, deep ink type, one restrained accent —
with the accent set to **navy** rather than the default plum, since the catalogue is Yale
apparel. It is one token (`--color-accent` in `src/index.css`) if that should change.

### Verification

All offline. Nothing here spends credits.

| Check | Result |
|---|---|
| `tsc -b && vite build` | Clean. 34 modules, 281 kB JS, 18.6 kB CSS |
| Backend imports and reads | 102 products, inventory in catalogue size order |
| Path traversal guard | `image_path('../../etc/passwd')` → `None`; route 404s |
| `/api/health` | `{"status": "ok", "products": 102}` |
| Products page | 102 cards rendered, 102 images loaded, **0 broken** |
| Product detail | `$32.00` two-decimal price, image 900×900, sizes in catalogue order |
| Empty-colours path | Benjamin Franklin T Shirt shows the "not recorded" message |
| Out-of-stock path | Champion Reverse Weave Crewneck: 4 sizes struck through, "In stock in 2 of 6 sizes" |
| Missing product | 404 |
| Empty chat message | 422 from Pydantic validation |
| Chat stub round trip | Message sent, stub reply rendered in the panel |
| Browser console | No errors except the two deliberate negative tests above |
| Mobile, 375×812 | No horizontal overflow, grid collapses to one column, chat panel fits |

### 3.1 Selecting colours and sizes

Christine asked why neither colours nor sizes could be selected on a product page. The two
turned out to have opposite answers.

**Colours are not options, and offering them would be a lie.** `colors` lists the colours
*present in the garment's design*, not colourways you can order. The Boola Boola T Shirt is
a navy shirt with white-and-gray lettering, so its array is `["navy", "white", "gray"]`.
The Branford quarter-zip is heather gray with a multicolour crest, so it carries green and
yellow. Two independent confirmations: `inventory` is keyed by `(product_id, size)` with
**no colour column**, and there is exactly one image per product. A colour picker would
have implied the Branford comes in green.

The real defect was presentational — colours were rendered as pill badges that looked
exactly like selectable chips, which is what invited the click. They now read as a
sentence under the heading "Colours in this design", ending with "This item comes in the
one colourway shown."

**Sizes are a real variant, so they are now selectable.** They had been `<li>` elements,
which gave a text cursor on hover and a native `title` tooltip — Christine caught both.
They are now real `<button>` elements:

- in-stock sizes get a pointer cursor, a hover state, `aria-pressed`, and keyboard focus;
- out-of-stock sizes stay visible but `disabled`, struck through, with a not-allowed cursor;
- clicking a selected size again clears it;
- the native `title` tooltip is gone, replaced by an `aria-label` carrying the stock count.

Selecting a size reveals its exact stock and a button that opens the chat panel with the
question already written — "Is the Big Yale Tri Blend T Shirt still available in size M?".
That handoff runs through `ChatContext`, so the product page never reaches into the panel's
internals. **Decision:** no cart. The assignment does not ask for checkout, and a size
control that leads to a bag we cannot fill would be the same kind of lie as the colour
picker. Handing the question to the assistant is the honest use of a selected size.

Verified in the browser: all six size controls are `BUTTON`; cursors are `pointer` when in
stock and `not-allowed` when not; no `title` attributes remain; selecting M shows
"Size M — 15 in stock"; the ask button opens the panel, pre-fills the question and focuses
the input; clicking M again sets `aria-pressed` back to false. Clean `tsc -b && vite build`.

### 3.2 Spec coverage audit

Checked each line of the Problem 3 prompt against the running site rather than against the
source, by driving the real pages in a browser.

| Spec | Evidence |
|---|---|
| React + Vite + TypeScript | Clean `tsc -b && vite build` |
| Nav bar: Home, Products, About Us, Log In, Create Account | All five links clicked in sequence; each routes and renders real content |
| Home and About Us in Christine's voice, not copied | Written fresh from our own catalogue counts and tags; the store address is the only researched fact |
| Card shows catalogue image, name, price, short description | `src` is `/api/products/{id}/image`, resolved from `catalogue.image_file_path`; description clamps to 3 lines |
| Card click opens the single-item page | Real click on the Benjamin Franklin 1/4 Zip card landed on `/products/benjamin-franklin-1-4-zip` |
| Large image on the **left**, text on the other side | At 1280×900: image x=85–619, text starts x=660, tops aligned |
| Detail page shows description, price, sizes/stock | Plus colours, search tags, and selectable sizes |
| Floating chat panel, bottom right, stub | Posts to `/api/chat` and renders the reply |
| FastAPI in `backend/main.py` serving products and images | Five routes, read-only database access |

**One finding worth keeping.** The image-on-left assertion first failed. The cause was not
the layout but the measurement: the preview pane is narrower than the `lg` breakpoint
(1024px), where the two-column grid intentionally stacks to image-above-text. Re-measured
at 1280×900 it passes. Christine reviewed the stacking behaviour and approved it, so the
breakpoint stays at `lg`; moving it to `md` would put the columns side by side on tablets.

Worth remembering as a method note: a layout assertion measured at one viewport says
nothing about another, and a responsive layout can look broken to a test that never
checked which breakpoint it was in.

### Still open after this problem

- Accounts do nothing yet; the forms are disabled placeholders. *(Built in Problem 4.)*
- The chat route is a stub. Problem 5 replaces it with the PydanticAI agent, which will
  receive the pre-filled size questions this page now sends.
- Category filtering (D3) is not built, so the Products page lists all 102 unfiltered.

---

## Problem 4: Accounts and login

### Correction to Problem 2, finding 5 — and to decision D1

Problem 2 concluded that the seeded accounts **could not be logged into**, because their
`pbkdf2_sha256$salt$hash` records hold only three fields and omit the iteration count that
Django's four-field format carries. That reasoning was right about the format and wrong
about the conclusion: the iteration count is not missing, it is simply **not stored**. The
assignment specifies it.

Christine supplied the parameters: **PBKDF2-HMAC-SHA256, 120,000 iterations**, stored as
`pbkdf2_sha256$salt$hash`, with `password` as the test account's password. Verified
against the seeded row before any code was written — 120,000 matches; 100,000, 260,000 and
600,000 all fail. So the seeded accounts work, and **D1 is superseded**: there is no
Argon2id path and no "legacy hashes cannot verify" case to handle.

### What is stored for a user

The supplied `users` table, unchanged — no columns were added.

| Column | What goes in it | Why |
|---|---|---|
| `id` | autoincrement | Session identity, and the owner of `chat_messages` rows |
| `name` | `"First Last"` | NOT NULL and predates the split columns, so it is always written |
| `first_name`, `last_name` | as typed, trimmed | Lets the site greet someone by first name |
| `email` | lower-cased, trimmed | The login identifier. Its unique index is what makes "already registered" a database answer rather than a check-then-insert race |
| `password_hash` | `pbkdf2_sha256$salt$digest` | Never leaves the backend |
| `created_at` | `datetime('now')` | UTC, by the table's own default |

**What is never stored:** the password itself, in any form that can be read back. There is
no plaintext column, no reversible encryption, and no recovery path — a forgotten password
would have to be reset, not retrieved. Verified against the new row: the plaintext does not
appear in it.

### How passwords are protected

One module, [`backend/auth.py`](../backend/auth.py), with one set of constants. Both signup
and login call into it. That is deliberate: if the two paths ever used different settings,
a correct password would stop matching, so there is only one place for them to disagree and
a test that fails if they do.

- **PBKDF2-HMAC-SHA256, 120,000 iterations.** Slow on purpose. The cost is paid once per
  login by a user and a few hundred thousand times over by anyone grinding a stolen table.
- **A unique random salt per password**, from `secrets.token_hex(16)` — 32 hex characters.
  Generated at signup only. Salts are not secret; their job is to make identical passwords
  produce different hashes, which is what makes precomputed rainbow tables useless.
  Verified: all four salts in the table are distinct.
- **Login never reverses the stored value**, because it cannot. It splits the record, takes
  the salt **out of the middle of the stored string**, re-derives with the same settings,
  and compares.
- **Constant-time comparison** via `hmac.compare_digest`, so the check takes the same time
  whether the first character differs or the last. A byte-by-byte `==` leaks how much of a
  guess was right, which is enough to recover a digest one character at a time.
- **Malformed records fail closed.** A record that is not three fields, or carries a
  different algorithm, returns `False` rather than raising — a 500 on a damaged row would
  itself confirm that the account exists.
- **Nothing is logged, returned, or rendered.** The `PublicUser` model is an allow-list of
  id, name, email; `password_hash` is not on it and must not be added. Verified: neither
  the login nor the signup response contains the string `pbkdf2`.

**A note on the house rule.** `AGENT.MD` prefers Argon2id and treats PBKDF2 as the weakest
acceptable choice. The assignment mandates PBKDF2-HMAC-SHA256 at 120,000 iterations and
requires signup and login to share settings, so using Argon2id for new accounts would
break exactly the thing the problem warns about. The assignment wins. Worth recording that
OWASP's current guidance for PBKDF2-HMAC-SHA256 is on the order of 600,000 iterations, so
120,000 is the assignment's number rather than today's recommended one.

### How the session works

- On successful signup or login the backend mints a random opaque token
  (`secrets.token_urlsafe(32)`) and sets it as an **HttpOnly** cookie, `SameSite=Lax`.
  HttpOnly means JavaScript cannot read it, so cross-site scripting cannot steal the
  session. Verified: `document.cookie` does not contain it.
- The token is meaningless by itself — it is a key into a server-side map in
  [`backend/sessions.py`](../backend/sessions.py). Nothing about the user travels in it.
- The store is in memory, so sessions end when the server restarts. Honest for coursework;
  a real deployment needs a shared store with expiry. `secure=False` for `http://localhost`
  and must be `True` behind HTTPS.
- This does not contradict **D2**. The cookie appears only after someone chooses to log in.
  A signed-out visitor still gets no cookie, no IP logging, and no fingerprint.

### Two places the design deliberately differs

**Login is vague; signup is specific.** A failed login says "Invalid email or password"
whether the address is unknown or the password is wrong — same status, same words — so the
endpoint cannot be used to discover which addresses have accounts. Signup does the
opposite and says plainly that an email is taken, because a signup form that hides it is
unusable. That asymmetry is intentional.

**A missing account still pays the hashing cost.** `login` hashes a throwaway value when
no user is found, so an unknown email does not answer measurably faster than a wrong
password. Without it, the timing difference is itself an account oracle.

### Writes to the supplied database

Problem 3 opened the database read-only. Accounts have to be written somewhere, so
`db.connect_rw()` now exists — used **only** for `users` (and later `chat_messages`).
Catalogue and inventory reads still go through the read-only `connect()`, so product data
cannot be modified even by accident.

### Verification

Offline except for the local servers. No model calls, so no Portkey credits.

**Unit checks** — `.venv/bin/python tests/test_auth.py`, 19 checks, all passing:

| Group | What it proves |
|---|---|
| Stored format | Three `$` fields, `pbkdf2_sha256`, 64-hex digest |
| Round trip | Correct verifies, wrong and empty rejected |
| Salt handling | Two hashes of the same password differ, salts differ, both verify |
| **Signup and login agree** | Iteration count is 120,000, and an independent re-derivation from the stored salt matches the stored digest |
| Malformed records | Six bad shapes all return `False` without raising |
| Seeded format | A seeded-style record verifies through the same code path |

**End-to-end**, driven in the browser against the running servers:

| Check | Result |
|---|---|
| Log in as `test@campuscustoms.yale.edu` / `password` | 200, returns Test User |
| Session survives via cookie (`/api/auth/me`) | Returns the user |
| Cookie readable by JavaScript | **No** — HttpOnly |
| Login response contains a hash | **No** |
| Wrong password | 401, "Invalid email or password." |
| Unknown account | 401, **identical** status and message |
| Signup with mismatched confirmation | 422, rejected server-side as well as in the form |
| Signup with a 5-character password | 422 |
| Signup, valid | 201, account created, signed in |
| Duplicate email | 409, "An account with that email already exists." |
| **Signup → log out → log in again** | 200 — the proof that both paths use the same settings |
| Stored row for the new account | `pbkdf2_sha256`, 32-char salt, 64-char digest, re-derives at 120,000, no plaintext |
| All salts in the table distinct | Yes |
| Log in through the form | Lands on Products, nav shows "Hi, Test" and Log out |
| Sign up through the form | Lands on Products, nav shows "Hi, Christine" |
| Mismatched passwords in the form | Inline error, submit disabled |
| Chat notice when signed in | "Signed in as Test." instead of the not-saved warning |
| Browser console | Only the deliberate 401/422/409 negative tests |

### Still open after this problem

- Two accounts created during testing are in the `users` table (ids 4 and 5) and can be
  deleted on request; they were left in place rather than removed unasked.
- Sessions do not survive a backend restart, and there is no expiry or "log out everywhere".
- There is no password reset, no rate limiting on login attempts, and no email
  verification. None are asked for by the assignment; all three would matter in production.
- `chat_messages` is not yet written. Problem 5 wires the agent, and D2's persistence for
  signed-in users lands with it.
