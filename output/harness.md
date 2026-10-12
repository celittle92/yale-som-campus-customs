# HW4 Harness

This file is our own engineering record: the design decisions behind each problem and the
checks that show the result is trustworthy. It is **not** a required deliverable — the
assignment's evidence is the prompt log, the running site, the database writes, and
screenshots, and the professor said no extra proof essay is needed beyond the prompts. Keep
this file short and useful; the verbatim prompt history lives in
[`../AI_prompts.md`](../AI_prompts.md).

**Project:** a Campus Customs customer website with a helpful chatbot. Shoppers browse
products, create an account, chat about merch, see matching items appear on the page, and
get price and stock answers that come from the supplied database rather than from the model.

**Shared setup (all problems)**

| Item | Value |
|---|---|
| Front end | React + Vite, TypeScript |
| Backend | Python FastAPI; the agent is PydanticAI |
| Data | `campus_customs.db` (SQLite): `catalogue` 102 rows, `inventory` 612 rows by size, `users`, `chat_messages`. Never committed. |
| Product images | `products/` beside the database, paths held in `catalogue.image_file_path`. Never committed. |
| Model access | Portkey, through [`../app_config.py`](../app_config.py); key read from the workspace-root `.env`, server-side only |
| Main model | `gpt-5.6-luna` (`OPENAI_MODEL`); 5.6 or 6 series per the assignment, with a stronger model available for harder agent steps |
| Runtime prompts | `../prompts/<name>.md`, loaded at runtime; never inlined in Python |
| Submission | pushed to a public GitHub repo; the repo URL goes on Canvas |
| Pre-submission check | `python3 check_submission.py hw4` (offline, no API calls) |

## System overview

*For a reader who wants the whole system in one place. The problem sections that follow
keep the detailed history of how each part was built and tested.*

*(Fill in once the first problem is built.)*

---

<!--
Template for the next problem. Copy below this line, replace N and the bracketed text,
and add a line for it under Contents.

## Problem N: [Title]

**Script:** [`../script.py`](../script.py) ·
**Prompt:** [`../prompts/script.md`](../prompts/script.md) ·
**Model:** `[ModelName]` in [`../models.py`](../models.py) ·
**Output:** [`output_file`](output_file)

### N.1 [Main design decision]

#### Christine's prompt

> [verbatim]

#### What we did, step by step

1. ...

#### Result

### N.2 [Model fields or other decisions]

### N.3 Verification
-->
