# Case 2 narrative — UTA Upgrade Program at UKG

Spoken version. Built for ~13-15 minutes at conversational pace
(130-150 wpm). Sections marked with beat headers for your reference
while rehearsing; do not read the headers out loud.

Same voice constraint as Case 1: contractions, no em dashes, no
machine-gun rhythm, no theatrical hooks, no fabricated moments.

---

## Opening hook (~1.5 min)

The second case is a different shape from the first. Case 1 was
behavior change at the level of individual PMs. Case 2 is operating
mechanism at the level of a multi-year program.

The program is the UTA Upgrade Program at UKG. UTA stands for UKG Pro
Time and Attendance. It's software we license from Infor, and a
couple of years ago Infor announced end-of-support for the version
we were running our customers on. The underlying tech stack, Java and
SQL Server, was going to lose support, which meant we had to upgrade
everyone. Or we had three hundred customers carrying ARR of about
two hundred and fifty million dollars sitting on infrastructure with
a cliff edge in front of it.

So the program got built. Planning started in winter of twenty
twenty-four, customer upgrades started in October of twenty
twenty-five, and the delivery date was end of twenty twenty-six.
Three hundred customers in roughly fourteen months, against a
back-end change that touched almost nothing the customer saw on the
surface but touched a lot underneath.

Lisa, our program manager, ran the projects. I owned it from the
product side. I ran the prioritization analysis, I sat in the
product seat on the high-risk customer calls with our account
managers and our sales partners, I negotiated with engineering on
the approach, and I built the operating mechanism that the program
ran on.

That operating mechanism is the meat of this case.

---

## Structure — the dashboard and the data underneath it (~3.5 min)

The mechanism was a triage dashboard, but the dashboard wasn't the
interesting part. The interesting part was the data infrastructure
underneath it.

The dashboard took inputs from four sources. Sentiment from the CSM
leads and from Salesforce account notes. Defect counts from Jira.
Case volume from Salesforce. ARR exposure from Salesforce, with a
Power BI layer on top to do the financial weighting. Four systems,
four data shapes, one combined view.

The interesting work, though, was deciding what counted as a defect.
When you're upgrading three hundred customers on a back-end tech
stack change, support gets noisy. A customer reports an issue, the
case lands in Salesforce, the support engineer escalates to product.
But a lot of the issues that landed weren't actually about the
upgrade. Some of them were customer configuration problems that
existed before the upgrade. Some of them were pre-existing bugs the
customer hadn't noticed until the upgrade gave them a reason to
look. If we treated all of those as upgrade defects, the data would
have told us we were on fire when we weren't. And worse, it would
have pulled engineering's attention onto noise instead of onto the
things that actually needed code fixes.

So I worked with Leila, our engineering manager, to design a Jira
labeling system that bucketed the work cleanly. Customer
configuration issues got one label. Pre-existing issues got another.
And only the issues that required an actual code fix and a
deployment got tagged as upgrade defects. That meant the defect
count in the dashboard was a real count of real defects, not a
count of noise.

Co-designing that taxonomy with Leila was the single most important
structural decision in the case. Because if I'd just consumed Jira
data without thinking about what was in it, the dashboard would have
looked productive but would have been lying. Engineering and I had
to share the vocabulary before either of us could trust the signal.

From those four inputs and that clean defect classification, the
dashboard produced a weighted top-five list of at-risk customers.
The weights were ARR-dominant and true-defect-dominant. Sentiment
and case volume mattered but they were secondary. The reason for
that weighting was straightforward. A small customer with a few
cases is a small customer with a few cases. A large-ARR customer
with three confirmed defects in the upgrade pipeline is a different
kind of problem, and the dashboard had to reflect that.

The cadence on the dashboard was two-tier. We reviewed it daily in
standup, which was operational rhythm, and we reviewed it weekly in
the cross-functional upgrade program call, which was where Lisa,
engineering, support, and the customer-facing functions came
together. Two altitudes of visibility. Same artifact.

---

## The engineering negotiation (~2 min)

I want to spend a beat on one specific moment in the program where
the operating mechanism mattered most, which is the negotiation with
engineering on how to sequence the upgrades.

