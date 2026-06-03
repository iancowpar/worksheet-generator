# Panel talk script — master

Single source of truth for the full hour on June 3, 3:30pm ET. Built
to be scrollable on the day. Cold open, bridges, and close are
**inline in full**. Case 1 and Case 2 bodies reference the dedicated
narrative files because they're long; open those alongside this on
the day.

Companion files:
- `Case_1_Narrative.md` — full Case 1 spoken arc (~2,050 words)
- `Case_2_Narrative.md` — full Case 2 spoken arc (~2,000 words)
- `../../slides/panel-june3/index.html` — 16-slide deck

---

## Time budget for the full hour

| Block | Duration | Slides |
|---|---|---|
| Cold open — Starbucks frame | 45 sec | 2 |
| Two-cases setup | 30 sec | 3 |
| **Case 1 — AI Capability Layer** | **~13 min** | 4-9 |
| Bridge to Case 2 | 30 sec | (end of Case 1) |
| **Case 2 — UTA Upgrade Program** | **~13 min** | 10-14 |
| Throughline close | 45 sec | 15 |
| Open to Q&amp;A | 15 sec | 16 |
| **Panel Q&A** | **~28 min** | (stay on 16) |

The two presentations are table-setting. The Q&amp;A block is where
rapport is built and the offer is decided. Build the talk to *invite
the right questions*, not to answer everything in 30 minutes.

---

## 1 · Cold open — the Starbucks frame (45 sec · Slide 2)

**Context:** The week of May 23 2026, Starbucks retired its AI inventory
counting system nine months into a rollout across 11,000 stores. The
official statement called it *"a decision to standardize how inventory
is counted"* — careful phrasing for fixing something that didn't work.
The internal employee note Starbucks themselves shared was more honest:
*"The thought behind it was great, but the execution was proving
difficult."*

**Delivery script — say this out loud, Ian's voice:**

> "Before I get into the cases, quick frame. Starbucks fired its AI
> inventory system this week. Nine months in, eleven thousand stores.
> The official line called it 'a decision to standardize how inventory
> is counted,' which is a careful way to phrase fixing something that
> didn't work. The employee note Starbucks themselves shared was more
> honest: 'The thought behind it was great, but the execution was
> proving difficult.' That sentence is the pattern. You can do the
> thinking well and the deployment well and still miss the thing that
> actually matters, which is whether the people who have to live with
> the system are different on Tuesday. The two cases I want to walk you
> through are about what it took to make that part real."

**Why it works for this room:**

- **Tushaus** has been saying versions of this on podcasts for two
  years. Same dialect.
- **Rabideau's** institutional line is *AI embedded, not bolted on* —
  the UX version of the same idea.
- **Kapoor's** FinOps worldview is the financial version: measurement
  beats assertion.
- **Cipollone** has said culture and change management are the hard
  part of AI. This is exactly the gap between press release and reality
  she lives.

All four already believe a version of this. Naming it at the top tells
them you read the same landscape.

**Don't:**
- Don't perform indignation. Quiet diagnosis lands.
- Don't crib LinkedIn writer phrases ("deployment is not adoption").
  Use the public facts and the employee quote, then let the diagnosis
  land in your own vocabulary.
- Don't skip the cold open to save time. The frame is what makes the
  cases read as evidence of an alternative pattern, not as standalone
  accomplishments.

---

## 2 · Two-cases setup (30 sec · Slide 3)

**Delivery script:**

> "What I want to walk you through are two internal operating
> mechanisms I built. Different shapes of the same belief about how
> adoption actually works. The first one is behavior change inside a
> PM organization. The second one is risk visibility across a
> multi-year program. Different muscles. Same discipline. I'll spend
> about thirteen minutes on each, then we can open it up."

This is the only time you should explicitly name the time budget.
After this, the panel just experiences the cases.

---

## 3 · Case 1 — The AI Capability Layer (~13 min · Slides 4-9)

**Full spoken arc in `Case_1_Narrative.md`.** Six beats:

| Slide | Beat | Anchor |
|---|---|---|
| 4 | Title card | Six weeks. From one PM to twenty. |
| 5 | The catalyst | Vasu's question — *"How long would it take you to write me one of these?"* |
| 6 | Four pieces of infrastructure | Slash commands · Confluence dashboards · build board · GitHub repo |
| 7 | Three adoption shapes | Maria (direct) · Laura (observed) · Keith &amp; Vasu (propagated) |
| 8 | The Maria quote | *"It's magic. It feels like life will never be the same again."* |
| 9 | Measurement principle | Adoption measured by what stopped, not what launched. |

