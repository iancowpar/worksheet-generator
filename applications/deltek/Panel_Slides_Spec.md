# Panel Slides — visual spec + outline

The deck is part of the design-chops signal Rabideau and Cipollone
will read. Engineering isn't on this panel, so we're not in
shipped-artifacts-over-decks territory. Build slides that demonstrate
the same restraint and considered choice as the portfolio page.

## Visual language (locked, no negotiation)

Same brand tokens as the portfolio page so the deck reads as part of
the same body of work, not as a one-off:

| Token | Hex | Use |
|---|---|---|
| Charcoal | `#0B1220` | Primary text, titles |
| Charcoal-mid | `#3A4258` | Secondary text, body |
| Charcoal-soft | `#6B7280` | Metadata, labels |
| Glacier | `#7CC0B8` | Brand accents, section labels |
| Glacier-deep | `#5BA89E` | Hover, deeper accent |
| Amber | `#F59E0B` | Wins only — metric underlines |
| White | `#FFFFFF` | Background |
| Surface-soft | `#F7F7F5` | Alternating-section wash |
| Border | `#E5E5E2` | Hairlines (1px) |

Typography:
- **DM Sans** for everything display and body.
- **JetBrains Mono** for metadata (section labels, dates, slide
  numbers, mono accents on numbers).
- Display headlines: 72–96pt, tracking-tight, charcoal.
- Section labels: 14pt mono uppercase, tracking-wide, glacier-deep.
- Body: 24–32pt charcoal-mid for the rare slide that has body text.

Composition rules:
- **One idea per slide.** Never two.
- **No bullet lists.** Use sentences, single phrases, or diagrams.
- **No stock photos.** No decorative illustrations.
- **No shadows.** 1px borders only.
- **Generous whitespace.** If a slide feels crowded, kill content.
- **The metric is a typographic moment**, not a chart annotation. The
  $50M, the 97%, the 20 PMs — each gets its own slide as a
  display-scale typographic reveal.
- **Diagrams are line art**, charcoal stroke, glacier accent, no fill.

## Deck structure — 12 slides total

Two case studies × 5 slides each + 2 bookend slides. Fewer slides
than a typical deck on purpose. Confidence reads as restraint.

| # | Slide | Time | Notes |
|---|---|---|---|
| 1 | Title card | <30 sec | Name + role tagline. Sets the brand language. |
| 2 | The frame (Starbucks cold open) | 45 sec | Optional visual anchor for the cold open. Could be just the killer quote as a typographic slide. |
| **3** | **Case 1 — title card** | <15 sec | "Case 1: The AI Capability Layer" |
| 4 | The mechanism (Case 1 structure) | 3.5 min | Diagram of peer community + shared infrastructure + on-ramp ritual. |
| 5 | The adoption arc (Case 1) | 3.5 min | Visual of how 1 PM became 3 became 20. |
| 6 | The outcomes (Case 1) | 3 min | Typographic reveals: "20 PMs" / "workflows retired" / specific names if you want. |
| 7 | The principle (Case 1) | 1 min | One sentence on the slide: *"Adoption measured by what stopped, not what launched."* |
| **8** | **Case 2 — title card** | <15 sec | "Case 2: The UTA Operating System" |
| 9 | The mechanism (Case 2 structure) | 3.5 min | Diagram of the three components: composite risk model + five-panel analytics + weekly cadence. |
| 10 | The signal routing (Case 2) | 3.5 min | Diagram of the five panels + the Claude Code routing function as the centerpiece. |
| 11 | The outcomes (Case 2) | 3 min | Typographic reveals: "$50M" / "97%" / "$250M ARR / 300 customers." |
| 12 | The principle (Case 2) → close | 1 min | One sentence: *"The system's value was measured by whether decisions changed."* Then Q&A. |

## The two centerpiece visuals

Two slides will carry the most weight. Get these right and the rest
follows.

### Slide 4 — Case 1 mechanism diagram

The mechanism is **peer community + shared infrastructure + on-ramp
ritual.** Concept sketch:

