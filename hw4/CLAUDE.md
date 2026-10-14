# HW4 project memory

Authoritative rules for this folder live in `.claude/rules/hw4-campus-customs.md`, in the
private AI Foundations course workspace two levels up. Read that file, plus `AI_prompts.md`
and `output/harness.md`, before changing anything here. The import below resolves only
inside that workspace, not in a standalone clone of this repo.

@../../.claude/rules/hw4-campus-customs.md

## Local facts

- There is no written per-problem brief. Christine typed the scenario once (recorded in
  `AI_prompts.md`, Problem 1) and types each problem in her own words as the work goes.
  Each problem gets a section in `AI_prompts.md` and in `output/harness.md`.
- **Where this folder sits.** The public git repo is the parent, `yale-som-campus-customs/`,
  and it holds exactly one thing: this `hw4/`. That matches the file layout the assignment
  specifies (Problem 13). So the workspace root is **two** levels up, not one, and every
  command the user runs from the workspace root needs the
  `yale-som-campus-customs/hw4/...` prefix.
- **The supplied data is already in the workspace**, at its root in a folder whose name
  contains a space: `data hw4/campus_customs.db` and `data hw4/products/` (102 JPEGs).
  Quote the path in shell commands. It sits outside the repo so it cannot be committed by
  accident; the assignment forbids committing either one. `db.data_dir()` finds it by
  searching each ancestor of this folder rather than climbing a fixed number of levels —
  that assumption broke once already when the project moved deeper.
- Database shape (SQLite, 172 KB): `catalogue` (102 rows: `product_id` TEXT PK, `name`,
  `garment_type`, `description`, `colors`, `search_tags`, `image_file_path`, `price` REAL),
  `inventory` (612 rows: `product_id`, `size`, `quantity`, unique on the pair),
  `users` (3 rows: `name`, `email` unique, `password_hash`, `created_at`, `first_name`,
  `last_name`), `chat_messages` (22 rows: `user_id`, `role`, `content`, `products_json`,
  `created_at`). Sizes are XS, S, M, L, XL, XXL.
- `catalogue.image_file_path` is relative, e.g. `products/2025-yale-vs-harvard-t-shirt.jpg`,
  so it resolves against the `data hw4/` folder, not against `hw4/`.
- The three seeded users' passwords are hashed `pbkdf2_sha256$...` (Django's format).
  Existing logins must verify against that; `AGENT.MD` wants Argon2id for anything we hash.
  The plan to confirm with Christine before writing auth: verify old hashes with PBKDF2,
  hash new signups with Argon2id, and re-hash on successful login. Never print or return a
  hash while working on this.
- `python` is not on PATH, and the system `python3` is 3.9, too old for this code's type
  hints. Use this folder's `.venv/bin/python`. The venv exists (Python 3.14.7) with
  `requirements.txt` installed: fastapi 0.143, uvicorn 0.54, pydantic 2.14, pydantic-ai-slim
  2.55, openai 3.29, pwdlib 0.3.1 + argon2-cffi 25.1, python-dotenv. SQLite 3.50.4.
- Environment smoke check (free, no API calls), from this folder:
  `.venv/bin/python -c "import fastapi, uvicorn, pydantic_ai, app_config; from pwdlib import PasswordHash"`
- `npm` and `npx` from nvm are blocked by the sandbox. Use the Node v24.20.0 copy in the
  course workspace one level up: `PATH="../../../.tools/node/bin:$PATH"
  npm_config_cache="../../../.tools/npm-cache" npm ...` (absolute paths if the shell is elsewhere).
- Christine's terminal usually sits at the workspace root, so give her commands with
  `yale-som-campus-customs/hw4/` paths.
- `PORTKEY_API_KEY` comes from the shared workspace-root `.env` through `app_config.py`
  (the `Lecture 3 In Class/` pattern). No per-project `.env` is needed; `.env.example`
  lists the names. The sandbox cannot read `.env`, so live connection checks are Christine's
  to run.
- The course Portkey key hit its usage limit on 2026-10-04 (HTTP 412 on HW3). Confirm it was
  raised before planning any paid run.
- **The parent folder is its own git repo**, nested inside the private `ai-foundations`
  workspace and gitignored there (the `Lecture 4 In Class/yale_som_virtual/` pattern). Its
  remote is a **public** repo, because the assignment requires submitting a public repo
  URL. Nothing committed there is private: no keys, no database, no product images.
- Git writes and pushes fail in sandboxed Bash (`.git/config: Operation not permitted`) and
  the sandbox cannot read gh credentials. Run `git commit`, `git push`, and `gh` from the
  Terminal panel. `gh` lives at `../../.tools/gh/bin/gh`. Read-only git (status, diff, log)
  works in Bash. Ask before every push.
- **The remote is `celittle92/yale-som-campus-customs`, public**, created in Problem 13.
  Before any push, confirm with `git ls-files` that no key, database or product image is
  tracked. Push from the Terminal panel, from the repo root one level up. Ask first, every
  time.
- **The API runs on port 8000 from inside `backend/`**, because the assignment specifies
  `uvicorn main:app --reload --port 8000`. So `backend/` is **not** a package: modules
  import each other flatly (`from db import ...`), and `app_config.py` lives in `backend/`.
  Don't reintroduce `backend/__init__.py` or relative imports.
  Run it: `cd yale-som-campus-customs/hw4/backend && ../.venv/bin/python -m uvicorn main:app --reload --port 8000`.
- The site is on **5174**, not 5173, because another Vite app on this machine holds 5173.
  Run it from `yale-som-campus-customs/hw4/frontend/`: `npm run dev` (workspace Node, see above). Vite proxies
  `/api` to 8000, so only the site is opened in a browser.
- A long-running `Python` process on this machine has held port 8000 since before this
  project. It is not ours — ask before killing it:
  `lsof -nP -iTCP:8000 -sTCP:LISTEN` then `kill <pid>`.
- The agent is four files in `backend/`: `prompts/prompt.md` (system prompt, read at
  runtime), `agent.py` (wiring only), `tools.py` (six read-only catalogue tools),
  `models.py` (structured types). The agent returns product **ids**; `main.py` resolves
  them against the catalogue, so no price or image ever comes from the model.
- Offline agent tests use PydanticAI's `TestModel` and spend nothing:
  `.venv/bin/python tests/test_agent.py` (83 checks), `tests/test_auth.py` (19) and
  `tests/test_audit.py` (40).
  Use these instead of live calls to verify an edit.
- Front-end build and type check, from `frontend/`: `npm run build`.
- Sandboxed Bash cannot reach these local ports with `curl` (connection refused), and the
  preview tools can. Verify the API through the browser rather than the shell.
- `catalogue.image_file_path` is data, so images are served by product id and the resolved
  path is checked against the image folder. Keep it that way.
