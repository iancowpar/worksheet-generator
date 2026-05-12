# Suffolk HM Screen — Live Notes (Blake Abbenante, 3pm)

**Glance reference. Don't read full sentences — find the bullet you need.**

---

## Q1 — Walk me through your background

- Greeting + warm thanks
- "Two years at UKG as a senior PM **protecting 300 enterprise customers representing $250M ARR** through migration off legacy workforce management"
- "**Three things that map directly to what you're building**" — pick three:
  - **0→1 self-serve migration tool** — wrote the working prototype myself in Claude Code, designed UX with services consultants, handed engineering the full delivery package (bepics, epics, stories, Gantt, roadmap). In production now; Services runs it without an engineering ticket.
  - **Five-panel operational analytics product** — auto-refreshed daily, surfacing a single highest-leverage action per view across four products
  - **Sprint health instrumentation** — 15-min refresh, documented rejection criteria for burndown, velocity, story-point anti-patterns
  - **AI capability layer** — first organized AI adoption effort, scaled without a top-down mandate
- "Before UKG, **ten years at Broadridge — 40+ enterprise deployments in compliance-grade financial services**"
- "Part of an **April reduction in force at UKG**"
- Close: "What pulled me to this role is your LinkedIn post — **you're not hiring someone to ship features, you're hiring someone to build a product function. That's the work I've been doing without the title. I want to do it with one.**"

---

## Q2 — Why this role / Why Suffolk

- "The tech bet here is **real and structural, not marketing**"
- **Suffolk Technologies** — VC arm, dogfooding portfolio companies on Suffolk job sites, 12-18 month read on where construction tech is going. Information advantage competitors don't have.
- **Seamless Platform** — connective tissue across pre-construction, active construction, operations. Insights from one phase inform decisions in the next.
- "The Lead PM role sits exactly where that platform **needs a product function around it**"
- Bridge: "That's the framing from your LinkedIn post that pulled me in"
- Connect: "That's the work I've spent the **last two years** doing at UKG without the title — building data products with opinion, scaling product practice across a team without authority, sitting at the seam between operational data and the decision the operator needs to make"
- Land: "**The domain is new. The work shape is the work I want to be doing.**"

**Don't say:** "I've always been interested in construction."

---

## Q3 — Walk me through the five-panel system

- **Problem:** Support could only file tickets as defects (no other ticket type). Severity was support-assigned. So engineering was staring at a couple hundred items across four products that all *looked* like real bugs but weren't.
- **Built a five-panel data product, auto-refreshed daily across four products. The panels:**
  1. **Customer escalations** (real customer impact)
  2. **Code defects** (engineering-validated bugs)
  3. **Internal bugs** (caught by us, not customers)
  4. **CVEs** (security)
  5. **Noise** (won't-fix bucket) — the panel most teams don't have, prevents re-evaluating non-actionable items every triage cycle
- **Opinion baked in: a Claude Code function inside the tool that identifies the highest-leverage move per panel.**
  - Example: *"one security fix here clears 15 Jira issues — that's your highest-leverage move today"*
  - Not a list to triage. One decision to make.
- **Why these five panels (if probed):** action-owner, not severity. Escalations route to Services/CSMs. CVEs route to Security. Code defects + internal bugs to engineering leads. Noise gets acknowledged.
- **Impact:** Engineering stopped staring at noise. Triage cycle compressed. ~200 apparent defects → ~5 real ones at any given time. **Product is still in use.**

---

## Q4 — People management probe

- Open clean: "**Honest answer: I haven't formally managed direct reports in my product career.**" (Don't say "25 years.")
- "Closest thing: **peer groups I led around the AI capability layer at UKG**"
- "I designed the layer **as shared infrastructure from the start, not personal tooling** — so adoption could spread organically"
- "**Other PMs adopted it without a top-down mandate**, and I ran peer groups around it to make sure the practice stuck"
- "That's coaching work in everything but title"
- "**What I want from this role is the player-coach mix** — mentoring the two PMs while staying accountable to portfolio direction myself"
- **First 60 days:**
  - Get to know the two PMs — where they are in their craft
  - Understand where their days actually break down
  - Understand what they need from a manager vs. from a peer
  - Then do the same coaching I've been doing informally, with the authority and accountability that come with the title
- "**That's the next step I want, not a step away from the work**"

---

## Q5 — Technical depth probe (Databricks / dbt / semantic layers)

- Open clean: "**Honest answer: I don't have deep hands-on with Databricks or dbt.**" (No "Oh.")
- "The modeling layer — which transforms, which semantic-layer patterns, which warehouse architecture — is **depth the data engineering team owns**"
- "What I'd bring as a Lead PM is **judgment about what to build on top of that and how to instrument value from it**"
- **What I do have:**
  - **SQL-fluent** — used it daily at UKG for self-serve analysis
  - Comfortable in technical conversations about API design, data models, architectural tradeoffs — can reason with data engineers without writing production code
  - **Real AI fluency** — agentic workflows, prompt strategies, building Claude Code functions directly into operational tools
- **The ramp:** "I'd ramp on Databricks and dbt patterns fast — SQL foundation and modern-data-stack mental model are already there. **The judgment piece — what to build, how to instrument value, what makes a data product worth shipping — is the part that doesn't develop fast, and that's where I'd add value from day one.**"

---

## UKG departure (if probed)

> "Reduction in force in April. The UKG Pro Services line was restructured; a number of PM roles were eliminated, mine included. Timing was unfortunate but the situation is clear-cut."

**Don't elaborate. Don't editorialize. Move on.**

---

## Other gaps to pre-empt if Blake probes

- **Construction domain — none.** "Plus, not required (per JD). I'd plan to spend the first 30 days close to the field — operations, safety, planning leaders — before pushing on the roadmap."
- **Two-year PM title runway.** Don't apologize. Broadridge BA decade was product-adjacent work; UKG title is the formalization.

---

## Questions for Blake (pick 3 when he asks)

1. *"How big is the PM team I'd be inheriting? What's their current maturity — coming from product backgrounds, or growing into product from analytics or operations?"*
2. *"Of operations, planning, safety, and finance — which is the most underbuilt right now? Where do you want me to spend the first quarter?"*
3. *"What's the most painful thing the PM team is working through right now that you'd want me to address in the first 60 days?"*
4. *"What does the relationship between Data Product and Suffolk Technologies look like — where do they intersect, where are they intentionally separate?"* (Homework signaler — only if there's room)

---

## Watch-fors

- Pre-empt the people-management question early — don't let it fester
- Don't apologize for the two-year PM title runway
- Keep "**data products**" as the through-line
- Blake will zero in on the AI capability work — *"spread without a top-down mandate"* framing ready
- After the meeting: send the Substack piece on Jira hygiene as follow-up morning-after touchpoint

---

**You've done the work. Trust the structure. Go.**