**Power phrases you want to hit somewhere in Case 1:**
- *"shared infrastructure built around real workflows people actually hated"*
- *"the honest measure of whether I'd built something good was whether
  it kept running when I wasn't running it"*

**Verbatim quotes — say these exactly:**
- Vasu: *"Wait. How long would it take you to write me one of these?"*
- Maria: *"It's magic. It feels like life will never be the same again."*

---

## 4 · Bridge from Case 1 to Case 2 (30 sec · end of Slide 9, transition into 10)

**Delivery script:**

> "The reason I tell that case the way I do, with the people named and
> the workflows named and the metrics held back, is because the lesson
> of the program isn't about the technology. It's about the
> discipline. Most AI enablement programs fail because they treat AI
> as a tool installation problem. License it, train people on it,
> declare adoption. The honest version is that AI is a behavior change
> problem. What I want to do with the second case is talk about a
> different shape of operating mechanism. Different muscle. Same
> belief about what it means to build something that actually lands."

That paragraph is the close of Case 1 *and* the bridge to Case 2.
Don't add a separate transition.

---

## 5 · Case 2 — The UTA Upgrade Program (~13 min · Slides 10-14)

**Full spoken arc in `Case_2_Narrative.md`.** Six beats:

| Slide | Beat | Anchor |
|---|---|---|
| 10 | Title card | 300 customers · $250M ARR · cliff edge by Nov 2026 |
| 11 | Four-source operating mechanism | Inputs · Jira labels with Leila · weighted top-5 |
| 12 | The negotiation | Pod-based vs complexity-based. Complexity won. |
| 13 | The university story | Five flags lit at once. Tre Morgan testimonial. |
| 14 | Outcomes (honest frame) | 40% / velocity rising / ahead. Lisa's decisions weren't changed. |

**Power phrases you want to hit somewhere in Case 2:**
- *"engineering's preference was operationally efficient. product's
  preference was operationally resilient."*
- *"the dashboard's value was the shared vocabulary it created across
  functions, not the executive judgment it replaced"*

**Verbatim quote — read off the slide:**
- Tre Morgan: *"Clear communication across teams, ensuring all
  stakeholders remained informed and aligned. A key contributor to the
  project's success."*

---

## 6 · Throughline close (45 sec · Slide 15)

**Delivery script:**

> "The throughline across both cases — the AI capability layer and the
> UTA upgrade program — is that the operating mechanisms I'm most
> proud of building are the ones that change what a function can
> *see*, not the ones that try to change what a function does. Case 1
> changed what twenty PMs could do with their week, by making the
> workflows they hated easier to retire. Case 2 changed what a
> multi-function program could see about its own risk, by making the
> data underneath the dashboard honest.
>
> Different muscles. Same belief. Build the conditions where the right
> thing becomes the easier thing, and the people you're working
> alongside will do the rest."

This is the most important sentence in the talk:
*"Operating mechanisms change what a function can SEE."*

If you only land one thing, land that.

---

## 7 · Open to Q&amp;A (15 sec · Slide 16)

**Delivery script:**

> "I'll leave it there. Happy to take questions — whichever would be
> most useful to dig into."

Then *stop talking*. Don't fill the silence. Let the first question come
to you.

---

## 8 · Q&amp;A frame (~28 min)

Q&amp;A is where the offer gets decided. Two principles:

1. **Stay in operator register.** Settled curiosity, not pitch energy.
   Treat each question as a conversation, not a quiz.
2. **Follow up on their answers.** Brooks's research: follow-up
   questions raise likability more than any other conversational move.
   When a panelist responds to your answer, ask them one follow-up
   question in their frame before continuing.

See `Panel_Council.md` and `Panel_Round_June3_Prep.md` for the
panel-shaped questions to drill against. The Q&amp;A drill at 1:45 today
will get you reps on the eight most likely.

---

## On-the-day checklist

| Time | Move |
|---|---|
| 12:30 | Lunch. No laptop. |
| 1:00 | Verbal dry-run Case 1 with me. |
| 1:30 | Verbal dry-run Case 2 with me. |
| 1:45 | Q&amp;A drill — 8 panel-shaped questions, cold. |
| 2:15 | Tech rehearsal — deck open, screen share check, audio check. |
| 2:45 | Close the laptop. Water. Walk. |
| 3:25 | Settle in. Breath. The work is already in the room with you. |
| 3:30 | Show up as the operator who's already done it. |

The script is done. Internalize. Don't read.
