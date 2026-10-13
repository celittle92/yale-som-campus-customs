# Design

What the Campus Customs storefront looks like, and why each choice is there. Every
decision below is user-centric first: the goal is a shopper who can tell at a glance what
this shop sells, what is clickable, and whether they can actually have the thing they are
looking at.

## The direction

**Warm editorial.** Cream ground, deep ink type, one restrained accent in Yale navy.
Not the default black-on-white of a template, and not a loud e-commerce palette — this
reads like a shop with a point of view, which is what a licensed apparel store in New
Haven should feel like.

## What changed

### Typography

**Fraunces** for display, **Inter** for everything you read quickly.

Fraunces is a variable serif with an optical-size axis, so headings use tighter,
higher-contrast letterforms at large sizes — the difference between type that was *set*
and type that was scaled up. Inter handles body copy, labels and UI.

**Optical size is matched to the size the text is actually set at** — `opsz 72` for page
titles, `32` for section headings, `18` for card titles. The first attempt used the
display value everywhere, which gave hairline strokes and cramped spacing on smaller
headings; Christine's words were "hard to read and looks messy", and she was right. An
optical-size axis is only useful if you actually use it.

Fraunces' `WONK` alternates are switched **off**. The quirky letterforms are charming in
isolation and harder to read in a paragraph heading. Character is good; legibility wins.

**Why it helps:** a storefront is judged in about a second. Two well-paired typefaces do
more for "this is a real business" than any amount of decoration, and Inter at 15–18px
keeps the actual reading effortless.

### Colour and hierarchy

- A four-step ink ramp (`ink` → `body` → `muted` → `line`) so importance is expressed by
  weight and contrast rather than by boxes and borders.
- `sand` as a second surface, used behind product photography so garments on white
  backgrounds do not float in nothing.
- One accent, used only for things that act: links, buttons, the selected size, prices.
- A separate warm `low` tone reserved for scarcity, so "Only 2 sizes left" never reads as
  decoration.

**Measured:** body text sits at **7.08:1** contrast and headings at **17.45:1** against
the cream ground. 7:1 is WCAG's AAA threshold for body text, so this passes the strictest
level rather than scraping the minimum.

**Why it helps:** a shopper scanning 102 products should never have to work out what is
important. Price and name are the two things the eye lands on, and nothing else competes.

### Product presentation

- Cards lift on hover and the photograph zooms slowly inside its frame — the effect you
  liked on the product page, now consistent everywhere.
- A **"View details →"** chip fades in on hover, so there is no doubt the whole card is
  clickable rather than just the title.
- **Real stock badges**, drawn from live inventory: "Only 2 sizes left" in the warm
  signal tone, "Sold out" in solid ink. Never invented urgency — it only appears when the
  database says so.
- The product page image is **sticky** on wide screens, so it stays put while you read the
  details. On a product page the photo is the thing you keep glancing back at.
- Sizes are pills; the selected one fills solid navy, sold-out ones are struck through and
  unclickable.

**Why it helps:** the lift and the chip answer "can I click this?" before anyone has to
guess. The badges answer "can I have it?" at the grid, not three clicks later — which is
the same disappointment the stock filter exists to prevent.

### Motion

Motion is used to explain, never to perform:

- Cards **stagger in** by index, so a grid resolves in sequence instead of flashing.
- **Skeleton placeholders** with a shimmer replace "Loading…", so the page does not jump
  when real content arrives.
- Buttons lift a single pixel on hover and the hero's arrow slides.
- The chat panel scales up from its launcher rather than appearing.

Everything is wrapped in `prefers-reduced-motion`. If a visitor's system asks for less
motion, all of it drops to near-zero duration. **Decoration should never make anyone
queasy.**

### The chat

- A **CC monogram** in the header, so the assistant is a presence rather than a text box.
- Messages animate in and use asymmetric corners — the tail points at who is speaking.
- "Thinking…" became **three animated dots**, the convention everyone already reads as
  "it heard you, it is working".
- The launcher has a soft pulsing dot, which is the only looping animation on the site.

**Why it helps:** the gap between sending and receiving is where people give up. Dots say
*working*; a frozen panel says *broken*.

### Navigation

