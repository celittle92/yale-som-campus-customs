# Campus Customs

A customer website for Campus Customs, a shop selling officially licensed Yale apparel in
New Haven. React + Vite + TypeScript front end, Python FastAPI backend, and a shopping
assistant built on PydanticAI over the shop's own SQLite catalogue.

Shoppers browse the catalogue, create an account, and chat with an assistant that answers
price and stock questions **from the database** and makes matching products appear on the
page. It cannot invent a price: the agent returns product *ids*, and the backend resolves
each one against the catalogue.

Coursework for Yale SOM, AI Foundations, Homework 4.

## Layout

```text
hw4/
├── AI_prompts.md              # the prompt log, one section per problem
├── requirements.txt
├── .env.example               # variable names only, no values
├── .gitignore
├── README.md
├── frontend/                  # Vite React TypeScript app
├── backend/
│   ├── main.py                # FastAPI app — run with: uvicorn main:app --reload --port 8000
│   ├── agent.py               # the agent, wiring only
│   ├── models.py              # structured types in and out of the model
│   ├── tools.py               # the six read-only catalogue tools
│   └── prompts/
│       └── prompt.md          # system prompt, read from disk at runtime
└── output/
    ├── harness.md             # the engineering record — read this one
    ├── design.md
    ├── usability.md
    ├── app_check.html         # screenshots of the running site
    ├── app_check_images/
    └── audit_trail.json       # append-only record of every agent turn
```

The agent itself is the four files under `backend/`: `prompts/prompt.md`, `agent.py`,
`tools.py`, `models.py`. The other backend modules are the website around it — database
access, authentication, sessions, image handling and the audit trail.

**[`output/harness.md`](output/harness.md)** is the one document to read. It covers the
data model, every Pydantic field and why it is shaped that way, the tools, the safety
rules, and the full specification.

## 1. Get the data pack

**The database and the product photos are not in this repository.** The assignment
forbids committing them and this repo is public, so you need to add them yourself. You
need `campus_customs.db` and the `products/` folder of 102 JPEGs.

Put them together in a folder called `data`, inside `hw4/`:

```text
hw4/
├── backend/
├── frontend/
├── output/
└── data/                      # not in git
    ├── campus_customs.db
    └── products/
        ├── basic-hoodie-big-yale.jpg
        └── ...
```

That is the layout the assignment specifies, and it is what the backend looks for first.

If your copy is somewhere else, it will still be found: the backend checks each folder
above itself for one named `data` or `data hw4`, so beside `hw4/`, beside the repo, or a
level further up all work too. To put it anywhere else, set `CAMPUS_CUSTOMS_DATA` to the
folder holding `campus_customs.db`. If it cannot find the database, the error lists every
folder it checked.

Nothing in this project writes to the catalogue or the inventory — those connections are
opened read-only. Accounts and chat history are written to the same file, because that is
where the assignment puts them.

## 2. Add your API key

```bash
cp .env.example .env
```

Then fill in `PORTKEY_API_KEY`. It is read server-side only and never reaches the browser:
the front end talks to this backend, and the backend talks to Portkey.

Never put a key in a `VITE_`-prefixed variable. Vite compiles those into the browser
bundle, where anyone can read them.

The site, the catalogue and accounts all work without a key — only the chat assistant
needs one.

## 3. Run the backend

From **`hw4/`**, one time:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Then, from **`hw4/backend/`**:

```bash
../.venv/bin/python -m uvicorn main:app --reload --port 8000
```

Check it came up: <http://localhost:8000/api/health> should report `"status": "ok"` and
`"products": 102`. If it reports that the database was not found, it will list every
folder it looked in — see step 1.

## 4. Run the front end

In a second terminal, from **`hw4/frontend/`**:

```bash
npm install
npm run dev
```

Then open **<http://localhost:5174>**.

Only the front end goes in a browser. Vite proxies `/api` to port 8000, so both halves
have to be running. The API is on 8000 because the assignment specifies it; the front end
is on 5174 because 5173 was taken on the development machine — change it in
[`frontend/vite.config.ts`](frontend/vite.config.ts). The proxy target can be overridden
with `CAMPUS_CUSTOMS_API`.

## Checking it without spending anything

Three offline suites. They use PydanticAI's `TestModel` in place of the real model, make
no network calls, and cost nothing:

```bash
.venv/bin/python tests/test_agent.py     # 83 checks — prompt, tools, output validation
.venv/bin/python tests/test_auth.py      # 19 checks — hashing, salts, signup/login parity
.venv/bin/python tests/test_audit.py     # 40 checks — append-only trail, redaction
```

Front-end type check and production build, from `frontend/`: `npm run build`.

## API

| Route | Returns |
|---|---|
| `GET /api/health` | Readiness, the product count, and the model in use |
| `GET /api/products` | Every product: id, name, type, description, colours, price, image URL, themes |
| `GET /api/products/{id}` | One product, plus search tags and stock for all six sizes |
| `GET /api/products/{id}/image` | The product photo as JPEG, normalised onto a white background |
| `GET /api/products/{id}/similar` | The "You might also like" row |
| `GET /api/stock` | Stock by size for every product, for the filter |
| `POST /api/auth/signup` | Create an account |
| `POST /api/auth/login` | Log in; sets an HttpOnly session cookie |
| `POST /api/auth/logout` | End the session |
| `GET /api/auth/me` | Who is signed in, or `null` |
| `POST /api/chat` | Ask the shop assistant. Returns the reply plus resolved product cards. |
| `GET`/`DELETE /api/chat/history` | Stored conversation for a signed-in shopper |
| `POST`/`GET`/`DELETE /api/recently-viewed` | Recently viewed products for a signed-in shopper |

## Passwords

Hashed with **PBKDF2-HMAC-SHA256, 120,000 iterations**, a unique random salt per password,
stored as `pbkdf2_sha256$salt$digest`. Signup and login share one module and one set of
constants ([`backend/auth.py`](backend/auth.py)), because settings that drift apart would
stop correct passwords from matching.

Login never reverses the stored value. It reads the salt out of the stored record,
re-hashes what was typed, and compares with `hmac.compare_digest` in constant time.

## The agent, in one paragraph

`gpt-5.6-luna` through Portkey, on the OpenAI Responses API. The system prompt is read
from [`backend/prompts/prompt.md`](backend/prompts/prompt.md) on every run, never inlined
in Python. Six read-only tools query the catalogue; the agent must call one for any price
or stock claim. Its reply is validated against a Pydantic schema, then against the
database — every product id must exist and every price must be real — and a failure sends
it back to the model to fix. Each turn is capped at 6 model calls, 10 lookups and 40,000
tokens, and every turn is recorded in
[`output/audit_trail.json`](output/audit_trail.json).

Full detail, including why each model field is shaped the way it is, is in
[`output/harness.md`](output/harness.md).
