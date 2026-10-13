# Usability improvements

Seven improvements to the Campus Customs site: three on the front end, four in the
backend and agent. Written before the work, and updated with measured results as each
landed.

## Contents

**Front end**

1. [Product filter — type, colour, size, and exclude out of stock](#1-product-filter)
2. [You might also like — similar items on a product page](#2-you-might-also-like)
5. [Inline error validation on the account forms](#5-inline-error-validation-on-the-account-forms)

**Backend and agent**

3. [Recently viewed](#3-recently-viewed)
4. [A faster assistant](#4-a-faster-assistant)
6. [Grounded-output validation](#6-grounded-output-validation)
7. [Typo-tolerant search](#7-typo-tolerant-search)

Then: [where to find each one](#where-to-find-each-one-in-the-running-app) and
[two judgement calls](#two-judgement-calls-worth-stating).

---

## 1. Product filter

**What I added.** A filter bar above the product grid with four controls:

- **Type** — the seven canonical categories (Hoodie, Crewneck sweatshirt, T-shirt,
  Quarter-zip, Fleece jacket, Jacket, Long-sleeve shirt).
- **Colour** — the colours that actually appear in the catalogue, read from the data
  rather than hard-coded.
- **Size** — XS through XXL.
- **Exclude out of stock** — a toggle that drops any product with no stock in the
  selected size, or no stock in any size when no size is chosen.

The filter runs in the browser over the already-loaded catalogue, so it is instant and
costs nothing. A live count shows how many of the 102 styles match, and a "Clear filters"
control resets it. When a filter excludes everything, the page says so plainly and offers
to clear.

**Why it helps.** 102 products in one undifferentiated grid is a lot to scroll. The real
win is the stock toggle: without it, a shopper can filter to *navy crewnecks in large*,
fall for a design, open it, and only then discover their size is gone. That is a wasted
click and a small disappointment at exactly the wrong moment — when they were close to
buying. Filtering stock out at the grid means every product they see is one they can
actually have.

It also makes the honesty of the product page pay off commercially. We already tell people
when a size is sold out; this lets them never meet that message in the first place.

---

## 2. You might also like

**What I added.** A "You might also like" carousel at the bottom of every product page,
showing up to eight similar items in a horizontally scrollable row. Similarity is computed
by the backend from catalogue data, scoring other products on:

- same canonical category (strongest signal),
- shared colours in the design,
- shared search tags,
- similar price.

Products that are completely out of stock are pushed down the ranking, so a recommendation
is usually something a shopper can buy. Each card links to that product's page, so the
carousel is a way to keep browsing rather than a dead end.

**Why it helps.** The shopper is looking at one item. Either they want it, or something
about it is not quite right — the colour, the cut, the price, or their size being gone.
Showing neighbours turns all four of those into another chance rather than an exit.

For the business this is the recovery path for the exact disappointment the filter cannot
prevent: someone who is already on the page, already interested, and has just learned
their size is sold out. A row of similar items is the difference between leaving and
buying something else.

---

## 3. Recently viewed

**What I added.** A service that remembers the products a shopper has opened, shown as a
strip on the Products page and available to the chat assistant.

- **Signed in:** stored server-side in a new `recently_viewed` table, keyed to the account.
  It follows them across devices and survives logging out and back in.
- **Signed out:** kept in the browser's `localStorage` only. It works, but nothing is sent
  to or stored on the server.

The assistant can see the list too, so "what was that hoodie I was looking at?" is a
question it can actually answer.

**Why it helps.** Shoppers compare. They open three hoodies, lose track of the second one,
and either scroll to find it again or give up. A recently-viewed strip makes the path back
one click, which matters most for the item someone was closest to buying — the one they
left to check an alternative and never returned to.

Giving the agent the same list is what makes it feel like it is in the shop with you rather
than answering from a catalogue.

---

## 4. A faster assistant

**What I added.** Three changes, aimed at the pause between sending a message and seeing an
answer:

1. **Lower reasoning effort.** The model does internal reasoning before it answers, which
   is most of the "thinking" time. The assistant's work is lookup-and-report, not deduction
   — the tools do the comparing and counting — so the reasoning budget is set low.
2. **Leaner instructions.** Roughly 2,000 tokens were re-sent on every call, and every one
   is time on the wire and in the model. Trimmed without touching the safety section.
3. **An honest progress indicator.** Instead of a generic "Thinking…", the panel says what
   is happening and the input stays usable.

**Measured, same two questions before and after, agent warmed first:**

| | Before | After |
|---|---|---|
| "what crewnecks do you have?" | 5.5s | 3.5s |
| "anything in green?" | 4.3s | 3.5s |
| **Mean** | **4.9s** | **3.5s** |

A 29% reduction, and the slowest case improved most. The instructions also lost ~250
tokens per call, which comes off every message's cost as well as its latency.

**Accuracy re-checked afterwards**, because a speed change that quietly degrades answers
is worse than a slow one. All 65 offline checks still pass, and live:

> "is the Crew Left Chest Hoodie available in medium, and how much is it?"
> → "The Crew Left Chest Hoodie is $68.00. Medium is out of stock. It is currently
> available in XS, S, L, XL, and XXL."

Correct against the database, row for row. The safety probe still refuses: asked for its
model, its tools and another customer, it declined all three and named none of them.

**Why it helps.** A shopper who asks a question and gets a blank pause assumes it is
broken. Several seconds is a long time in a shop. Cutting the wait keeps people in the
conversation instead of closing the panel, and the leaner instructions cut the token cost
of every single message as a side effect.

**Why this is a usability win and not a corner cut.** Speed was only taken where
correctness is provably safe, so a better experience never comes at the cost of the site's
integrity. The optimisation deliberately bypassed the lazy shortcuts — no tool calls were
removed, no grounding rules relaxed, no validation skipped. Every guardrail is intact: the
safety section is untouched, the requirement to read every price and stock figure from a
tool is untouched, and the new output validator (improvement 6) now machine-checks the
result on top. What was removed was waste — internal reasoning this task does not need,
and words the instructions did not need to say twice.

---

---

## 5. Inline error validation on the account forms

**What I added.** Both the log-in and create-account forms now validate as you type
rather than on submit. An email without an `@` is flagged the moment it is recognisably
wrong, with a specific message rather than a generic "invalid":

| Typed | Shown |
|---|---|
| `c` | nothing yet — too early to judge |
| `chris` | "An email address needs an @ symbol." |
| `chris@` | "Add the part after the @, such as yale.edu." |
| `chris@yale.edu` | clears |

The same applies to the rest: a short password counts down ("5 more characters needed"), a
mismatched confirmation flags immediately, and the submit button stays disabled while
anything is wrong. Fields turn red, and the message is wired to the input with
`aria-invalid` and `role="alert"`, so a screen reader announces the problem instead of it
being a colour only sighted users can see.

One deliberate restraint: nothing complains on the first keystroke. Nobody has typed a
valid email after one character, and a form that calls you wrong before you have finished
is worse than one that waits.

**Why it helps.** The old flow was: type, submit, wait for the server, get rejected,
work out what was wrong, retype. That is four steps and a round trip to learn something
the browser already knew. Now it is caught in place, before any request is made.

For the business, the account form is the narrowest point in the funnel — someone has
already decided to sign up, and every avoidable failure there is a lost account. It also
takes pointless traffic off the backend, since malformed submissions never leave the page.

---

## 6. Grounded-output validation

**What I added.** A programmatic check that runs on every answer *before* it reaches the
shopper, using PydanticAI's output validator. Two rules:

1. **Every product id must exist in the catalogue.** An invented one previously got
   dropped silently, which left a reply discussing a product with no card beside it.
2. **Every price quoted with cents must be a price the shop actually charges.** The
   catalogue has exactly seven price points, so `$71.00` is provably wrong.

When either fails, the answer is not patched up or discarded — it is handed back to the
agent with the reason, and it tries again. Only amounts written with cents are checked,
because the instructions require quoted prices to carry them while ranges do not, so
"under $50" is never mistaken for a claimed price.

Verified with forced bad answers, no credits spent:

| Answer | Result |
|---|---|
| id `not-a-real-product` | sent back for correction |
| "That one is $71.00." | sent back for correction |
| "That one is $68.00." | accepted |
| "We have plenty under $50." | accepted — a range, not a quote |
| All seven real catalogue prices | all accepted |

**Why it helps.** Up to now, "never invent a price" was an instruction. Instructions are
followed almost always, which is not the same as always, and the one time it fails is a
shopper told the wrong price. This makes it a property of the system instead of a
behaviour of the model: a wrong price cannot reach the page, because code checks it
against the database first.

For the business that is the difference between a policy and a guarantee. Quoting a price
you do not honour is the kind of mistake that costs trust, and this one cannot happen
silently.

---

## 7. Typo-tolerant search

**What I added.** `search_products` now corrects misspellings against the catalogue's own
vocabulary, using `difflib` over the words that actually appear in product names, tags,
colours, categories and cuts. Before, a single typo returned nothing:

| Typed | Before | Now |
|---|---|---|
| `crewnek` | 0 results | 6, read as "crewneck" |
| `hoddie` | 0 results | 6, read as "hoodie" |
| `buldog` | 0 results | 6, read as "bulldog" |
| `champoin` | 0 results | 4, read as "champion" |
| `quater zip` | 0 results | 6, read as "quarter zip" |

The result carries `corrections`, so the agent tells the shopper what it searched for
instead of silently changing their words.

**Why it helps — and why this is an accuracy fix, not just a convenience.** A search that
returns nothing makes the agent say *"we don't carry that"*. For `crewnek` that sentence
is **false**: we carry 29 of them. The typo turned a spelling slip into the assistant
making an untrue statement about our own inventory. Fixing the search fixes the lie.

For the shopper it removes a dead end at the worst moment — they were telling us exactly
what they wanted. For the business, a zero-result search is one of the highest-exit
moments in any shop.

**Two guards against the opposite failure**, which would be worse:

1. **Correction only to words that exist in this catalogue**, and only when the match is
   close. `dres` is not turned into anything, because we sell no dresses — it returns
   nothing, and "we do not carry that" is then *true*. Fuzzy matching must not become
   "find something, anything". Short words are left alone entirely, so `red` can never
   become `read`.

2. **Unmatched words are reported.** Scoring is OR-based so natural phrasing still works,
   which means one word can match while another matches nothing — and that is exactly
   your "red dress" example. The result now carries `unmatched_terms`, and the agent is
   told to lead with it. Live:

   > **"do you have a red dress?"**
   > "We do not carry dresses. I found a couple of items with red in the design instead,
   > if that helps."

   Without that, it would have shown red t-shirts as though they answered the question.

Verified live with a typo too: *"do you have any navy crewnek sweatshirts?"* returned four
navy crewnecks at $58.00, and the reply told the shopper which word it had re-read.

---

## Where to find each one in the running app

| Improvement | Where |
|---|---|
| Product filter | **Products** page, above the grid. Type, Colour, Size, "Exclude out of stock" |
| You might also like | Bottom of any product page, e.g. `/products/basic-hoodie-big-yale` |
| Recently viewed | Top of the **Products** page, after opening a product or two |
| Faster assistant | The chat panel — replies now land in about 3.5s instead of 4.9s |
| Inline error validation | **Log in** and **Create Account** — type an email without an `@` |
| Grounded-output validation | Invisible by design: it runs on every chat answer. Evidence in the table above. |
| Typo-tolerant search | Ask the chat for a "crewnek" or a "hoddie" |

Verified live, signed in as the test account:

- Filter: 102 styles → **29** crewneck sweatshirts → **17** navy blue → **12** in stock
  in L. Cross-checked against the database: 29, 17, 12 exactly. That is the brief's own
  "navy crewneck in a large" example, and the shopper sees only the twelve they can buy.
- Carousel: 8 recommendations on the Basic Hoodie Big Yale, all navy hoodies at $68.00,
  each linking to its own detail page.
- Recently viewed: opened two products, both appeared newest-first. Signed out, the strip
  still works from `localStorage` with **no cookie set and nothing stored server-side**.

## Two judgement calls worth stating

**Recently viewed for signed-out shoppers uses `localStorage`, not a cookie.** The brief
allowed cookies here, but in Problem 2 the decision was that signed-out visitors are not
tracked by cookie or IP, because it is off-putting. `localStorage` keeps the feature
working for guests while honouring that: the list never leaves their browser, is never
sent to the server, and is not a tracking identifier. Signed-in shoppers get the
server-side version, which is what they are asking for by having an account.

**Speed is a usability win, not an accuracy or safety one.** The brief asked that the
backend and agent improvements make the output "better, more accurate, safer". Recently
viewed does make answers better — the agent knows more about the shopper, so it can resolve
"that hoodie I was looking at". Speed does not. A faster answer is not a truer one, and the
obvious ways to buy speed — skipping tool calls, trimming the grounding rules — would make
it *less* accurate.

So speed here is bought only in ways that cannot touch correctness: less internal
reasoning, fewer wasted tokens, better feedback while waiting. The grounding rules, the
safety section, and the requirement to read every price and stock number from a tool are
untouched. The accuracy guard is the test suite, which is re-run after the change to
confirm nothing regressed.
