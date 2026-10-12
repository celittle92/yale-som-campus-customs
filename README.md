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
.venv/bin/python -m uvicorn backend.main:app --reload --port 8010
```

**Front end**, in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:5174.

Ports 8010 and 5174 are used because 8000 and 5173 were already taken on the development
machine. Change them in `frontend/vite.config.ts` and the `uvicorn` command if you like;
the front end reads `CAMPUS_CUSTOMS_API` to override the proxy target.

## API

| Route | Returns |
|---|---|
| `GET /api/health` | Readiness, plus the product count — proves the database is reachable |
| `GET /api/products` | Every product: id, name, type, description, colours, price, image URL |
| `GET /api/products/{id}` | One product, plus search tags and stock for all six sizes |
| `GET /api/products/{id}/image` | The product photo as JPEG |
| `POST /api/chat` | The shop assistant. A stub until Problem 5. |

## Configuration

Copy `.env.example` to `.env` and fill it in. `PORTKEY_API_KEY` is read server-side only
and never reaches the browser — the front end talks to this backend, and the backend talks
to Portkey.

Never put a key in a `VITE_`-prefixed variable. Vite compiles those into the browser
bundle, where anyone can read them.
