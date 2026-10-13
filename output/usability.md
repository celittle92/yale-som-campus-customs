# Usability improvements

Four improvements to the Campus Customs site: two on the front end, two in the
backend and agent. Written before the work, and updated with measured results as each
landed.

## Contents

1. [Product filter — type, colour, size, and exclude out of stock](#1-product-filter)
2. [You might also like — similar items on a product page](#2-you-might-also-like)
3. [Recently viewed](#3-recently-viewed)
4. [A faster assistant](#4-a-faster-assistant)
5. [Two judgement calls worth stating](#two-judgement-calls-worth-stating)

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

---

## Where to find each one in the running app

| Improvement | Where |
|---|---|
| Product filter | **Products** page, above the grid. Type, Colour, Size, "Exclude out of stock" |
| You might also like | Bottom of any product page, e.g. `/products/basic-hoodie-big-yale` |
| Recently viewed | Top of the **Products** page, after opening a product or two |
| Faster assistant | The chat panel — replies now land in about 3.5s instead of 4.9s |

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
