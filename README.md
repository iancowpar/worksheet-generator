# Round Two

Round Two is a Streamlit web app for special-education math teachers.
Upload the test your students just took, and Round Two produces a
printable practice worksheet PDF — one worked example per problem
type, five practice problems per type distributed evenly down the
page, and a final answer key — so students can rehearse before
retaking the test.

## How it works

- Extract the distinct problem types from the uploaded test using
  the configured AI provider. The default provider is Anthropic using
  Claude (`claude-opus-4-7`).
- Generate per-problem variants for each type using the configured
  generation model. The default is Claude (`claude-sonnet-4-6`), with
  SymPy verification and a regenerate
  loop for incorrect answers.
- Render the final PDF with ReportLab using the canonical visual
  style (NAVY headers, tan-bordered example boxes, manual exponent
  rendering, even problem distribution).

## Tech stack

- Python 3.11+
- Streamlit (UI)
- Anthropic Python SDK (Claude API)
- ReportLab (PDF generation, canvas-direct)
- pdfplumber (test PDF text extraction)
- SymPy (algebraic answer verification)
- Pillow (image handling)

See `requirements.txt` for pinned versions and `CLAUDE.md` for the
full project spec, visual rules, and acceptance test.

## Run locally

```
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
streamlit run app.py
```

Optional provider/model configuration:

```
export ROUND_TWO_LLM_PROVIDER=anthropic
export ROUND_TWO_EXTRACT_MODEL=claude-opus-4-7
export ROUND_TWO_GENERATE_MODEL=claude-sonnet-4-6
export ROUND_TWO_VERIFY_MODEL=claude-sonnet-4-6
```

`ROUND_TWO_LLM_PROVIDER=gemini` is reserved for a district Gemini backend,
but this build does not implement the Gemini client yet. See `SCALING.md`
for the rollout path.

## Deploy

### Streamlit Community Cloud (public repo, free)

Connect the repository in
[share.streamlit.io](https://share.streamlit.io), point the app at
`app.py`, and add `ANTHROPIC_API_KEY` in the Secrets UI. The free
tier requires a public repository.

### Render (private repo, free tier)

Recommended for internal-school deployment where the repo should
stay private. Create a new Web Service from the repo with:

- Build command: `pip install -r requirements.txt`
- Start command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
- Environment variable: `ANTHROPIC_API_KEY`

For department use, prefer a private deployment with basic auth or school
SSO, secret-managed API keys, and usage monitoring before sharing the URL
broadly.

## Cost

A typical worksheet runs $0.10–$0.50 in Claude API usage (one
extraction call plus per-problem generation and verification). Set
a monthly spend cap in the Anthropic Console before you share the
app with other teachers.

## License

MIT — see `LICENSE`.