Sticky, translucent, blurred. Nav links grow an underline from the left on hover and stay
underlined when active. The account action is a filled pill; secondary actions are
outlined or plain. **One look per level of importance, used consistently.**

### Every entry point goes somewhere

The home page used to describe categories without letting you shop them. Now every card
is a link into a filtered product list, and **filters live in the URL** — so a filtered
view is shareable, survives a reload, and the back button works.

| Card | Goes to | Products |
|---|---|---|
| What we carry → Hoodies | `/products?type=Hoodie` | 27 |
| → Crewneck sweatshirts | `?type=Crewneck sweatshirt` | 29 |
| → T-shirts, Quarter-zips, Fleece jackets, Jackets | `?type=…` | 25 / 11 / 6 / 2 |
| Your residential college | `/products?theme=college` | 19 |
| Your team | `?theme=team` | 29 |
| Your school | `?theme=school` | 13 |

The count printed on each card is the count you get after clicking — verified for all of
them. A theme filter shows as a removable chip, so it is obvious why the list is short
and one click undoes it.

The three themes come from `search_tags`, with one exclusion that matters: **"Crew" is a
sport, but "crewneck" is a collar.** Matching naively would have filed all 29 crewneck
sweatshirts under varsity teams.

**Why it helps:** the cards already looked clickable — they lifted on hover. A thing that
looks like a link and isn't one is worse than a plain paragraph. Now the three ways people
actually shop for Yale gear are each one click from the front page.

### Product photography

The supplied photos were inconsistent: **74 of 102 garments sit on pure black, 28 on
white.** Side by side in a grid that reads as a mistake and pulls the eye off the product.

All of them are now composited onto white. The background is flood-filled from the
image's four corners, so a garment in the middle of the frame is never touched however
dark it is.

**The tolerance was calibrated, not guessed.** On the navy-hoodie-on-black shot, fill
tolerances from 10 to 55 all leave the same 51% of the frame as garment; at 70 it drops
to 47.6%, the fill escaping through a dark shadow and eating part of a sleeve. The first
version used 70 and did visibly bite the hoodie. It now runs at 30, and every image gets
a second, timid pass at 12 — if the two disagree about how much survived, the generous
fill leaked and the timid result is used instead.

**The supplied images are never modified.** Originals are read-only; results are cached in
a gitignored directory, and image URLs carry a version marker so a browser holding the old
black-background copy fetches the new one.

## One content fix worth recording

Three products — `benjamin-franklin-t-shirt`, `berkeley-sweater-fleece-jacket`,
`timothy-dwight-college-crewneck` — had no real description in the supplied catalogue.
Their rows read *"Campus Customs product photo (…). Vision blocked; filename-based stub."*
— the vision pass that generated the catalogue was refused by a content filter, the same
kind of refusal this project hit in Problem 5.

That text was being shown to shoppers, and it looks broken. It is now detected and
replaced with *"We have not written a description for this one yet — the photo is the best
guide, or ask us in the shop."* The agent is told separately that the description is
missing, so it describes nothing it cannot see.

These are the same three products with an empty colours array, so the colours message no
longer points at a description that does not exist.

## Accessibility, because it is part of the design

| | |
|---|---|
| Body text contrast | 7.08:1 — passes WCAG AAA |
| Heading contrast | 17.45:1 |
| Focus ring | Visible on every interactive element, offset so it is never clipped |
| Motion | Fully disabled under `prefers-reduced-motion` |
| Form errors | `aria-invalid` + `role="alert"`, so problems are announced, not just coloured |
| Stock state | Stated in text, never colour alone |
| Mobile at 375px | No horizontal overflow; hero, grid and chat all reflow |

## Why this should keep people shopping

1. **It looks like a business.** The typography and spacing do that work before a single
   product loads, and trust is the precondition for a purchase.
2. **Nothing is ambiguous.** Hover states, the view-details chip and one consistent accent
   mean a shopper never wonders what is clickable.
3. **Bad news arrives early.** Sold-out and low-stock badges appear in the grid, so nobody
   falls for something they cannot buy.
4. **Waiting feels handled.** Skeletons and typing dots keep the slowest moments from
   reading as failure.
5. **It works for everyone.** AAA contrast, real focus rings, and motion that respects the
   system setting — a shopper who cannot use the site cannot buy from it.
