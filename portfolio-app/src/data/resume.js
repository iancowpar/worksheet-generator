export const profile = {
  name: "Ian Cowpar",
  tagline: {
    body: "Principal-scope product leader. AI-first SaaS, platform and adoption, ",
    accent: "zero-to-one builder.",
  },
  contact: [
    { label: "ian.cowpar@gmail.com", href: "mailto:ian.cowpar@gmail.com" },
    { label: "351.235.0365", href: null },
    { label: "linkedin/ian-cowpar", href: "https://linkedin.com/in/ian-cowpar" },
    { label: "github/iancowpar", href: "https://github.com/iancowpar" },
    {
      label: "theunofficialleader",
      href: "https://theunofficialleader.substack.com",
    },
  ],
};

export const summary = `Product leader operating at principal scope inside AI-first SaaS. Two years owning product across a $250M ARR enterprise platform serving 300 customers at UKG, including the organization's first organized AI capability layer (built from zero, no top-down mandate) and a zero-to-one product taken from concept to production in a week. A decade prior at Broadridge in compliance-grade financial services, where client confidentiality and regulatory consequence were the operating environment. Originator of the Zero-Translation Building framework, with weekly published thought leadership on AI adoption realism.`;

// Each outcome: lead sentence (with optional inline metric), body, single highlighted metric.
// `metric` is the substring within `body` that gets the amber-underline treatment.
export const outcomes = [
  {
    n: "01",
    lead: "Built UKG product organization's first organized AI capability platform.",
    bodyBefore: "Scaled shared infrastructure across ",
    metric: "20 PMs",
    bodyAfter:
      " with no top-down mandate, to the point that multiple PMs built their own custom slash commands and retired manual workflows entirely. Adoption measured by what stopped, not what launched.",
  },
  {
    n: "02",
    lead: "Shipped a zero-to-one self-serve product from concept to production in a one-week prototype cycle.",
    bodyBefore: "Projected ",
    metric: "~30% time reduction",
    bodyAfter:
      " in a ticket-gated enterprise workflow. Wrote the prototype in Claude Code, scoped three business epics with the platform architect, delivered an engineering-ready package the architect built directly against.",
  },
  {
    n: "03",
    lead: null,
    leadBefore: "Surfaced ",
    leadMetric: "~$50M in at-risk ARR",
    leadAfter: " before escalation.",
    bodyBefore:
      "Built a composite risk model scoring top accounts on exposure, case volume, true-defect rate, and sentiment, replacing raw ticket counts with weighted signal and an automated weekly cadence the program lead acted on.",
    metric: null,
    bodyAfter: "",
  },
  {
    n: "04",
    lead: null,
    leadBefore: "Cut a working defect list from ~200 issues to 5 (",
    leadMetric: "~97%",
    leadAfter: ").",
    bodyBefore:
      "Built an opinionated analytics product with an embedded Claude Code function that routed the single highest-leverage action across five issue panels and four products.",
    metric: null,
    bodyAfter: "",
  },
  {
    n: "05",
    lead: "Drove cross-functional prioritization across product, engineering, and services without direct authority.",
    bodyBefore:
      "Translated customer signal from executive escalation rooms into tradeoff decisions across four product lines on a ",
    metric: "$250M ARR",
    bodyAfter: " platform serving 300 customers.",
  },
];

