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

### Follow-up prompts

1. **What was lacking:** everything was verified with a stub model, so the agent had never
   actually reached Portkey. Port 8000 was also still held by another process.

   > kill 60887

   Identified the process first: it was the Evans Hall backend from Lecture 4, left
   running in `Lecture 4 In Class/yale_som_virtual/backend`. Christine killed it, and the
   API now runs on 8000 with `uvicorn main:app` from inside `backend/`, as the assignment
   requires.

   She then chose a three-question live test. All three results are written up in
   [`output/harness.md`](output/harness.md#the-live-run--first-paid-calls-in-hw4). The
   browse and stock questions worked, including conversational memory — "that crew one"
   resolved to the hoodie from the previous turn, and the stock answer matched `inventory`
   exactly.

   The safety probe failed usefully: Azure's content filter rejected the jailbreak-shaped
   message at the provider with HTTP 400, before the model saw it, and our route turned
   that into a generic 503 that made the site look broken. Fixed so a content-filter
   rejection is answered as a refusal in the assistant's voice. A filtered message is
   deliberately not persisted, because saved turns are replayed as context and storing one
   would re-trigger the filter on every later message. Re-tested: both the original probe
   and a milder one are now refused cleanly, with no leak of the model, the tools, the
   instructions, or another customer. Also fixed a display bug where reply line breaks
   collapsed into one run-on line.

   Cost: four billed exchanges of 2–3 model calls each. The two content-filtered attempts
   cost nothing.

2. **What was lacking:** the previous turn noted that the agent narrated the product cards
   in prose as well as returning them, and left it for Problem 6.

   > on list questions it repeats product names in prose and returns cards — redundant now that cards render.
   >
   > Fix it now

   Fixed in the instructions rather than in code: bulleted and numbered product lists are
   now forbidden outright, and the "Returning products" section explains that the website
   renders each id as a card under the reply, so the agent should use its words for what a
   card cannot say. Verified live with the same question in a fresh session — zero of the
   six card names now appear in the reply, no bullets, 226 characters against roughly 370,
   and the same six cards still returned. Detail in
   [`output/harness.md`](output/harness.md#51-stopping-the-agent-from-narrating-the-cards).
   Cost: one more billed exchange.

---

## Problem 6: Tools: Product info and stock

### Prompt

> Problem 6: Tools: Product info and stock
>
> Give the agent tools that look up real info from campus_customs.db:
> product description
> price
> how many are in stock (by size when customer asks)
>
> I like how we have the agent built rn though that links to product being asked about so don't remove that.
>
> The agent MUST use the database, and it should not invent prices or QTY. If a size is out of stock, the agent should say so clearly. No ghost info.
>
> Expand prompts/prompt.md so agent knows to call these tools for the price and stock questions. Add or update return types in models.py
>
> in output/harness.md, list each tool that was built, and explain which model fields that were chosen for lookup results and why (note that we combined certain fields and we should be clear about that too)

Converted every tool return from a loose dictionary to a typed model in
[`backend/models.py`](backend/models.py), added a sixth tool
(`find_products_by_price`) so price comparisons happen in Python rather than in the model,
and rewrote the tool-selection section of
[`backend/prompts/prompt.md`](backend/prompts/prompt.md) with a question-to-tool table and
the rule that price and stock questions always require a tool call. The product-card
linking from Problem 5 is untouched.

The full tool list, the field choices, the fields combined from `catalogue` and
`inventory`, and the fields derived in Python rather than left to the model are written up
in [`output/harness.md`](output/harness.md#problem-6-tools-for-product-info-and-stock).

Evidence: 43 offline checks pass, including a direct cross-check that every quantity the
tools report matches `inventory` exactly across three products and all six sizes. Live,
the agent quoted the Crew Left Chest Hoodie at $68.00, described it correctly, and said
"Medium is sold out; it's available in XS, S, L, XL, and XXL" — which matches the database
row for row. Asked what is under $40 it answered "25 items", which is exactly the count in
the catalogue. Cost: two billed exchanges.

### Follow-up prompts

1. **What was lacking:** nothing recorded what the live runs actually cost, so spend was
   guesswork.

   > do you have an idea how much $$ my apikey has spent

   Could not be answered in dollars from here — the Portkey dashboard holds the real
   figure, and inventing one without a per-token rate would have been a fabrication. What
   was measurable was volume: the instructions are ~2,000 tokens re-sent on every model
   call, a product lookup adds ~180 and a category listing ~580, and a typical question is
   two calls, so roughly 6–8k input tokens per exchange and 50–70k across HW4.

   Added real usage logging to the chat route so this stops being an estimate.

2. **What was lacking:** the model choice was a default rather than a recorded decision,
   and the assignment invites escalating to a stronger model.

   > allegedly i've only used $.008 today....let's make sure we keep using the luna model to keep the costs low whenever possible.

   Already on `gpt-5.6-luna` with no fallback and no escalation path, so this was about
   locking it in: recorded in [`backend/agent.py`](backend/agent.py), in
   `.claude/rules/hw4-campus-customs.md`, and in the harness. If answer quality needs work
   the first moves are better instructions and better tools, which cost nothing at runtime;
   switching models is Christine's call. Also fixed a drift risk where `model_name()` read
   `OPENAI_MODEL` from the environment directly and could report a different model than the
   agent actually used.

---

## Problem 7: Chat search that updates the page

### Prompt

> Problem 7: Chat search that updates the page
>
> We need to add a feature to the site. When a customer asks about a type of item, such as 'what hoodies' do you have?' - the agent should search the catalogue and the website should dynamically show those matching items as product cards including image, name, price, and short info. I feel like our chat bot already does this but lets see if we can get the website to as well.
>
> The is an API contract - the agent returns structured product matches and then the frontend renders them on the site. It should be cool!
>
> After the dynamic product cards re loaded by this feature, make sure the SINGLE ITEM PAGE BEHAVIOR FROM PROBLEM 3 STILL WORKS. Each product card - including the ones chat put on the page - should still open that large detail view including the image, and full information when clicked.
>
> once this is done, update prompts/prompt.md and output/harness.md so it is clear how the search results reach the page

Right that the chat panel already did this; the work was getting the matches onto the shop
itself. Added `match_label` to the `ChatReply` contract so the page has a real heading,
gave [`frontend/src/ChatContext.tsx`](frontend/src/ChatContext.tsx) a shared results store,
and had the Products page render a results section above the full grid. The shopper is
taken there automatically when the agent returns more than one product, but not for a
single one — that usually means a follow-up about something they are already reading.

The single-item page still works because the results section renders the **same**
`ProductCard` component as the main grid, so there is no second implementation to drift.
Verified by clicking a chat-placed card: it opened the full Problem 3 detail view with the
685×685 image on the left, `$98.00`, colours, and six size buttons.

Found and fixed a real bug on the way: `ChatReply` was defined twice, in both `models.py`
and `main.py`, and `models.py` defined `SizeStock` twice with the second silently shadowing
the first. All seventeen types now live in `models.py` and `main.py` defines none.

Also worth recording a mistake of mine: the first live test looked like a failure because I
waited a fixed 12 seconds and nothing had navigated. The first request after a backend
restart is slower, since the agent is built on demand. Re-run with polling, it navigated in
5 seconds. Full write-up in
[`output/harness.md`](output/harness.md#problem-7-chat-search-that-updates-the-page).
Cost: two billed exchanges.

---

## Problem 8: Customer memory

### Prompt

> Lets move to Problem 8: Customer memory.
> I think we did this already 😎 at least part of it!
>
> When a shopper is logged in, save their chat history in the database in an appropriate table and reload it when they return. The agent should know WHO is chatting - including the name and email. Put that in agent deps (or an equivalent clear pattern) and/or tools the agent can call.
>
> Also pass enough PAGE CONTEXT so if someone is on a product page and asks 'do you have this in pink?' the agent knows which item they mean. You can put code into the agent context.
>
> Guests can and should be able to still chat but the history only needs to persist for logged-in users (we did this part. woot. but double check everything so it's right and to the specs above).
>
> Document this in output/harness.md -- how the user chat history is stored, what customer fields the agent sees, and how the page context is passed.

Right that persistence was done. The audit found three real gaps. The history was replayed
to the *model* but the panel always opened empty, so a returning shopper never saw it;
`clear_messages()` existed but no endpoint ever called it, making it dead code; and the
agent had no idea who it was talking to or what page they were on.

Added `ShopperContext` as PydanticAI run dependencies — signed-in state, first name, full
name, email, page path, and the product being viewed — rendered into the instructions by
an `@agent.instructions` function. Deps rather than appending to the message, so the
context never enters `chat_messages`, is never replayed as something the shopper said, and
cannot be overwritten by typing. Added `GET` and `DELETE /api/chat/history`, and the panel
now restores the conversation on sign-in with a "Clear it" control.

Page context is a path only: the browser sends `location.pathname`, and the backend
resolves what it means against the catalogue. Identity comes from the session cookie, so
neither can be forged in the request body.

Evidence: 65 offline checks pass, including one that caught a run with no deps crashing
rather than falling back to guest. Live, on the Boola Boola product page, "do you have
this in pink?" resolved to that product with no clarifying question and answered honestly.
Signed in, the agent greeted by name without reciting the email; signed out it said it did
not know, and the history endpoint returned empty. A full reload as a returning shopper
restored 19 messages and 23 cards. Full detail in
[`output/harness.md`](output/harness.md#problem-8-customer-memory). Cost: three billed
exchanges.

---

## Problem 9: Usability improvements

### Prompt

> Problem 9: Usability improvements
>
> Now that our shop is working well, we need to improve it.
>
> We will implement 2 frontend usability improvements:
>
> * I want a product filter that filters items by type, color, and size. Include an 'exclude out of stock' button that will exclude items that are in scope of the filter but out of stock.
> * Add a 'You might also like' carousel to the bottom of individual product pages. Have the recommendations be items that are similar in type/color
>
> We will also implement 2 backend/agent usability improvements:
>
> * I want to have a backend logic that has a personalized 'recently viewed' service. This can use cookies/data from unlogged in users but it absolutely must work for logged in users
> * I want to make it so the agent works faster to turn up results. Right now I think when a chat is sent it takes too long in the 'thinking' phase
>
> Front end improvements are things that make the site look better and make it easier to use. The agent/backend improvements should make the agent output better/more accurate/safer. Make sure my choices do that.
>
> Write output/usability.md BEFORE or AS we build this out. For each improvement write:
> * What I added
> * Why it helps a shopper or the business
>
> Then make sure that the improvements show up in the running app. Graders are going to read the writeup and look for the features so pls make sure they are there on the site!!!

Wrote [`output/usability.md`](output/usability.md) first, then built all four and
verified each in the running app.

Measured results: the filter narrows 102 → 29 crewnecks → 17 navy blue → 12 in stock in
L, matching the database exactly — the brief's own example. The carousel returns 8 similar
items, all navy hoodies at $68.00. Recently viewed records newest-first for signed-in
shoppers and works for guests from `localStorage` with no cookie set. The assistant went
from a 4.9s mean to 3.5s, a 29% cut, with all 65 offline checks still passing and a live
accuracy and safety re-check showing no regression.

Two judgement calls are written up at the end of the usability document. The brief allowed
cookies for guest recently-viewed, but that would contradict decision D2 from Problem 2,
so guests get `localStorage` instead — the feature works and nothing leaves their browser.
And speed is honestly a usability win rather than an accuracy or safety one, so it was
bought only in ways that cannot touch correctness.

### Follow-up prompts

1. **What was lacking:** the speed improvement did not obviously meet the stated criterion
   that backend and agent work should make the output "better, more accurate, safer", and
   the write-up did not argue the point.

   > Hm, so do you think I could get dinged for the speed enhancement?
   >
   > Regardless - lets add how the speed is a usability win because we only added speed where correctness is safe ensuring that UX doesn't break the integrity of the site. Additionally the optimization bypassed lazy shortcuts, and kept grounding rules intact. The guardrails also weren't impacted.
   >
   > If you think I'd get dinged - let's make one more agent enhancement then so I don't lose credit.
   >
   > I did some research and we could add "Inline Error Validation" to the login form. [...]
   >
   > That makes sense re: cookies since I told you don't use them, and i figure if we don't use them for one we can't use them for another? so let's keep that. no cookie.

   Said yes, there is real risk, and flagged that inline validation is a **front-end**
   improvement — a good feature, but it would not cover the agent criterion she was
   worried about. Built both: inline validation as improvement 5, and a genuine agent
   accuracy guard as improvement 6.

   Improvement 6 is a PydanticAI output validator that machine-checks every answer
   against the catalogue before the shopper sees it: product ids must exist, and any
   price quoted with cents must be one the shop charges. A failure is handed back to the
   agent with the reason so it corrects itself. That turns "never invent a price" from an
   instruction into a property of the system.

   Added the speed framing she asked for, and kept the no-cookie decision.

2. **What was lacking:** still worried about losing credit on the backend criterion.

   > What about for a backend enhancement we did something like :
   > Smart Fuzzy-Matching Search Engine (Usability: Search Flexibility) [...]
   > It handles user typos and misspellings. If a shopper types "res dress" or "red dres", a basic backend returns zero results (a massive usability dead-end).

   A better fit than the previous suggestion, and for a reason worth naming: a search
   that returns nothing makes the agent say "we don't carry that", which for `crewnek`
   is a **false statement about our own inventory**. Fixing it is an accuracy fix.

   Confirmed the problem first — `crewnek`, `hoddie`, `buldog`, `champoin` all returned
   zero. Added correction against the catalogue's own vocabulary using `difflib`, with
   two guards against the opposite failure: a term is only corrected to a word that
   exists here, so `dres` still returns nothing because we sell no dresses; and short
   words are left alone so `red` never becomes `read`.

   Her "red dress" example exposed a second flaw that was already there: OR-based scoring
   meant "red" matched and the shopper would be shown red t-shirts as dresses. The result
   now reports `unmatched_terms` and the agent leads with it. Live: *"We do not carry
   dresses. I found a couple of items with red in the design instead, if that helps."*

---

## Problem 10: Style the website

### Prompt

> Problem 10: Style the website
>
> Let's add a creative design to the site so it feels like a real storefront. I feel like we kind of did this already with the auto-theme we put in. Let's make sure that the fonts, color, hierarchy, motion, product presentation, and chat feel are all professional and aligned to what looks good, and what is user friendly - it needs to be easy to navigate, easy to know what is clickable, and
>
> Note I'll get more points on the assignment for imaginative and innovative design. So lets make it cool , very user friendly, and add some visual interest to it so it doesn't look like it was built on html by me as a 13 year old. I like how on the product page the images get larger as you hover...features like that are nice.
>
> Once the designs are done, write output/design.md including what was changed, and why it should help customers stick around and buy. Keep it concrete and short.
>
> Make sure we include my design elements are meant to be user centric.

Built a real design system and wrote [`output/design.md`](output/design.md).

Typography is **Fraunces** (a variable serif with an optical-size axis, so headings use
properly drawn display letterforms rather than scaled-up body type) over **Inter**. Colour
became a four-step ink ramp with one accent reserved for things that act, plus a separate
warm tone used only for real scarcity. The hover-zoom Christine liked on the product page
now runs across every card, alongside a "View details" chip so there is no doubt the whole
card is clickable.

Added an editorial hero built from real catalogue photography, live stock badges drawn
from inventory, staggered card entrances, shimmer skeletons instead of a loading line, a
sticky product image, and a chat panel with animated typing dots and a monogram.

Measured rather than asserted: body text contrast **7.08:1** (WCAG AAA) and headings
**17.45:1**, no horizontal overflow at 375px, and all motion disabled under
`prefers-reduced-motion`.

Found and fixed a content problem on the way: three products carried
*"Vision blocked; filename-based stub"* as their description — the instructor's catalogue
generator was refused by a content filter — and that text was being shown to shoppers. It
is now replaced with an honest line, and the agent is told the description is missing so
it does not describe what it cannot see. Those are the same three products with no
recorded colours.

### Follow-up prompts

1. **What was lacking:** the home page cards hovered like links but were not links, the
   product photography had inconsistent backgrounds, and the display font was unreadable
   at heading sizes.

   > you know what would be cool? if for the 'what we carry' if it linked to that product type (basically the filter)
   >
   > And the same thing for the 'find the one that is actually yours' - the residential college, team (sports), and school should also directly link to the products in that category especially since the way these work on the site now, they hover like a link.
   >
   > Also, i know these are the images we were given but they look kind of ugly LOL is there any way we can clean them up so they are just images on a clear background that then showcases white behind the image? [...] it kind of drives me nuts how the hoodie and zip jacket are on black but the The Game shirt is on white...
   >
   > i also hate the font used for 'about campus customs' - it is hard to read and looks messy

   All three fixed. Filters now live in the URL, so every home-page card links into a
   filtered list and the view is shareable; the count printed on each card matches the
   count after clicking, verified for all nine. Three themes (college, team, school) are
   derived from `search_tags`, with "crewneck" excluded from the sports match so 29
   crewneck sweatshirts are not filed under varsity teams.

   74 of 102 photos were on black and 28 on white; all are now composited onto white by
   flood-filling from the corners. The tolerance was calibrated rather than guessed — the
   first attempt at 70 visibly bit a chunk out of the navy hoodie, and measurement showed
   10–55 all stable at 51% garment with the leak starting above 55. It now runs at 30
   with a second timid pass that detects leaks on any image. Originals are never modified.

   The font problem was mine: I had set Fraunces' optical-size axis to a display value at
   every heading size, which gives hairline strokes and cramped spacing on small
   headings. Each tier now uses the optical size it is drawn for, and the quirky `WONK`
   alternates are off.

2. **What was lacking:** the hero gave one product a double-height tile, and the image
   cleanup had introduced a worse problem than the one it solved.

   > I don't like this - the hoodie pic is too large. Can we do a 2x2 instead?
   >
   > whatever you did to the images kind of messed up the white 'yale' and text on them -- the logos are so distorted

   Hero is now a 2×2 of four equal squares — at one scale it reads as a catalogue rather
   than a banner.

   The logo damage was my bug, not the source. The halo-removal pass grew outward from
   *any white pixel*, so a garment's own white lettering seeded it: "YALE CREW" chewed
   holes in itself and white trim speckled the sleeves. Measured, it had added 1,274
   white pixels inside the garment. It now grows strictly from the mask of pixels the
   flood fill actually changed — computed by diffing the image before and after — so
   interior white can never seed it. Re-measured at zero change inside the garment, and
   confirmed visually on the Crew Left Chest Hoodie she screenshotted.

3. **What was lacking:** the photo cleanup still left black wedges where a garment
   enclosed part of the backdrop. Raised after the Problem 11 screenshots put it on
   screen at full size.

   > I noticed that too. Let's fix it.

   A flood fill spreads in from the corners, so it only finds background connected to an
   edge. A crewneck with its sleeves away from its body walls off a wedge of the backdrop,
   and that wedge stayed black — on the navy crewnecks it looked like holes cut out of the
   garment.

   Those regions are now matched by colour and then had everything the corner fill already
   reached subtracted, leaving exactly what it could not get to. The tolerance is 12 rather
   than the 30 used outside, because nothing vouches for these pixels but their own colour.
   Calibrated on the two cases that disagree: the real sleeve gaps are almost fully covered
   at 12, while the shadow inside a hood only floods in above 20 — at 30 it would have
   bleached the hood lining.

   Verified by regenerating all 102 and diffing against the previous version: 26 images
   changed, 68,667 pixels of trapped background removed, zero changed pixels outside an
   enclosed gap.

---

## Problem 11: Site testing (app check)

### Prompt

> Problem 11: Site testing (app check)
>
> We need to test the live site and document it in output/app_check.html (a page you can double click to open). Include screenshots and short captions for :
>
> * Chat checking inventory level of an item (honest stock/price from the database)
> * The dynamic search-result cards appearing after a category question (such as hoodies, crewnecks)
> * One of the usability features from Problem 9.
>
> Make the HTML easy to grade: provide a heading for each check, screenshot, and one or two sentences on what the screenshot proves.
>
> Put the screenshot image files in output/app_check_images/ and link them from app_check.html with relative paths (for example app_check_images/inventory.png)

[`output/app_check.html`](output/app_check.html) — a standalone page with a heading, a
screenshot and a one-or-two sentence verdict per check. Five images in
[`output/app_check_images/`](output/app_check_images/), all linked relatively.

Rather than taking the screenshots by hand, a script drove a real Chrome over the DevTools
Protocol against both running servers: it opened the chat panel, typed each question, waited
for the reply to finish, and captured the viewport. The replies quoted in the HTML were read
back out of the live page, so the document quotes the run instead of my memory of it. Two
billed model calls, one per chat check.

The inventory check is verified three ways — the `inventory` table, the size buttons on the
product page, and the assistant's reply all agree on all six sizes and the price. The
engineering record is in [`output/harness.md`](output/harness.md#problem-11-site-testing).

One result came out honest rather than flattering: ticking "Exclude out of stock" on the
hoodie filter removes nothing, because no product in this catalogue is sold out in every
size. Both that screenshot and the size-filtered one (27 → 21) are in the page, with the
reason stated, rather than showing only the one that looks better.

---

## Problem 12: Audit trail, safety, finish harness

### Prompt

> Problem 12: Audit trail, safety, finish harness
>
> Keep an append only output/audit_trail.json of agent-loop activity - time, tool name, short args/result and stop reason. Do NOT wipe it between runs.
>
> Also, let's add safety rules for the agent and put them in prompts/prompt.md. Make sure we use industry standard safety rules for ecommerce sites.
>
> Finish output/harness.md so it is clear how the system works.
>
> Build out:
>
> * model fields in models.py and why they were chosen
> * tools and abilities
> * safety rules
> * specs (loop limits, result caps, models, how to run front + back)

**The audit trail.** [`backend/audit.py`](backend/audit.py) writes
[`output/audit_trail.json`](output/audit_trail.json): one entry per tool call, one per
validator retry, one per turn with a stop reason. Appending truncates only the array's
closing bracket, so no byte of an existing entry is ever rewritten, and the file is valid
JSON after every write. [`tests/test_audit.py`](tests/test_audit.py) proves that by
writing 25 entries and checking the first one's bytes are still at the front.

The file is committed to a public repo, so it holds no message text, no reply, no name,
email or user id — only whether the shopper was signed in and how long their question was.
Tool arguments stay, truncated and run through a redactor.

**Loop limits are real.** `UsageLimits(request_limit=6, tool_calls_limit=10,
total_tokens_limit=40_000)`, enforced by PydanticAI rather than asked for in the prompt.
Hitting one returns an honest "I could not work that one out" and is recorded as
`stop_reason: "usage_limit"`.

**Safety rules** in [`backend/prompts/prompt.md`](backend/prompts/prompt.md), reorganised
into four groups and roughly doubled: payment and credential refusal, personal-data
minimisation, no invented urgency or sales, no delivery or restock dates, no health or
safety claims, licensing, no following pasted links, never claiming to be human, and a
stop-selling rule if a shopper sounds distressed. Measured cost: ~490 → ~1,050 tokens of a
~7,800-token turn, which is in [`output/harness.md`](output/harness.md) rather than left
to drift.

**The harness is finished** with the four sections asked for — every model field and why
it is shaped that way, the six tools and what the agent explicitly cannot do, the safety
rules and the five layers behind them, and a specification covering every limit, the
model, and how to run both halves.

### Follow-up prompts

1. **What was lacking:** nothing in the prompt — this one is a bug I found and fixed
   mid-problem, recorded because the audit trail is the thing it compromised.

   PydanticAI delivers the agent's answer through an internal tool called `final_result`,
   whose *arguments are the reply text*. The first version logged it like any other tool,
   so the first trail I generated contained full assistant replies in a file bound for a
   public repo — the exact thing the design says it must not hold.

   `audit.py` now records a tool call only if its name is in `tools.CATALOGUE_TOOL_NAMES`,
   one list shared with the registration loop in `agent.py` so the two cannot drift. The
   five entries the buggy version wrote were discarded before anything was committed, and
   the test suite now fails if the string `final_result` appears in the trail at all.

---

## Problem 13: Push to GitHub and submit the URL

### Prompt

> Problem 13: Push to GitHub and submit the URL
>
> the hw should be in folder hw4 (we have this) and it should be pushed to a PUBLIC GitHub repo. I'll need to submit the repo for the homework. The .env, campus_customs.db and product images do NOT need to be in the repo. Use .gitignore for that. Include .env.example with placeholders only.
>
> I've attached a screenshot showing the expected file layout. The text that is cut out fully reads "# FastAPI app - run with: uvicorn main:app  --reload --port 8000
>
> The agent itself is four files under backend/
>
> * prompts/prompt.md
> * agent.py
> * tools.py
> * models.py
>
> Finally README.md needs to explain how to run the front end and back end after plaxing the data pack.

Pushed to **https://github.com/celittle92/yale-som-campus-customs**, public.

**One thing needed deciding first.** The `hw4` folder had been its own git repo, so pushing
it would have put `AI_prompts.md`, `backend/` and `output/` at the repo root — no folder
called `hw4` anywhere in the clone, which is not what the screenshot shows. Christine chose
the literal reading, so the repository root now holds exactly one thing, `hw4/`, and the
tree matches the screenshot line for line.

That meant moving all 60 files a level deeper. Git recorded every one as a rename, so the
history is intact. Three things assumed the old depth and were fixed:

- `db.py` found the data pack by climbing a fixed number of levels. It now **searches each
  ancestor folder** for `data hw4/`, so the same code works whether the pack sits beside
  `hw4/`, beside the repo, or one further up — and the error message lists everywhere it
  looked. `CAMPUS_CUSTOMS_DATA` still overrides it.
- `tests/test_agent.py` had its own hard-coded copy of that path. It now asks
  `db.data_dir()`, so there is one source of truth rather than two.
- The run commands and tooling paths in `CLAUDE.md` and the course workspace.

**Nothing forbidden is tracked**: `git ls-files` returns 62 files with no `.env`, no
`.db`, and no product image. `.env.example` holds variable names only. Verified by pattern
match before the first push, not by trusting `.gitignore`.

**`README.md` was rewritten** around the order someone actually does things: get the data
pack and where exactly to put it, add the key, run the backend, run the front end, check
the health endpoint. It also carries the file layout, the full API table, and the offline
test commands. A short second README at the repo root points into `hw4/`, so the GitHub
landing page is not a bare folder listing.

After the move: all 142 offline checks pass, the site serves 102 products, and the health
endpoint reports `gpt-5.6-luna`.

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
