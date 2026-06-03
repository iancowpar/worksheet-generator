# Case 1 narrative — AI Capability Layer at UKG

Spoken version. Built for ~13-15 minutes at conversational pace
(130-150 wpm). Sections marked with beat headers for your reference
while rehearsing; do not read the headers out loud.

The voice constraint: contractions, no em dashes, no machine-gun
rhythm, no theatrical hooks, no fabricated moments. Flowing,
accumulating sentences. Operator register, not performer.

---

## Opening hook (~1.5 min)

I want to start in March, with one specific moment that ended up being
the seed for everything else.

I'd written a custom slash command in Claude Code for myself. It did
something pretty mundane. When I started a new epic in Jira, it would
pull the epic and all its stories, check that the required fields were
populated, run hygiene on anything broken, and move the epic into dev.
It wasn't fancy. It took me about an evening to write. But it took
something that used to eat thirty or forty minutes of my Monday and
reduced it to a button.

I shared it with my product partner, Vasu. Showed him the command,
walked him through what it did, watched him try it. And he stopped and
said, "Wait. How long would it take you to write me one of these for
the work I'm doing on roadmap planning?"

That was the moment. Not a strategy, not a roadmap, not a leadership
ask. One PM seeing that another PM had just removed an hour of their
week, and asking the only question that mattered. *What else can we do
with this?*

That question, asked once, in March, by one person, set the next six
weeks in motion.

---

## Structure (~3.5 min)

What I built from there wasn't a program. It was infrastructure.

The first piece was a slash command library. I started writing
commands for the workflows Vasu and I shared. Then for the ones our
manager Sam asked about. Then for the ones I noticed I was repeating
myself on. By the second week I had eight or ten commands. None of
them were impressive on their own. Each one was a small thing that
used to be manual and now wasn't.

The second piece was Confluence dashboards. I'd started using Claude
Code to build dashboards directly in Confluence. Things like a live
view of our team's epic health, our retro action items, our roadmap
state. I was building these for myself initially because I'd gotten
frustrated with the manual updates. But once they existed, Vasu and
Sam started referencing them in our team meetings. They became how we
talked about our work.

That created a problem. I had a slash command library and a growing
set of dashboards and no good way to keep track of any of it. So I
built a third piece. A Confluence page I called the build board. It
was just a single page with links to every dashboard, every command,
and a short description of what each one did. It was a map of the work.

The fourth piece was a GitHub repo. I'd been keeping the commands and
the Confluence templates in personal scratch space, and that wasn't
going to scale. So I built a shared repo. Pushed all the commands and
templates into it. Set up a basic README so a new PM could orient
themselves in five minutes. Shared the repo with our three-person
team first, then with anyone who asked.

None of these four pieces was the program. The program was what they
did together. The commands were the muscle. The dashboards were the
visibility. The build board was the index. The repo was the substrate.
And the whole thing was small enough that anyone could see all of it
on one screen, and that mattered, because the moment something gets
too big to hold in your head is the moment people stop contributing.

The discipline I tried to keep across all of it was that nothing was
theoretical. Every command in the library existed because some PM had
a real workflow they were trying to retire. Every dashboard existed
because some meeting was happening differently because of it. If I
couldn't point at a specific manual thing that wasn't happening
anymore because of what we'd built, the work didn't earn its place.

That was the structure. Not a curriculum, not a training program, not
a vendor rollout. Shared infrastructure built around real workflows
people actually hated.

---

## Adoption (~3.5 min)

The adoption story is where this gets interesting, because almost none
of it was driven by me.

The first thing that happened, after Vasu and I were a few weeks in,
was that he went to Sam, our senior director, and to Raph, our
director, and he started telling them what we were doing. He framed
it as me being the AI champion for our area. I didn't ask him to do
that. He just did it.

That conversation moved into a peer learning session. I organized it
for the twenty PMs in our broader WFM group. One session, ninety
minutes, no slides. I walked them through the repo, I demoed a few
commands, I let them try one on their own work in real time. The
session itself wasn't the point. The point was what happened after.

After that session, the first PM who came to me with specifics was
Maria. Maria works on the translation team. Her job is to add
translated versions of WFM software as we expand into new markets.
Coordinating a new language launch means a massive amount of Jira
coordination across about a dozen teams. Cloning epics, restructuring
stories, making sure all the descriptions and acceptance criteria
reflect the new market, not just doing a Hungarian-for-Polish text
swap.

I sat with her for a couple of hours and we wrote a command together.
It would take a previous language deployment, clone the entire epic
structure, identify the right paths, make intelligent updates to
descriptions, and push everything into the right state. When she ran
it for the first time, the thing that broke her brain wasn't that it
worked. It was that she could go work on something else while it did
the work. She said, and I'll never forget this, *"It's magic. It feels
like life will never be the same again."*

She retired her old workflow that afternoon.

That same week, Laura, my product partner on Ascentis, saw what I'd
built for our quarterly business review. The QBR was something I used
to spend six or seven hours on every quarter. Go through Jira, bucket
the work by category, build the slides. I'd written a command that
did the whole thing in about ten minutes. Laura watched me run it
once, asked for the command, and used it for her own QBR at the end
of March. She didn't need me to walk her through it. She just took it
and ran with it.

And the third thing that happened, which to me was the most important
signal of all, was that Keith, my other product partner, and Vasu
started writing their own commands and contributing them back to the
repo. The WFM-wide Slack channel that had existed mostly as a place
to share interesting articles became a two-way exchange. We weren't
just consumers of that channel anymore. We were a hub for it.

