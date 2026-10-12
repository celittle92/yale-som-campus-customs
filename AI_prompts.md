# AI Prompts — HW4

This file is the running record for Homework 4. It has one section per homework problem,
and each section includes:

- the problem number and title;
- at least one prompt Christine typed, in her own words, recorded verbatim; and
- if the first prompt was not enough, the follow-up prompts, each with a sentence on what
  was lacking after the previous one.

The running site, the database writes, and screenshots are the additional evidence that the
work was done. Per the professor, no extra proof essay is needed beyond these prompts, so
the notes under each prompt stay short and say only what was built.

The file is updated throughout the assignment. Prompts are recorded verbatim and are not
rewritten later to match the final code.

## Problem 1: Vibe Coder Prompts

### Prompt

> Ok, we need to set up a hw4 folder - make sure it's ready to go and uses all of our requirements for HWs

Ran the `/newhw` scaffolding skill. No HW4 assignment brief exists anywhere in the
workspace, so only the parts that are the same for every homework in this course were
created:

- [`app_config.py`](app_config.py) — the Portkey settings loader copied from
  `Lecture 3 In Class/`. It reads `PORTKEY_API_KEY` from a project `.env` if one exists and
  otherwise from the shared workspace-root `.env`, and keeps the model configurable through
  `OPENAI_MODEL` (default `gpt-5.6-luna`).
- [`requirements.txt`](requirements.txt) — `pydantic-ai-slim[openai]` and `python-dotenv`.
- [`.env.example`](.env.example) — variable names only, no values.
- [`prompts/`](prompts/) — empty; each AI step's runtime prompt goes here and is loaded by
  its script at runtime.
- [`output/harness.md`](output/harness.md) — the engineering record, one section per problem.
- this file.

Still waiting on the assignment: `submission_spec.json` (the required scripts, the prompt
each one loads, and the exact output filenames), `hw4/CLAUDE.md`, and a
`.claude/rules/hw4-*.md` rule file.

### Follow-up prompts

1. **What needed resolution:** setup was blocked on two things the scaffold could not
   guess — whether an assignment brief existed, and what shape HW4 takes.

   > I will share the brief of the overall problem, but then will type each problem in my own words

   > We will need to call portkey scripts but I'll need to build a site to be uploaded to a public GitHub repo

   Added `hw4/` to the workspace project map in [`../CLAUDE.md`](../CLAUDE.md). `hw4/CLAUDE.md`,
   the `.claude/rules/hw4-*.md` rule file, and `submission_spec.json` wait for the brief,
   which names the scripts, the prompt each one loads, and the exact output filenames.

   Two consequences of the site being public that the rule file will carry: nothing in the
   published site or repo may contain `PORTKEY_API_KEY` or any other secret, and the site
   must be generated from files kept in this workspace rather than edited in place on the
   public repo.

2. **What needed resolution:** the rule file, `hw4/CLAUDE.md`, and `submission_spec.json`
   all needed the assignment's actual requirements.

   > here's the general brief:

   Christine shared the scenario as a screenshot. Its requirements, as given:

   - Campus Customs needs a real customer website with a helpful chatbot: a **React + Vite
     TypeScript** front end and a **Python FastAPI** backend whose brain is a **PydanticAI**
     agent.
   - Shoppers browse products, create an account, chat about merch, see matching items
     appear on the page, and get honest price and stock answers from a local database.
   - `campus_customs.db` is supplied, with tables for the product catalogue, inventory by
     size, and users with hashed passwords. Product image file paths are in the catalogue
     table.
   - Research yalebulldogblue.com for the style of the Campus Customs page and for
     information to use in the agent prompt.
   - Use `PORTKEY_API_KEY` for the agent's AI calls; with OpenAI through Portkey, any model
     in the 5.6 or 6 series. A smarter model may suit harder agent steps.
   - Work one problem at a time, each typed in her own words.
   - At the end, push to a **public** GitHub repo and submit the repo URL on Canvas; the
     last problem shows the file tree. **Do not commit the database or the product images.**

   Created from this: [`../.claude/rules/hw4-campus-customs.md`](../.claude/rules/hw4-campus-customs.md),
   [`CLAUDE.md`](CLAUDE.md), [`submission_spec.json`](submission_spec.json), and
   [`.gitignore`](.gitignore). Updated the workspace project map and verification commands
   in [`../CLAUDE.md`](../CLAUDE.md) and the shared-setup table in
   [`output/harness.md`](output/harness.md).

   Found the supplied data already in the workspace at `data hw4/` (database plus 102
   product JPEGs), outside `hw4/` so it cannot be committed by accident. Inspected the
   schema; recorded it in [`CLAUDE.md`](CLAUDE.md). The three seeded users' passwords are
   `pbkdf2_sha256` hashes, which the auth work will have to verify against.