Engineering wanted to sequence them by database pod. Pods were the
natural unit of their operational planning. If you upgrade a pod at
a time, you batch the work, you minimize coordination cost, you can
predict your sprint capacity. From an engineering operations
standpoint it was the clean answer.

Product's argument, my argument, was that pod-based scheduling would
shatter the first time a customer asked us to hold off. And
customers were going to ask. They were going to ask because of
internal projects, because of their own change windows, because of
regulatory cycles, because of mergers and acquisitions, because of
all the normal reasons a complex enterprise customer asks for a
delay. If a pod's schedule depends on every customer in that pod
being available in the same window, one ask breaks the whole pod.
And then the cadence breaks. And then we lose the delivery date.

The alternative was to sequence by complexity. Upgrade simpler
customers first, build the muscle and the playbook on the easier
accounts, then move to the harder ones with the lessons in hand. And
because the sequencing was by complexity rather than by pod, a
customer delay was a local event. You move them later in the queue.
The cadence holds.

Engineering's preference was operationally efficient. Product's
preference was operationally resilient. We landed on complexity
because the delivery date was the load-bearing constraint, and only
one of those two approaches survived contact with the customer
reality we were going to hit.

That conversation wasn't easy. But it wasn't acrimonious either.
Leila and her team understood why pod-based scheduling would have
failed, and we found the version of complexity-based that respected
as much of their operational planning as we could.

---

## Adoption and stakeholders (~3 min)

Adoption on Case 2 was different from Case 1. On Case 1, adoption
was a peer-spread story. On Case 2, adoption was institutional. The
dashboard became the artifact that anchored the program's cadence.
Daily standup ran on it. Weekly cross-functional call ran on it.
Engineering used the Jira labels to allocate capacity. Lisa used the
top-five list to focus her own attention.

The stakeholders I worked with most closely were:

Lisa, the program manager. She ran the projects. I ran the
analytical center. Our working pattern was that I'd produce the
weekly view, walk her through what had changed, and she'd take that
into her project conversations with the delivery teams. Without that
working relationship, the dashboard would have been a report nobody
read.

Leila, the engineering manager. The Jira-label conversation kept
going. Every couple of weeks she'd come to me with a case that
didn't fit cleanly into one of the existing buckets, and we'd refine
the taxonomy together. The taxonomy was a living document, not a
static one.

The account managers and sales partners. They consumed the top-five
list when their customer showed up on it. The dashboard never became
a political object, which I was honestly relieved about. AMs didn't
push to get their customer prioritized off-list, and they didn't
argue with the ranking when their customer was on it. The reason
for that, I think, was that the data structure was clean enough that
the list was defensible. If somebody had wanted to challenge the
math, the math would have stood up.

The high-risk customer calls. This is the most human part of the
program. Sitting in the product seat on those calls didn't look like
product demos or feature pitches. It looked like walking pre-upgrade
customers through what the process would actually do, calming their
fears, and addressing concerns they brought up about prior upgrade
experiences they'd had with UKG. Some of those prior experiences had
not gone well. The customers were honest about that. And my job on
those calls was, in part, repair work. Acknowledging that the
company had not always gotten this right, telling them specifically
how this program was different, and earning the right to ask them
to trust us through the upgrade.

---

## The university story (~1.5 min)

There's one customer that captures the full shape of Case 2. I'm
not going to name them. They're a large university. They were red
sentiment going in. They had multiple existing contract issues with
us. They had scars from previous implementations. They had
high-risk payroll concerns. And they had a custom time-off request
approval process that was particularly fragile in the context of
this upgrade.

Five flags lit at once. Compound-risk profile. The kind of customer
where if anything went wrong, it was going to go wrong publicly.

We did several things for them that we didn't do for the average
customer. We built a custom validation process for their specific
upgrade requirements, walking through everything they cared about
ahead of the cutover. And we offered them dedicated engineering
support for their custom Cognos reports. Normally customers are
responsible for their own custom reports. For this account, we made
an exception. Not because they asked for it. Because the risk
profile warranted it, and offering it was the move that bought
their trust.

They got through the upgrade. The upgrade itself happened after I
was let go. I followed up with the CSM on the account after I'd
left UKG to confirm it went well. She told me it did.

---

## Measurement (~2 min)