That was when I knew the thing had legs. People weren't waiting for
me. They were building.

---

## Stakeholders (~2.5 min)

I want to be specific about who was involved, because the stakeholder
management on this one is different from how I'd describe most
cross-functional programs I've run.

Vasu, my product partner, was the first believer and the one who
carried it upward. He's the person who decided, on his own, to
position me to Sam and Raph as the AI champion for our area. Without
that move, this thing stays a small project between two PMs. The
single highest-leverage stakeholder relationship in the whole program
was the one I already had as a peer.

Sam, our senior director, was the executive cover. Once Vasu surfaced
the work, Sam didn't try to formalize it. He didn't ask me to write a
charter or run it through governance. He just gave it room to grow.
The fact that he didn't formalize it was the thing that let it stay
healthy. Programs like this die when they get sponsored and turned
into a roadmap line item, because once you have to report on adoption
metrics every two weeks, you start gaming them. Sam protected it from
that.

Raph, our director, was the operational sponsor. He's the one who
asked the practical questions about how to spread this further, who
started thinking about whether the peer-group model could move outside
our group.

And the twenty PMs were both the audience and the engine. I want to
be careful here. The peer learning session reached twenty PMs. It's
not the case that twenty PMs each independently built command
libraries. What happened was that the session reached twenty, the
early adopters built, the champions emerged, and the work propagated
through Slack and through one-on-one conversations.

The discipline I tried to hold across all of those relationships was
that I wasn't asking anyone for permission, and I wasn't operating
invisibly either. The work was loud where it needed to be visible
and quiet where it didn't.

---

## Measurement (~3 min)

I want to be careful and honest with the measurement story, because I
think the measurement story is the part of this case that's easiest
to inflate and the part that matters most that I don't.

The honest measurement frame I held to throughout was *what stopped*,
not what launched. If I built something and no manual workflow
stopped happening because of it, the thing I built wasn't real. If a
workflow stopped, that was the only proof I trusted.

By that measure, the program retired three named workflows across
three teams in six weeks, and that was just what I could see directly.

Maria retired her language deployment coordination workflow the day
we built her command together. Laura retired her QBR preparation
workflow at the end of March. And I retired several of my own
workflows along the way. The Jira hygiene one, the epic-start one,
the retro action tracking, the roadmap rollup. Each one a thing that
used to take time and now didn't.

The signal that mattered more than any of those, though, was that
Keith and Vasu started building their own commands. That's the
measurement that matters most to me. Because if I'm the only one
building, then what I've built is a personal productivity hack with
an audience. The moment other people are building and contributing
back, the program isn't dependent on me anymore. That's the only
metric that distinguishes real adoption from theater.

What I deliberately did not measure, and what I would not measure if
I ran this again, is token usage, hours saved as a global number, or
anything that looks like an aggregate productivity metric. Token
usage isn't an adoption metric. Hours saved as a global number is
gameable, and people will game it. The only adoption signal I trust
is what stopped, and the only sustainability signal I trust is who
else is building.

If you ask me what the program would have grown into if it had run
another six months, my honest answer is I don't know. The RIF on
April 15 cut it short. But I know what it looked like at week six,
and at week six it was a self-organizing peer community with shared
infrastructure being maintained and extended by people I hadn't asked
to maintain or extend it. That was the goal. The honest measure of
whether I'd built something good was whether it kept running when I
wasn't running it. The week before I was let go, it was.

---

## Close / bridge to Case 2 (~1 min)

The reason I tell this case the way I do, with the people named and
the workflows named and the metrics held back, is because I think the
lesson of the program is not about the technology. It's about the
discipline.

Most AI enablement programs fail because they treat AI as a tool
installation problem. License it, train people on it, declare
adoption. The honest version is that AI is a behavior change problem.
People retire the workflows they're going to retire, and they keep
the ones they're going to keep, and the only thing the program can do
is create the conditions where retiring a workflow feels safer than
keeping it.

What I want to do with the second case is talk about a different
shape of operating mechanism. Different muscle. Same belief about
what it means to build something that actually lands.

---

## Word count and pacing

Total: ~2,050 words.
- At 130 wpm (slow, considered): 15.7 min
- At 150 wpm (natural pace): 13.7 min

If you need to come in tighter (12-13 min), the cleanest cuts are:

1. **Structure** — could collapse the "discipline" closing paragraph
   into one sentence. Save ~60 words.
2. **Stakeholders** — could compress Raph's paragraph into one
   sentence. Save ~40 words.
3. **Measurement** — could cut the "what I deliberately did not
   measure" paragraph in half. Save ~50 words.

That's ~150 words of trim available without losing structural beats.

## Verify before rehearsing

1. **Names spelled right.** Vasu, Sam (senior director), Raph
   (director), Maria (translation), Keith (product partner), Laura
   (Ascentis product partner). Flag any misspellings.
2. **Maria's quote.** "It's magic. It feels like life will never be
   the same again." Confirm wording.
3. **Laura's QBR cadence.** End of March is when she ran it for her
   QBR. Confirm.
4. **The "dozen teams" claim** for Maria's translation deployment.
   Confirm or correct.
5. **"Six or seven hours" for QBR prep.** Your number, confirm.

Any corrections needed, flag now before I start Case 2.