3. **What needed resolution:** the project had no environment, so nothing could be run.

   Christine ran the setup command herself in her terminal:

   > cd "/Users/christinelittle/Yale SOM_Old/AI Foundations/hw4" && python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt

   Created `hw4/.venv` on Python 3.14.7 and installed
   [`requirements.txt`](requirements.txt). Verified offline that fastapi 0.143, uvicorn
   0.54, pydantic 2.14, pydantic-ai-slim 2.55, openai 3.29 and
   [`app_config.py`](app_config.py) all import, and that a `pwdlib` Argon2id hash verifies
   round-trip. No API calls, so no Portkey credits spent. Versions recorded in
   [`CLAUDE.md`](CLAUDE.md).

4. **What needed resolution:** the assignment requires submitting a **public** repo URL, but
   the surrounding AI Foundations workspace is a private repo. The project needed its own
   repo, and a decision about when it becomes public.

   > let's do the nested clone for the public repo

   Christine chose the name `yale-som-campus-customs` (matching the existing
   `yale-som-evans-hall`) and chose to keep the repo local for now, creating it on GitHub at
   submission time rather than working in public.

   Made `hw4/` its own git repo on branch `main` and gitignored `hw4/` and `data hw4/` in the
   workspace repo, following the `Lecture 4 In Class/yale_som_virtual/` pattern. First commit
   `e253e7a` holds 9 files; `.venv`, `.env`, the database, and the product images are all
   excluded. Removed the absolute home paths from [`CLAUDE.md`](CLAUDE.md) so nothing in the
   eventual public repo carries them, and recorded there the exact `gh repo create` command
   for submission day.

5. **What was lacking:** this log existed but had been built from the house convention
   rather than from Problem 1's stated requirements.

   > Problem 1: Vibe Coder Prompts
   >
   > If we have not already, create AI_Prompts.md to keep it updated as we work together. This will keep a log of what I typed to you as we work.
   >
   > Keep one section for each problem. The sections must include:
   > -problem number and title
   > -at least one prompt typed, (use my words here)
   > -IF needed - follow up prompt(s) and a sentence on what was lacking after the initial prompt
   >
   > The running site, database writes, and screenshots are additional evidence - prof says I "do not need an extra proof essay beyond these prompts"

   Retitled this section to "Vibe Coder Prompts" and restated the required section format
   above in the words of the assignment: problem number and title, at least one prompt in
   Christine's own words, and follow-ups only where the first prompt left something lacking.
   Recorded that the running site, database writes, and screenshots are the evidence, so
   these notes stay short rather than becoming a proof essay.

   This file already existed, created during setup (Problem 1's first prompt, above), so
   Problem 1 was a matter of bringing it in line with the stated format rather than starting
   it.

6. **What was lacking:** the prompt above wrote the filename as `AI_Prompts.md`, so it was
   renamed to match. That spelling was a typo rather than the assignment's.

   > wait - the assignment has AI_prompts.md
   >
   > I just uppercased it by reflex. Keep the lowercase. but do the rest.

   Renamed the file back to `AI_prompts.md`. Both renames went through `git mv` in two
   steps, because macOS is case-insensitive and a direct rename silently does nothing. The
   tracked filename is unchanged from the first commit, and every reference to it elsewhere
   still resolves. The prompt in follow-up 5 is left exactly as typed, per the rule that
   prompts are never rewritten to match later decisions.

---

<!--
Template for the next problem. Copy below this line and replace N and the bracketed text.

## Problem N: [Title]

### Prompt

> [verbatim]

[What was built, with links to the code and JSON outputs that are the evidence.]

### Follow-up prompts

1. **What was lacking:** [what the initial prompt did not settle].

   > [verbatim]

   [What was done.]
-->
