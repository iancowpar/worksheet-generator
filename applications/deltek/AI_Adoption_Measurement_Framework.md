# Measuring AI Adoption — Beyond Token Usage

The honest taxonomy, ordered by signal strength. Most orgs stop at Tier 1-2 because that's what tools instrument by default. The real measurement work happens at Tiers 3-6 — and it's almost entirely instrumented by hand or by program design, not by vendor dashboards.

---

## Tier 1: Usage metrics (what most orgs measure today — and shouldn't stop at)

- Token / API call volume
- Active seats, DAU/WAU/MAU
- Logins, sessions per user
- Time spent in tool

**What this tells you:** People are touching the tool.
**What this does NOT tell you:** Whether the tool is changing how they work.

A user can have 50,000 tokens in a month and have integrated the tool into zero of their workflows — they could be experimenting, playing, or running it once and forgetting. Token usage scales with curiosity *and* with adoption; you can't tell which one is driving it.

---

## Tier 2: Engagement metrics (slightly better)

- Frequency per user (daily, weekly)
- Cohort retention curves (Day 7, Day 30, Day 90)
- Variety of use cases per user
- Multi-tool integration (do they use Claude Code AND Cursor AND ChatGPT, suggesting workflow integration not novelty)

**Better — retention curves especially.** A cohort handed Claude Code in March, plotted at Day 30 / Day 60 / Day 90, tells you whether the initial spike collapsed or held. Healthy adoption looks like cohort curves that flatten high. Failed adoption looks like curves that continue dropping.

**Still insufficient:** High engagement could be high curiosity. People who play with new tools daily without integrating them look identical in usage data to people who've truly integrated.

---

## Tier 3: Output and quality metrics (harder, more meaningful)

- Quality of AI-augmented output vs. baseline (requires rubrics)
- Time-to-completion for specific tasks before/after
- Defect rates / rework rates on AI-augmented work
- Customer satisfaction or downstream business metrics on AI-touched work

These start measuring whether the tool is making the work *better*, not just present. Hard to measure cleanly because you need controlled comparisons, and most orgs don't have the discipline to capture pre-AI baselines before they roll out.

**Move worth making:** when launching an AI tool, capture a 4-week baseline of the same metrics on the same population BEFORE giving them the tool. Most orgs skip this and then can't measure what changed.

---

## Tier 4: Workflow integration metrics (the real game starts here)

This is where adoption stops being a usage question and becomes a workflow question.

- **Number of workflows where AI is now standard, not optional.** If a workflow is documented as "step 3: prompt the AI for X," it's integrated. If it's "you can use AI here if you want," it isn't.
- **Process steps eliminated.** When AI takes over one step, downstream steps often disappear too. Count the steps that vanished.
- **Handoffs reduced.** If AI handles a step that used to require a handoff to another team, the handoff frequency drops. That's a measurable, structural shift.
- **Time-to-meaningful-contribution for new hires.** Deltek's JD asks for this directly. New hires with AI tooling vs. new hires without — how fast do they hit baseline productivity? Reductions here are pure structural adoption signal.
- **% of decisions or artifacts AI-augmented as standard practice.** Specs written with AI assistance. Decisions documented with AI synthesis. Reports generated with AI. Track the percentage over time.

---

## Tier 5: Behavior change and habit formation (the hardest tier — and the most truthful)

This is where the Deltek role is being built. The JD explicitly asks for *"a clear ability to distinguish genuine behavior change from participation without follow-through."* These are the metrics that distinguish them.

### The "extinction over addition" frame (most important)

**True adoption is not "person now uses AI." It's "person STOPPED doing the manual version."**

If someone uses Claude Code daily but *also still writes specs the old way*, you don't have adoption — you have parallel workflows, which is the most expensive failure mode of all. Real adoption shows up as something STOPPING. Measure:

- Tickets that previously required human triage but no longer do
- Manual reports that have been deleted from the operating cadence
- Meetings cancelled because the AI now produces what the meeting used to produce
- Time spent on the legacy version of a workflow per user, plotted over time

If the legacy version isn't decaying, the new version isn't winning.

### The fallback principle (the mechanism behind extinction)

**Adoption is slow when the fallback exists.**

This is the mechanism that explains why parallel workflows are the most expensive failure mode. When two systems run in parallel, people don't split evenly between them — they revert to the familiar one under any kind of stress. Comfort wins under load. The presence of a fallback is itself the drag on adoption, regardless of how good the new tool is or how loudly leadership pushes it.

**Real-world proof point:** at UKG post-Ulti/Kronos merger, the org migrated from Slack to Teams. Slack later made a "heralded return" — Ulti veterans were genuinely happy. Engineering leadership pushed adoption. But Teams remained for non-P&T comms, so even willing users ended up running both (Slack for engineering, Teams for everyone else). When even *willing* users get pulled into parallel workflows, you've identified the structural problem: the fallback isn't a backup plan, it's the gravitational pull that prevents adoption from sticking.

**The diagnostic question to ask of any adoption program:**

*"What is the user's fallback if they don't use the new tool? Is that fallback still sanctioned, available, and free of friction?"*

If the answer is *yes* to all three, your adoption program is fighting gravity. You can run champion networks, training programs, and recognition systems indefinitely without moving the needle.

### The corollary: deliberate sunset

**The highest-leverage move an enablement function can make isn't more training, more champions, or better internal marketing — it's removing the fallback.**

Every successful AI adoption push is paired with a deliberate sunset plan for the displaced workflow:

