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

## Problem 2: Analyze the database

### Prompt

> Problem 2: Analyze the database
>
> Look at the database in data hw4 -- campus_customs.db -- understand the fields of each table. But ABSOLUTELY ensure you understand catalogue, inventory, and users.
>
> Once that is complete, start the file output/harness.md -- each table and its fields should be recorded, as well as a short line on why each field matters for the shop and/or chatbot.  Send me what you come up with and I'll review and either approve or revise.
>
> Note this harness file will need to continue to grow in later HW problems (models, tools, safety, and specs).

Inspected all five tables read-only with Python's `sqlite3` — schema, types, nullability,
indexes, foreign keys, value ranges, and distinct values. No model calls, so no Portkey
credits, and nothing was written to the database. Wrote
[`output/harness.md`](output/harness.md): a field-by-field table for `catalogue`,
`inventory`, `users`, and `chat_messages` with a line on why each field matters, how the
tables join, eight findings that change the design, and three open questions.

### Follow-up prompts

1. **What was lacking:** the harness reported that `garment_type` was too messy to filter on
   and that prices were whole dollars, but neither finding said what to do about it.

   > Hm, for garment_type would there be a way for us to standardize them? maybe not now but down the line? because a website like that would drive me nuts.
   >
   > For the price is it because the database has no cents included? Because if cents ARE included the future website and chatbot should absolutely include the full price.

   Both answered in [`output/harness.md`](output/harness.md). Built and verified a keyword
   rule that collapses the 22 `garment_type` spellings into seven canonical categories with
   102 of 102 products mapped and nothing left over; recorded the mapping table and the
   decision to apply it as a read-time lookup, leaving the database untouched, when a
   problem first needs category filtering. Confirmed against the data that 0 of 102 products
   have non-zero cents, so the whole-dollar prices reflect the data and not a display
   choice; recorded the decision to read `price` as stored and format it with two decimals
   at the display boundary, so full prices appear automatically if cents ever arrive. Also
   corrected a loose claim in the first draft: price does not follow from category — hoodies
   run $45–$88 — so a price must always be read per product.

2. **What was lacking:** the harness ended with two open questions — what to do about the
   unusable seeded logins, and whether chat history should persist — and neither could be
   decided without Christine.

   > Let's handle these open questions for me first:
   >
   > * The seeded logins are unusable (finding 5). [...] My recommendation is the first — it needs no guessing, and new accounts get the stronger algorithm your semester rules call for.
   >
   > Do the thing you recommend.
   >
   > * Chat memory. `chat_messages` already stores history per user. Reuse it as the agent's memory, or keep memory in-process for the session only?
   >
   > If the user is logged in lets keep the chat memory. That could make life easier for users. Do not do it by cookies or IP tho if the user is not logged in, bc that could be sus and users don't like that.

   Recorded both as decisions D1 and D2 in [`output/harness.md`](output/harness.md), and
   carried the parts that must hold across sessions into
   `.claude/rules/hw4-campus-customs.md`. D1: seeded accounts stay untouched as historical
   data, new signups use Argon2id, and a legacy hash must fail as a generic "invalid email
   or password" rather than a 500 or an enumeration hint. D2: history persists for signed-in
   users and is never written for signed-out ones — no cookie, no IP, no fingerprint — with
   the bound on replayed history noted as a recurring token cost. Found while writing it up
   that `chat_messages.user_id` is NOT NULL with a foreign key to `users`, so the supplied
   schema already makes anonymous persistence impossible; no extra guard is needed.

Awaiting Christine's review of the rest of the harness.

---

## Problem 3: Build the Campus Customs website

### Prompt

> Problem 3: Build the Campus Customs website
>
> Time to scaffold a react + vite + TypeScript front end for Campus Customs. There should be a nav bar at the top of the site that links to the main pages we'll have:
> -home
> -products
> -about us
> -log in
> -create account
>
> The Campus Customs-style wording can be pulled from yalebulldogblue.com for the Home page and About Us page. HOWEVER, write these pages in a voice more like mine - direct, informational, yet conversational and with a user-focused lens. We should NOT copy the original site text.
>
> On the products page, we should create a product card including images from the catalogue -- use the image paths that were included in the database, along with the basic product information including name, price, and a short description.
>
> Each product should open a single-item page with a large image on the side (left side), the full product text on the other including description, price, sizes/stock whenever available. Clicking on the product card on the Products page should take the shopper to the primary single-item page for the product.
>
> There should be a chat interface on the bottom right of the website -- a floating chat panel is OK. We do NOT YET need to code it to talk to an agent, but a stub that calls the backend later is enough for right now.
>
> However, we will need to include an API to read the database. Start a simple FastAPI app in backend/main.py to serve products and images. We will grow it into the agent backend once we get to problem 5.

