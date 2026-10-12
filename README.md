# Campus Customs

A customer website for Campus Customs, a shop selling officially licensed Yale apparel in
New Haven. React + Vite + TypeScript front end, Python FastAPI backend, and a shopping
assistant built on PydanticAI.

Coursework for Yale SOM, AI Foundations, Homework 4.

## What is here

| Path | What it is |
|---|---|
| `backend/main.py` | FastAPI app: products, product detail, images, and the chat route |
| `backend/db.py` | Read-only access to the SQLite catalogue |
| `frontend/` | React + Vite + TypeScript storefront |
| `prompts/` | Runtime prompts, loaded by the backend and sent to the model |
| `AI_prompts.md` | The prompt log for the assignment, one section per problem |
| `output/harness.md` | The engineering record: data model, decisions, verification |

## The data is not in this repository

The assignment forbids committing the database and the product images, and this repo is
public, so neither is here. To run it you need `campus_customs.db` and the `products/`
folder of JPEGs.

Put them together in one folder:

```text
some-folder/
  campus_customs.db
  products/
    basic-hoodie-big-yale.jpg
    ...
```

The backend looks for `../data hw4/` next to this repository by default. To point it
somewhere else, set `CAMPUS_CUSTOMS_DATA` to that folder.

Nothing in this project writes to the supplied database. The connection is opened
read-only.

## Running it

Two servers. The front end proxies `/api` to the backend, so you only ever open the
front end in a browser.

**Backend**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cd backend
../.venv/bin/python -m uvicorn main:app --reload --port 8000
```

**Front end**, in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:5174.

The API runs on **8000**, as the assignment specifies. The front end uses 5174 because
5173 was taken on the development machine; change it in `frontend/vite.config.ts`. The
proxy target can be overridden with `CAMPUS_CUSTOMS_API`.

## API

| Route | Returns |
|---|---|
| `GET /api/health` | Readiness, plus the product count — proves the database is reachable |
| `GET /api/products` | Every product: id, name, type, description, colours, price, image URL |
| `GET /api/products/{id}` | One product, plus search tags and stock for all six sizes |
| `GET /api/products/{id}/image` | The product photo as JPEG |
| `POST /api/auth/signup` | Create an account |
| `POST /api/auth/login` | Log in; sets an HttpOnly session cookie |
| `POST /api/auth/logout` | End the session |
| `GET /api/auth/me` | Who is signed in, or `null` |
| `POST /api/chat` | The shop assistant. A stub until Problem 5. |

## Passwords

Hashed with **PBKDF2-HMAC-SHA256, 120,000 iterations**, a unique random salt per password,
stored as `pbkdf2_sha256$salt$digest`. Signup and login share one module and one set of
constants ([`backend/auth.py`](backend/auth.py)), because settings that drift apart would
stop correct passwords from matching.

Login never reverses the stored value. It reads the salt out of the stored record,
re-hashes what was typed, and compares with `hmac.compare_digest` in constant time.

Run the checks: `.venv/bin/python tests/test_auth.py`

## Configuration

Copy `.env.example` to `.env` and fill it in. `PORTKEY_API_KEY` is read server-side only
and never reaches the browser — the front end talks to this backend, and the backend talks
to Portkey.

Never put a key in a `VITE_`-prefixed variable. Vite compiles those into the browser
bundle, where anyone can read them.