- Hard-deprecate the legacy tool with a date
- Remove the manual report from the cadence (don't make it "optional," remove it)
- Stop maintaining the old training materials
- Remove access to the fallback for new hires entirely
- Tie performance reviews to using the new workflow, not just to outcomes

This is politically harder than running adoption programs, which is why most enablement functions default to programs. But programs without sunset plans produce parallel workflows, which produce the metric you don't want to see: high usage of *both* systems, declining usage of *neither*.

**For a measurement framework:** track the "fallback availability ratio" — for each major AI workflow being adopted, is the legacy workflow still (a) sanctioned, (b) available, (c) frictionless to use? Three yeses means adoption will plateau. Adoption that holds requires at least one of those three to flip to no.

### The "voluntary effort" frame

When people pay for something with their own time, they've adopted. Voluntary creation is costly — nobody builds a custom slash command for a tool they don't trust. Track:

- Custom prompts written and saved per user
- Slash commands / agents built per user
- Prompt templates shared in Slack/Teams without prompting
- Documentation pages created by users (not by L&D) about their AI workflows

This is what your Jira-hygiene slash command was — and the PM who told you "this is magic" gave you the strongest possible adoption signal: she didn't just use it, she shared it.

### The "champion network velocity" frame

Adoption that holds is adoption that propagates without official sponsorship.

- **Net referral rate:** how many people learned about the tool from someone OTHER than L&D, the AI team, or the official rollout?
- **Velocity of peer-to-peer spread:** if 5 people on a team adopt, how many days until the 6th, 7th, 8th adopt without anyone in leadership pushing?
- **Champion conversion rate:** of the people you formally enlisted as champions, how many actually drove adoption in their teams vs. wore the title without effect?

The PM automation library at UKG that scaled "without a top-down mandate" is exactly this metric in narrative form.

### The "advocacy" frame

- Do users defend the new way when challenged?
- Do they teach others unprompted?
- Do they report missing the tool when it's unavailable?

These are qualitative but real. Run a quarterly "what would you stop doing if this tool went away tomorrow" survey. The answers tell you what's structurally integrated vs. what's still optional.

---

## Tier 6: Outcome metrics (the ROI conversation)

The metrics leadership ultimately wants — but they're lagging indicators, so they tell you adoption worked AFTER it's too late to course-correct.

- Business outcome change attributable to AI workflow shifts (with controls)
- Cost reduction from AI-augmented work
- Quality improvements (defect rates, customer satisfaction)
- Speed improvements (time-to-market, cycle time)
- Talent leverage (revenue per employee, output per FTE)

The Deltek 2026 Clarity A&E Study found 90% of A&E firms are using or planning to use AI but **45% can't measure ROI**. That gap is the entire reason a real measurement framework matters — without Tier 4-5 metrics in place, you can't connect Tier 6 outcomes back to AI specifically.

---

## The framework for actually measuring it

**Leading indicators (Tier 4-5)** tell you adoption WILL work in 6 months. Examples: peer-referral rate, voluntary creation rate, behavior extinction rate.

**Lagging indicators (Tier 6)** tell you adoption DID work. Examples: cycle time, cost saved, quality improved.

**Most orgs only measure lagging** and then discover, too late, that adoption never took root and the lagging metrics moved for unrelated reasons.

The role of an enablement function is to instrument the leading indicators FIRST — so you can iterate the program before the lagging metrics make or break it.

---

## The middle-out frame for measurement

Top-down measurement: rolled-up dashboards for the CPTO. Looks like adoption. Often theater.

Bottom-up measurement: individual usage metrics. Looks like activity. Often noise.

**Middle-out measurement:** instrument at the team level — the layer where workflows actually live. Measure:
- Per-team behavior extinction (what manual processes did this team stop doing?)
- Per-team voluntary creation (how many custom workflows did this team build?)
- Per-team peer spread (when one person on the team adopted, how fast did the others?)
- Per-team workflow integration (what % of the team's standard processes now include AI as a non-optional step?)

The team is the unit of analysis where adoption either holds or fails. Individuals are too noisy. Orgs are too aggregated. The middle is where the signal lives.

---

## How to use this with Lisa Martin today (if it comes up)

Don't dump the framework. If she asks something like *"what does good measurement look like to you,"* land one or two of these:

> *"The shortest version: most orgs measure usage, but usage is the same shape whether someone's curious or genuinely integrated. The metrics that actually distinguish adoption from theater are extinction over addition — did the person stop doing the manual version — and voluntary creation rate, how often users are building their own prompts and workflows because they trust the tool enough to invest. Token usage is the floor; behavior extinction is the ceiling. The Clarity study's 45% who can't measure ROI is what happens when you skip the middle layer."*

That's ~75 seconds of substantive perspective. It signals:
- You've thought about this rigorously
- You have a position, not a textbook recap
- You can connect external customer data (Clarity study) to internal program design
- You speak in operations language, not aesthetics

---

## Substack potential

This is genuinely a Substack piece. *The Unofficial Leader* readers — product and engineering leaders trying to figure out what AI adoption actually looks like — would eat this. Working title:

**"Why your AI adoption metrics are lying to you"** — opens with the token-usage trap, walks through the tiers, lands on the middle-out measurement frame and the extinction-over-addition principle. ~1,000 words. Could be the follow-up to your slash-command piece.

Worth drafting after the Deltek conversations settle out — and timed for when you're either in the Deltek pipeline (so the writing reinforces the conversation) or out of it (so you don't tip your strategy).