The measurement story on Case 2 is shaped by the fact that the
program is still in flight. I can tell you what I saw through
April fifteenth.

At the time of the RIF, we'd upgraded about forty percent of the
three hundred customers. That's roughly a hundred and twenty
accounts in six months of customer-facing execution. Velocity was
increasing, not decreasing. The program was ahead of schedule for
the November twenty twenty-six delivery date.

The Jira-label classification was directing engineering capacity.
Engineering allocated their sprint capacity against the true-defect
list, not against the raw case volume. That's the operational
outcome of the data infrastructure work. It moved engineering from
reactive triage on noise to proactive work on real defects.

I want to be honest about one thing the dashboard did not do. The
dashboard did not change Lisa's prioritization calls. Lisa knew the
program. She knew the accounts. She had her own read on what
mattered. The dashboard's job wasn't to make her decisions for her.
It was to keep the cross-functional team calibrated to the same
reality she was already in. The value of the dashboard was the
shared vocabulary it created across functions, not the executive
judgment it replaced.

What I'm proud of in this program is what we promised the customer
base. A transparent upgrade. Dedicated focus where it was warranted.
Real ownership and accountability when the conversations got hard.
Those aren't things you put on a dashboard. They're things you have
to live up to one customer call at a time.

---

## Close (~45 sec)

The throughline across both cases, the AI capability layer and the
UTA upgrade program, is that the operating mechanisms I'm most
proud of building are the ones that change what a function can
*see*, not the ones that try to change what a function does. Case 1
changed what twenty PMs could do with their week, by making the work
they hated easier to retire. Case 2 changed what a multi-function
program could see about its own risk, by making the data underneath
the dashboard honest.

Different muscles. Same belief. Build the conditions where the
right thing becomes the easier thing, and the people you're working
alongside will do the rest.

I'm happy to take questions.

---

## Word count and pacing

Total: ~2,000 words.
- At 130 wpm (slow, considered): 15.3 min
- At 150 wpm (natural pace): 13.3 min

If you need tighter (12-13 min), cleanest cuts:

1. **Adoption and stakeholders** — could compress the AM/sales paragraph
   into two sentences. Save ~50 words.
2. **University story** — could compress the five flags into one
   sentence. Save ~40 words.
3. **Measurement** — could cut the "honest about what the dashboard
   did not do" paragraph. **Don't.** This is the move that lands.

About 90 words of trim available without losing structural beats.

## Verified specifics (locked from interview)

- UTA = UKG Pro Time and Attendance, licensed from Infor
- 300 UKG Pro customers, ~$250M ARR exposure
- Planning winter 2024 → upgrades started October 2025 → delivery
  date end of 2026
- Lisa (program manager), Ian (product owner), Leila (engineering
  manager) — named in the talk
- Four-source inputs: CSM/Salesforce sentiment, Jira defects,
  Salesforce cases, Salesforce + Power BI for ARR
- Jira labels co-designed with Leila: customer config / pre-existing /
  true defect requiring deployment
- Top-five weighting: ARR-dominant and true-defect-dominant, static
- Cadence: daily standup, weekly cross-functional call
- Engineering negotiation: pod-based (engineering) vs complexity-based
  (product) — complexity won on delivery-date resilience
- University customer: large university, red sentiment, contract
  issues, prior implementation scars, payroll concerns, fragile
  custom time-off workflow. Custom validation + dedicated Cognos
  engineering support. Made it through after Ian's RIF; CSM
  confirmed.
- 40% of 300 customers upgraded as of April 15, velocity increasing,
  ahead of schedule
- Honest: Lisa's decisions weren't changed by the dashboard. The
  dashboard's value was shared vocabulary, not replaced judgment.

## Backup assets for Q&A

- **Theresa "Tre" Morgan LinkedIn recommendation**, dated April 30,
  2026 — CSM on the university account. Quote available:
  *"clear communication across teams, ensuring that all stakeholders
  remained informed and aligned."* Use if panel asks for third-party
  validation of the work. Do NOT bring up unprompted.
- **What I'm proud of** (for the close, or for "what would you do
  differently" Q&A): *"A transparent upgrade. Dedicated focus where
  it was warranted. Real ownership and accountability when the
  conversations got hard."*
