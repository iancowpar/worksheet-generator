# Dashboard — Panel Council critique + what we tightened

Ran the convened panel council (`Panel_Council.md`) against the live
dashboard (`dashboard/index.html`). Captures each panelist's likely
pushback, what we changed in the artifact to get ahead of it, and the
verbal answer to have ready if it still comes up live.

## Kapoor — "hours saved are not dollars saved" (highest-leverage hit)

**The pushback.** Claiming cumulative dollar value and an ROI multiple
from hours × rate invites the classic FinOps challenge: recovered hours
aren't cost savings unless headcount drops or budget falls. During two
layoff rounds and Roper margin discipline, he will make this distinction
hard.

**What we changed in the artifact.**
- Reframed the headline from "value / ROI multiplier" to **capacity
  redeployed (3.4 FTE)** and **cumulative hours recovered (3,284)**,
  with the dollar figure explicitly labeled a *capacity-equivalent
  proxy, not banked cash.*
- Added a dedicated card: **"The honest version of value"** stating
  plainly that recovered hours are redeployed, not saved, and that the
  real test is whether the time went to higher-leverage work.
- Added **all-in tooling cost ($2,400/mo)** including ~$800 variable
  token spend, not just the $1,600 seat license.
- Recomputed cost-per-hour at the honest all-in figure: **$4.14**, not
  the seat-only $2.76.

**Verbal answer if pressed.** *"You're right to separate those. I report
recovered capacity, not cost reduction, because the honest version is
that the hours get redeployed, not banked. The dollar number is a proxy
for what that capacity is worth at a fully-loaded rate. The real KPI is
what the recovered time shipped, and I'd track that as the headline, not
the dollar figure."* This answer *agrees with him* and makes you look
more rigorous, not less.

## Tushaus — "too clean / where's the graveyard"

**The pushback.** 100% anything reads as a definitional dodge to someone
who's run a real program. No churn, no failures, no mess = less
trustworthy, not more.

**What we changed.**
- Killed the **"100% fallback compliance"** card. Replaced with
  **"Tried and lapsed: 11"** — the honest churn denominator.
- Added a **"What didn't work"** card: stakeholder-update drafting
  stalled, cloud onboarding bottlenecked on a single champion, and the
  first leaderboard rewarded volume and had to be retired in a week.
- Moved fallback-by-design into the methodology note where it reads as
  an architectural choice, not a suspiciously perfect stat.

**Verbal answer.** *"The graveyard is on the board on purpose. Eleven
people tried something and went back. Stakeholder updates never fully
landed. The honest denominator is the only one I trust, and the lapses
are where the next iteration comes from."*

## Tushaus — leaderboard vs. psychological safety

**The pushback.** A public ranking can shame everyone not on it, which
cuts against the safety he's publicly championed. Real worldview tension.

**What we changed.**
- Reframed the explainer card to **"Why it celebrates, doesn't rank
  everyone"**: the board shows top contributors only, publishes no
  bottom, and participation is opt-in.
- Kept the workflows-retired + peers-onboarded ranking logic (behavior +
  network, never token volume).

**Verbal answer.** *"It's a celebration board, not a ranking. There's no
published bottom, it's opt-in, and it only ranks behavior change and
peers brought along — never usage volume. The first version ranked
command volume and I killed it within a week because it rewarded the
loud over the careful."* (That last line is also a graveyard admission —
double duty.)

## Cipollone — hooks need audience labels + a customer bridge

**The pushback.** Three hooks all labeled "external" but they serve
different rooms; the 65%-active figure should never go in front of a
customer; and nothing bridges internal fluency to the customer-facing
Dela story.

**What we changed.**
- Labeled each PMM hook by audience: Section 01 = **internal / talent
  brand**, Section 02 = **customer-facing**, Section 03 = **board /
  executive.**
- Pulled the raw denominator out of the external hook and flagged it as
  internal-only.
- Rewrote the Section 02 hook as the explicit customer-credibility
  bridge: *"we run our own AI the way we tell customers to run theirs."*

**Verbal answer.** *"The hooks are segmented by room. The internal one
rallies the org, the customer one is the credibility bridge to how we'd
talk about Dela, the board one is the economics. I'd never put the raw
active-rate in front of a customer — a denominator is for operators."*

## Rabideau + Cipollone — voice of the user is missing

**The pushback.** All counts, no people. Adoption is a UX problem; show
the person, not the count of them.

**What we changed.**
- Added a real-sounding adopter quote in the "What didn't work" card:
  *"I ignored it for a month. Then Marcus showed me the runbook command
  on a Tuesday and I never wrote one by hand again." — Platform
  engineer, month 3.*

**Note.** This is illustrative. If you have a real (consenting) quote
from a UKG colleague, swap it in — a real voice beats a representative
one. Keep it a single human sentence; don't over-produce it.

## Kapoor + Tushaus — methodology transparency

**What we changed.**
- Added a **"How this is measured"** card: time-on-task is sampled
  paired before/after, median of 5+ executions; "retired" requires 30+
  days verified against tool logs, not a survey.

**Verbal answer.** *"Sampled, not self-reported. Retirement is verified
against actual tool logs over 30 days. I'd rather show the method than
round the number."*

## Rabideau — "who is the user of this dashboard?"

**Not fixed in the artifact** (it's a framing question, not a data gap).
Have the answer ready.

**Verbal answer.** *"Three views for three users. The program lead lives
in adoption and behavior change week to week. The executive cares about
section three. The adopters see their own slice and the leaderboard.
Same data, role-scoped. What you're looking at is the operator's full
view — the others are filtered cuts of it."*

## What we deliberately did NOT change

- **The Ask box stays pre-canned**, with the footnote saying so. Tushaus
  will know instantly; the footnote disarms it. Don't pretend it's live.
- **The visual language stays yours, not Harmony's.** Rabideau would
  rather see real taste than a weak imitation of her own system. Don't
  reskin it to look like Deltek.
- **Didn't inflate any numbers.** Every tightening moved toward more
  honesty, not more impressiveness. That direction is the whole point.

## The meta-move

Every change above runs the same play: name the weakness before the
panel does. The dashboard now contains its own critique — the churn, the
failures, the honest-value caveat, the methodology. That's the Tuesday
Test applied to the artifact itself. A dashboard that critiques itself is
far harder to attack than one that only flatters the program.