Built the backend ([`backend/main.py`](backend/main.py), [`backend/db.py`](backend/db.py))
and the storefront ([`frontend/`](frontend/)), plus [`README.md`](README.md). Full
engineering detail and the verification table are in
[`output/harness.md`](output/harness.md#problem-3-the-website).

Evidence: 102 product cards render with 102 images and none broken; a product detail page
shows a two-decimal price, colours, and per-size stock with out-of-stock sizes struck
through; the floating chat panel sends a message and renders the stub reply. The front end
type-checks and builds clean, and there is no horizontal overflow at 375px. No model calls
anywhere in this problem, so no Portkey credits were spent.

`yalebulldogblue.com` was read once for what the business is and how it is organised. No
sentence or asset was copied; the page copy is written fresh and grounded in our own
catalogue counts and tags. The store address is the only fact taken from the research.

### Follow-up prompts

1. **What was lacking:** the product page displayed colours and sizes but let you do
   nothing with either, and it gave no hint which of the two was even selectable.

   > Great - use Navy cause it should look like Yale for sure. QQ - why on product pages can't I select the color and/or size if it is in stock?

   Checked the data before answering. Colours turned out **not** to be orderable options:
   the array lists colours present in the garment's design, so the Boola Boola tee is navy
   with white-and-gray lettering, and `inventory` has no colour column. Offering a colour
   picker would have implied the Branford quarter-zip comes in green. The real fault was
   that colours were rendered as pill badges that looked selectable; they now read as a
   sentence under "Colours in this design".

   Sizes are a genuine variant, so Christine chose to make them selectable and hand the
   selection to the chat assistant rather than build a cart. Full detail in
   [`output/harness.md`](output/harness.md#31-selecting-colours-and-sizes).

2. **What was lacking:** the size controls behaved like text, not like controls.

   > yeah my cursor goes to a text highlight when I hover over a size:

   (Sent with a screenshot showing the text cursor and a native tooltip over size XXL.)
   The sizes had been `<li>` elements with a `title` attribute. They are now real
   `<button>` elements: pointer cursor and hover state when in stock, disabled and
   not-allowed when out, `aria-pressed` for the selected one, and the native tooltip
   replaced by an `aria-label` carrying the stock count.

3. **What was lacking:** the work was done but nobody had checked it line by line against
   what Problem 3 actually asked for.

   > Cool. It looks good. Are all the specs of Problem 3 covered now?

   Audited every clause of the prompt against the running site, driving the real pages
   rather than re-reading the source. All nine covered; the table is in
   [`output/harness.md`](output/harness.md#32-spec-coverage-audit). The image-on-left
   assertion failed on first measurement because the preview pane sits below the `lg`
   breakpoint where the layout intentionally stacks; re-measured at 1280×900 it passes.

4. **What was lacking:** the audit found no code to change, so it was not yet recorded
   anywhere.

   > commit this. i'm good with the responsive design, that's great.

   The working tree was already clean — the audit only read the running site. Recorded the
   coverage table and the breakpoint finding in the harness and committed that, and noted
   Christine's approval of the stacking behaviour, so the `lg` breakpoint stays.

---

## Problem 4: Create an account and login

### Prompt

> Problem 4: Create an account and login
>
> Build a normal create-account/login flow.
>
> Create account should include first name, last name, email, password, and confirm password fields
> Log in should have email and password.
>
> I know the pages more or less have these, but let's also make sure they are built out properly. New accounts should go to the 'users' table. Make sure to store the passwords securely (as we discussed doing in either @[Lecture 4] or @[jsnode installation and usability] i forget which one) to ensure hackers, either human or AI bots, cannot access them.
>
> The seed database should already have a test user you can use while building it out.
>
> Email: test@campuscustoms.yale.edu
> password: password
> see the screenshot I sent for the Hash function lol i'm not typing that out
>
> The login should check a password by:
> -never un-hashing the stored value. re-hash what the user typed and compare
> -read the salt out of the stored string (middle piece) - do not make a new one at login
> -hash the typed password with that same salt, and compare it to the stored hash. use a constant-time compare.
> -signup and login must use the SAME hash settings (function, salt handling, and iteration count) -- if they differ then the right PW will not match -- do NOT mess this up
>
> I will need to ensure that I can log in as the test user and will need to create an account on the website so make sure it works.
>
> update output/harness.md with how the auth works, what is stored for a user, and how we protect passwords

(Sent with a screenshot giving the hash parameters: PBKDF2-HMAC-SHA256, 120,000
iterations, stored as `pbkdf2_sha256$salt$hash`.)

**This corrected an earlier conclusion.** Problem 2 had found that the seeded accounts
could not be logged into, because the iteration count is absent from the stored string.
The count is not missing — it is specified by the assignment rather than stored. Verified
against the seeded row before writing any code: 120,000 iterations matches; 100,000,
260,000 and 600,000 do not. Decision D1 is superseded; there is no Argon2id path.

Built [`backend/auth.py`](backend/auth.py) (one module, one set of constants, used by both
signup and login), [`backend/sessions.py`](backend/sessions.py) (HttpOnly cookie over a
server-side store), the auth routes in [`backend/main.py`](backend/main.py), user writes in
[`backend/db.py`](backend/db.py), and the real forms with
[`frontend/src/AuthContext.tsx`](frontend/src/AuthContext.tsx).

Evidence: 19 unit checks pass in [`tests/test_auth.py`](tests/test_auth.py), including an
independent re-derivation proving signup and login agree. End to end in the browser,
logging in as the test user works through the form, creating an account works through the
form, and signup → log out → log in again succeeds. The stored row for a new account is
`pbkdf2_sha256` with a 32-character random salt that re-derives at 120,000 iterations and
contains no plaintext. The session cookie is not readable by JavaScript, and neither auth
response contains a hash. Full write-up in
[`output/harness.md`](output/harness.md#problem-4-accounts-and-login). No model calls, so
no Portkey credits.

### Follow-up prompts

1. **What was lacking:** the harness recorded the automated checks but not Christine's own
   confirmation that both flows work for a real person using the site.

   > To wrap up problem 4, I need to add to the harness too the following:
   > I can confirm I can log in as the test user that was created, it says 'hi test' and I was able to easily log out using the logout button crated. Yay.
   >
   > I also was able to successfully create a new account - I used my real name but a fake email and an easily guessed password - but it worked!

   Added her confirmation verbatim to
   [`output/harness.md`](output/harness.md#confirmed-by-christine-2026-10-11), with the
   database-side evidence beside it: `users` now holds six rows, the three created through
   the site all have a 32-character random salt and a 64-character digest, all six salts
   are distinct, and no row stores anything resembling a plaintext password. Her account is
   id 6.

   Noted two things rather than leaving them implied. Her real name is only in the local
   database, which is gitignored and outside the repository, so nothing personal reaches
   the public repo. And the hashing protects a stolen table, not a guessable password at
   the login form — that would need rate limiting, which is now listed as a known gap.

---

## Problem 5: PydanticAI agent backend

### Prompt

> Problem 5: PydanticAI agent backend
>
> Now we need to build the agent for the shop chatbot as a PydanticAI agent behind the FastAP that is plugged into the front-end chat widget. The API app should be put in backend/main.py which is the file to be ran with Uvicorn.
>
> Keep the agent as these four files next to it (same idea as what we did for @[HW3] ) :
> backend/prompts/prompt.md - the system prompt (grow this file later)
> backend/agent.py - agent entry/wiring
> backend/tools.py - tools the agent can call
> backend/models.py - Pydantic/PydanticAI structured types
>
> in main.py expose a chat route so a message from the created website returns a reply from the agent (and whatever else needed for products/auth) -- the AI model API Key is needed for this agent!!
>
> Put the Campus Customs voice we created and safety basics (industry standard on top of any standard we've established) into prompts/prompt.md -- we will actually expand tools and safety later but let's just add what we have for now bc we are here.
>
> Start or update the types in models.py for chat replies/product cards if needed.
>
> In output/harness.md, note how the front end talks to FastAPI and how the agent is loaded (including prompt file and model).
>
> Make sure that the backend runs from the backend/ folder like this:
> uvicorn main:app --reload --port 8000
>
> ^^^ knowing we had to use a somewhat different port than 8000, let's move everything to port 8000 so its consistent with what the professor/TA/AI grader whoever is looking for.

Built the four agent files — [`backend/prompts/prompt.md`](backend/prompts/prompt.md),
[`backend/agent.py`](backend/agent.py), [`backend/tools.py`](backend/tools.py),
[`backend/models.py`](backend/models.py) — and wired the chat route in
[`backend/main.py`](backend/main.py). Moved everything to port 8000, which meant making
`backend/` a plain folder rather than a package (flat imports, `app_config.py` moved into
it) so `uvicorn main:app` works from inside `backend/`.

The agent returns product **ids**, never product data; `main.py` resolves them against the
catalogue, so every price and image on the page comes from the database and an invented id
is dropped and logged. Decision D3 landed here, since `browse_category` needed it:
asking for hoodies now returns all 27 rather than the 5 that raw `garment_type` gives.
Decision D2 is implemented too — history is loaded and saved for signed-in shoppers only,
bounded to 10 messages because replayed turns are re-paid every time.

Evidence: 33 offline checks pass in [`tests/test_agent.py`](tests/test_agent.py) using
PydanticAI's `TestModel`, which drives the real prompt, tools and output validation with a
stub in place of the LLM — **no credits spent**. `python3 check_submission.py hw4` reports
0 fail, 0 warn, 36 ok, confirming `agent.py` both calls a model and loads its prompt file.
How the front end talks to FastAPI and how the agent is loaded are written up in
[`output/harness.md`](output/harness.md#problem-5-the-pydanticai-agent).

Not yet done: a live model call. That is the first paid step in HW4 and is waiting on
Christine's go-ahead.

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