```
         shared infrastructure
              (slash commands)
                    │
                    │
   peer community ─ ┼ ─ on-ramp ritual
   (20 PMs)              (15-min build)
```

Visually: three nodes connected by glacier hairlines. Each node is a
short label in charcoal. No icons. The whitespace and the line art do
the work. Optional: a small annotation that the seed at the center was
the personal Claude Code productivity OS.

### Slide 10 — Case 2 signal-routing diagram

The most distinctive technical visual in the deck. The five panels
feeding the Claude Code routing function which outputs a single ranked
action. Concept:

```
  customer escalations ──┐
  code defects ──────────┤
  internal bugs ─────────┼──→  [routing function]  ──→  the one
  CVEs ──────────────────┤                              action
  noise ─────────────────┘                              this week
```

Visually: five short labels on the left flowing into a central
labeled element (the routing function as a charcoal box with a glacier
border), then a single arrow out to the right with a typographic
emphasis on *"the one action this week."*

This slide does double work — it shows that you actually shipped AI
inside a product (Kapoor and Tushaus both care about that), and it's
the most architecturally distinctive moment in the deck (Cipollone
will read it as a real story to retell).

## The typographic-moment slides

For slides 6 and 11 (outcomes), the move is restraint. The metric IS
the slide. Examples:

**Slide 6 — Case 1 outcomes:**

```
        20 PMs
        Twenty custom slash-command libraries.
        Workflows retired, not workflows launched.
```

The "20 PMs" is set at display scale (~120pt), the rest is small
caption-style mono text underneath. The slide is mostly whitespace.

**Slide 11 — Case 2 outcomes:**

```
        ~$50M
        in at-risk ARR surfaced before escalation.
        Working defect list cut ~97%.
        $250M ARR · 300 customers · one weekly decision.
```

Same pattern. The number is a typographic event. The supporting text
is mono caption underneath.

## What this deck deliberately doesn't have

- No agenda slide. Lisa already told them the agenda. Recapping it is
  filler.
- No "About Ian" slide. They have the resume. They have the dossier
  from Rabideau. Telling them again is filler.
- No "Thank you / Questions?" slide at the end. The principle slide
  closes Case 2 and you transition to Q&A verbally. The "Questions?"
  slide is the design equivalent of clearing your throat.
- No company logos. No customer logos. No brand-name dropping in the
  visuals. The talk is about the work.
- No animated transitions beyond simple cross-fades if anything at
  all. Animation costs credibility in this room.

## Build path — pick one

Two options for actually producing the deck:

**Option A: I build the slides as HTML/CSS** (using the same brand
tokens and component language as the portfolio page). Pros: pixel
control, brand-continuous, can present from browser via Teams share.
Cons: no native presentation animations (which we don't want anyway),
one more thing to set up for the actual call. You'd preview locally
the same way you preview the portfolio page.

**Option B: I write a tight slide-by-slide spec** and you build in
Keynote or Figma. Pros: native presentation tool, you own the file,
easier to last-minute edit. Cons: brand fidelity depends on you
implementing the spec carefully; takes you several hours of build
time you could spend rehearsing.

My recommendation: **Option A.** Three reasons —
(1) the portfolio page already proves the design language works in
HTML; reusing the same system for the deck means perfect fidelity
with minimal new work; (2) browser-based slides via Teams screen
share are well-tested and don't drop frames; (3) it frees your build
time to focus on the narrative rehearsal, which is the higher-value
work between now and June 3.

If you want Option B, say so and I'll write the slide-by-slide spec
for Keynote.

## Open from earlier (still need)

To deepen the case-study narrative inside the slides (especially the
adoption arc and outcomes slides), I still need the specifics flagged
in `Panel_Case_Studies_Scaffolding.md`:

- The catalyst moment for Case 1
- 2–3 named champion PMs and what each retired
- Whether to claim hours-saved numbers or hold to extinction-over-addition
- Whether to name the UTA program lead or use the role label
- Confirm five-panel categories and what's sayable about model weights
