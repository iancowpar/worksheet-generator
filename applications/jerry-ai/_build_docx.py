"""Generate Jerry.ai resume as a .docx file."""

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

OUTPUT = "/home/user/worksheet-generator/applications/jerry-ai/Ian_Cowpar_Resume_Jerry_AI.docx"

doc = Document()

# Margins
for section in doc.sections:
    section.top_margin = Inches(0.6)
    section.bottom_margin = Inches(0.6)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)

# Set Normal style font
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(10.5)


def add_run(p, text, bold=False, italic=False, size=None):
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    r.font.name = "Calibri"
    if size:
        r.font.size = Pt(size)
    return r


def add_blank(space=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space)
    return p


def add_section_header(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(2)
    add_run(p, text, bold=True, size=11)
    # underline-ish: use a paragraph border via xml could work, but keep it simple
    return p


def add_body(text_runs, indent=None, space_after=2):
    """text_runs = list of (text, bold, italic) tuples"""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    if indent is not None:
        p.paragraph_format.left_indent = Inches(indent)
    for text, bold, italic in text_runs:
        add_run(p, text, bold=bold, italic=italic)
    return p


def add_bullet(text_runs):
    """Indented bullet line."""
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.left_indent = Inches(0.25)
    for text, bold, italic in text_runs:
        add_run(p, text, bold=bold, italic=italic)
    return p


# === NAME ===
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(0)
p.paragraph_format.space_after = Pt(2)
add_run(p, "Ian Cowpar", bold=True, size=18)

# === TAGLINE ===
add_body([
    ("PM building at principal scope  |  AI-fluent prototyping  |  data products with opinion  |  zero-translation systems", False, False)
], space_after=2)

# === CONTACT ===
add_body([
    ("ian.cowpar@gmail.com  |  351-235-0365  |  linkedin.com/in/ian-cowpar  |  theunofficialleader.substack.com", False, False)
], space_after=4)

# === SUMMARY ===
add_section_header("SUMMARY")
add_body([
    ("Senior PM building AI platforms, data products, and self-serve flows inside compliance-heavy enterprise environments. Two years at UKG protecting 300 enterprise customers ($250M ARR) through migration off legacy workforce management — scaled UKG product's first organized AI capability layer across the team without a top-down mandate, built the data products that let services and engineering catch problems before customers felt them, and shipped a 0→1 migration tool with the prototype I wrote myself in Claude Code. Ten years prior at Broadridge: 40+ enterprise deployments in compliance-grade financial services.", False, False)
], space_after=4)

# === EXPERIENCE ===
add_section_header("EXPERIENCE")

# UKG
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(2)
p.paragraph_format.space_after = Pt(0)
add_run(p, "Senior Product Manager", bold=True)
add_run(p, "    Jun 2024 – Apr 2026", bold=False)

add_body([
    ("UKG  |  Lowell, MA  |  $250M ARR  |  Data products, AI tooling, and self-serve flows protecting enterprise customers through migration", False, True)
], space_after=3)

bullets = [
    [("Built UKG product's first organized AI capability layer. ", True, False),
     ("Started as a personal automation library, scaled into team-wide shared capability without a top-down mandate. Adoption spread because the thing worked better than what it replaced — the only kind of adoption that lasts.", False, False)],
    [("Built a 0→1 self-serve migration tool, idea to production. ", True, False),
     ("Took it from concept through three business-epic decomposition (UI, rules, deployment), wrote the working prototype myself in Claude Code, designed the UX feedback loop and persona, and handed engineering the full delivery package — bepics, epics, stories, Gantt, roadmap. Now in active production; the Services org runs migrations independently without an engineering ticket.", False, False)],
    [("Designed a five-panel operational analytics product ", True, False),
     ("classifying open issues across customer escalations, code defects, internal bugs, and CVEs across four products; auto-refreshed daily, surfacing a single highest-leverage action per view. Opinionated routing, not a dashboard.", False, False)],
    [("Designed sprint health instrumentation ", True, False),
     ("refreshing every 15 minutes across two engineering teams, with documented rejection criteria for burndown, velocity, and story-point anti-patterns — each with technical rationale. Built for signal, not ceremony.", False, False)],
    [("Led ARR-focused risk tracking for the UTA upgrade program: ", True, False),
     ("automated weekly reporting routes every open blocker to the program lead; live tracking surfaces aging issues before escalation.", False, False)],
    [("Served as the product-side voice on enterprise customer escalation and pre-upgrade calls ", True, False),
     ("— synthesizing what 300 UTA customers ($250M ARR) actually needed versus what was on the roadmap, feeding that gap back into prioritization decisions.", False, False)],
]
for b in bullets:
    add_bullet(b)

add_body([
    ("Brand Champion, UKG North America Regional Lead 2026  |  Fire Up ERG (women and allies), Business Innovation workstream lead", False, True)
], space_after=4)

# Broadridge Business Analyst
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(4)
p.paragraph_format.space_after = Pt(0)
add_run(p, "Business Analyst", bold=True)
add_run(p, "    Jan 2014 – Jun 2024", bold=False)

add_body([
    ("Broadridge Financial Solutions  |  Andover, MA", False, True)
], space_after=3)

broadridge_bullets = [
    [("Led 40+ enterprise client deployments end-to-end in a compliance-grade financial services environment; developed strong instincts for regulatory consequence, requirements quality, and the difference between a delivery that closes and a product that keeps producing.", False, False)],
    [("Internal SME for an omni-channel communication product adopted across the full client base; translated complex compliance capabilities into workflows non-technical buyers could operate without support.", False, False)],
]
for b in broadridge_bullets:
    add_bullet(b)

# Broadridge Sr. Doc Dev Analyst
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(4)
p.paragraph_format.space_after = Pt(0)
add_run(p, "Sr. Document Development Analyst", bold=True)
add_run(p, "    Jan 2006 – Jan 2014", bold=False)

add_body([
    ("Broadridge Financial Solutions  |  Andover, MA", False, True)
], space_after=4)

# === SKILLS ===
add_section_header("SKILLS AND FOCUS AREAS")

skills = [
    ("AI as Co-Builder:  ", "Claude Code prototyping, agentic workflows, AI-fluent product development, PM automation, zero-translation building"),
    ("Product:  ", "0→1 product building, data products, self-serve flow design, MVP definition, end-to-end delivery from prototype to production, customer discovery, persona and UX feedback loops, B2B SaaS"),
    ("Data & Analytics:  ", "Operational analytics products, opinionated instrumentation, KPI definition, automated reporting cadence, qualitative-to-structured synthesis"),
    ("Compliance & Enterprise:  ", "Regulatory-consequence delivery, compliance-grade financial services, multi-stakeholder coordination, executive customer engagement, escalation room presence"),
    ("Tooling:  ", "Jira, Confluence, GitHub, SQL, Slack MCP, Claude Code CLI"),
]
for label, content in skills:
    add_body([(label, True, False), (content, False, False)], space_after=3)

# === EDUCATION ===
add_section_header("EDUCATION")
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(0)
p.paragraph_format.space_after = Pt(0)
add_run(p, "Bachelor of Science, Management Information Systems and Management", bold=True)
add_body([
    ("Manning School of Business, UMass Lowell  |  1999", False, False)
], space_after=4)

# === WRITING ===
add_section_header("WRITING AND THOUGHT LEADERSHIP")
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(0)
p.paragraph_format.space_after = Pt(0)
add_run(p, "The Unofficial Leader", bold=True)
add_run(p, "  (Substack)  |  theunofficialleader.substack.com", bold=False)
add_body([
    ("Weekly publication on AI adoption, unofficial leadership, and what's happening beneath the surface of how teams work. Originator of the Zero-Translation Building framework. Active LinkedIn audience engagement on product, AI adoption, and team dynamics.", False, False)
], space_after=0)

doc.save(OUTPUT)
print(f"Saved: {OUTPUT}")
