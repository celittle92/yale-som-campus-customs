# HW4 project memory

Authoritative rules for this folder live in `.claude/rules/hw4-campus-customs.md`, one level
up in the private AI Foundations course workspace. Read that file, plus `AI_prompts.md` and
`output/harness.md`, before changing anything here. This folder is its own git repo, so the
import below resolves only inside that workspace, not in a standalone clone of this repo.

@../.claude/rules/hw4-campus-customs.md

## Local facts

- There is no written per-problem brief. Christine typed the scenario once (recorded in
  `AI_prompts.md`, Problem 1) and types each problem in her own words as the work goes.
  Each problem gets a section in `AI_prompts.md` and in `output/harness.md`.
- **The supplied data is already in the workspace**, at the root in a folder whose name
  contains a space: `data hw4/campus_customs.db` and `data hw4/products/` (102 JPEGs).
  Quote the path in shell commands. It sits outside `hw4/` so it cannot be committed by
  accident; the assignment forbids committing either one.
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
- `python` is not on PATH. Use `hw4/.venv/bin/python`. The venv exists (Python 3.14.7) with
  `requirements.txt` installed: fastapi 0.143, uvicorn 0.54, pydantic 2.14, pydantic-ai-slim
  2.55, openai 3.29, pwdlib 0.3.1 + argon2-cffi 25.1, python-dotenv. SQLite 3.50.4.
- Environment smoke check (free, no API calls), from `hw4/`:
  `.venv/bin/python -c "import fastapi, uvicorn, pydantic_ai, app_config; from pwdlib import PasswordHash"`
- `npm` and `npx` from nvm are blocked by the sandbox. Use the Node v24.20.0 copy in the
  course workspace one level up: `PATH="../.tools/node/bin:$PATH"
  npm_config_cache="../.tools/npm-cache" npm ...` (absolute paths if the shell is elsewhere).
- Christine's terminal usually sits at the workspace root, so give her commands with `hw4/`
  paths.
- `PORTKEY_API_KEY` comes from the shared workspace-root `.env` through `app_config.py`
  (the `Lecture 3 In Class/` pattern). No per-project `.env` is needed; `.env.example`
  lists the names. The sandbox cannot read `.env`, so live connection checks are Christine's
  to run.
- The course Portkey key hit its usage limit on 2026-10-04 (HTTP 412 on HW3). Confirm it was
  raised before planning any paid run.
- **This folder is its own git repo**, nested inside the private `ai-foundations` workspace
  and gitignored there (the `Lecture 4 In Class/yale_som_virtual/` pattern). Its remote is a
  **public** repo, because the assignment requires submitting a public repo URL. Nothing
  committed here is private: no keys, no database, no product images.
- Git writes and pushes fail in sandboxed Bash (`.git/config: Operation not permitted`) and
  the sandbox cannot read gh credentials. Run `git commit`, `git push`, and `gh` from the
  Terminal panel. `gh` lives at `../.tools/gh/bin/gh`. Read-only git (status, diff, log)
  works in Bash. Ask before every push.
- **There is no remote yet, by Christine's choice.** Local commits only until submission;
  the GitHub repo gets created at the end, as `celittle92/yale-som-campus-customs`. Before
  that first push: confirm with `git ls-files` that no key, database, or product image is
  tracked, then from the Terminal panel in `hw4/`:
  `../.tools/gh/bin/gh repo create yale-som-campus-customs --public --source=. --remote=origin --push`
  The submitted Canvas URL is that repo's URL.
- Run commands and smoke checks go here as each piece is built. Nothing in `hw4/` runs yet.