export const experience = [
  {
    role: "Senior Product Manager",
    org: "UKG",
    location: "Lowell, MA",
    dates: "Jun 2024 — Apr 2026",
    summary:
      "Principal-scope product ownership across AI capability, zero-to-one builds, and data products serving 300 enterprise customers on a $250M ARR platform.",
    bullets: [
      {
        lead: "Built the organization's first AI capability platform from zero,",
        body: " scaling it across 20 PMs without mandate and coaching individual PMs until they retired manual workflows for their own slash commands.",
      },
      {
        lead: "Shipped a zero-to-one self-serve product concept-to-production in one week,",
        body: " prototyped in Claude Code and scoped with the platform architect, projected to cut ~30% from a ticket-gated enterprise workflow.",
      },
      {
        lead: "Owned the upgrade program's data products",
        body: " — a composite ARR-risk model that surfaced ~$50M at risk before escalation, and an analytics product with an embedded Claude Code function that cut a defect list ~97%.",
      },
    ],
    footer:
      "Drove cross-functional prioritization in executive escalation rooms across four product lines. Brand Champion, UKG North America Regional Lead 2026; Fire Up ERG (women and allies), Business Innovation workstream lead.",
  },
  {
    role: "Business Analyst",
    org: "Broadridge Financial Solutions",
    location: "Andover, MA",
    dates: "Jan 2014 — Jun 2024",
    summary:
      "Forty-plus enterprise SaaS deployments end-to-end in compliance-grade financial services, where client confidentiality and regulatory consequence shaped every delivery decision.",
    bullets: [
      {
        lead: "Led 40+ enterprise SaaS client deployments end-to-end",
        body: " in a regulated environment where a wrong output had regulatory consequence, not a bug ticket; partnered with engineering on system behavior, data flows, and integration dependencies.",
      },
      {
        lead: "Served as internal subject-matter expert for an omni-channel communication product",
        body: " adopted across the entire enterprise client base, translating complex compliance capabilities into workflows non-technical buyers could operate without support.",
      },
    ],
    footer: null,
  },
  {
    role: "Senior Document Development Analyst",
    org: "Broadridge Financial Solutions",
    location: "Andover, MA",
    dates: "Jan 2006 — Jan 2014",
    summary:
      "Built and maintained complex client-facing document and communication systems in a regulated financial services environment.",
    bullets: [],
    footer: null,
  },
];

export const skills = [
  {
    category: "Product Strategy & Leadership",
    body: "Principal Product Manager-scope ownership, product vision and roadmap, OKR-to-execution, prioritization in ambiguous spaces, cross-functional leadership without direct authority, mentorship of junior PMs, outcomes over output, Agile / Scrum, B2B SaaS.",
  },
  {
    category: "AI as Core Multiplier",
    body: "AI capability platform building, embedded AI features inside internal products, Claude Code prototyping, twenty custom slash commands and a personal Claude Code productivity OS in active daily use, agentic workflows, AI adoption measurement (extinction over addition).",
  },
  {
    category: "Technical Credibility",
    body: "APIs and system architecture, data flows and integration dependencies, deployment-model and platform product thinking, technical-systems fluency with engineering, SQL.",
  },
  {
    category: "Data & Experimentation",
    body: "Opinionated analytics products, composite scoring and risk modeling, success-metric and KPI definition, hypothesis-driven development, signal-versus-noise routing.",
  },
  {
    category: "Enterprise SaaS",
    body: "Compliance-grade regulated delivery, client confidentiality as table stakes, enterprise customer escalation-room presence, multi-org program coordination, stakeholder management.",
  },
  {
    category: "Tooling",
    body: "Jira, Confluence, GitHub, SQL, Claude Code CLI, Slack MCP, Salesforce Service Cloud (operator).",
  },
];

export const education = [
  {
    degree: "Bachelor of Science, Management Information Systems and Management",
    school: "Manning School of Business, UMass Lowell",
    year: "1999",
  },
];

export const writing = {
  title: "The Unofficial Leader",
  context: "(Substack)",
  href: "https://theunofficialleader.substack.com",
  hrefLabel: "theunofficialleader.substack.com",
  body: "Weekly publication on where AI actually earns its place, adoption realism, and what's happening beneath the surface of how teams work. Originator of the Zero-Translation Building framework.",
};

// Section IDs for the section-nav rail
export const sections = [
  { id: "summary", label: "Summary" },
  { id: "outcomes", label: "Outcomes" },
  { id: "experience", label: "Experience" },
  { id: "skills", label: "Skills" },
  { id: "education", label: "Education" },
  { id: "writing", label: "Writing" },
];
