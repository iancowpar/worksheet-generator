# Scaling Round Two

Round Two is useful because it is more than a prompt. The product combines a
teacher review loop, deterministic math verification, retry behavior, and a
carefully controlled PDF renderer. Keep those as the core app even if the AI
backend moves from Claude to Gemini.

## Near-term department rollout

1. Deploy the Streamlit app privately.
   - Use Render, Fly, Cloud Run, or another private host.
   - Put the app behind basic auth, Google Workspace auth, or district SSO.
   - Store provider API keys in the host's secret manager, never in the repo.

2. Add lightweight operational controls before broad sharing.
   - Per-teacher usage log: timestamp, uploaded file hash, type count, problem
     count, provider, model names, estimated cost, and flagged-problem count.
   - Monthly spend cap and a visible admin warning when usage is near the cap.
   - Maximum PDF size and maximum extracted type count so one bad upload cannot
     create a surprise bill.
   - A kill switch that disables new generation while leaving existing
     downloads available.

3. Preserve teacher trust.
   - Keep the review step mandatory.
   - Keep PDF generation blocked until every flagged problem is regenerated or
     manually accepted.
   - Add more fixture tests from real anonymized worksheets before each math
     department rollout.

## Provider strategy

`llm_provider.py` is the provider boundary. Today it implements Anthropic and
keeps the existing behavior as the default:

```bash
ROUND_TWO_LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=...
ROUND_TWO_EXTRACT_MODEL=claude-opus-4-7
ROUND_TWO_GENERATE_MODEL=claude-sonnet-4-6
ROUND_TWO_VERIFY_MODEL=claude-sonnet-4-6
```

The app should only talk to providers through this small interface:

- `extract_problem_types(pdf_bytes, system, user) -> raw_text`
- `generate_problem(system, user) -> raw_text`
- `verify_word_problem(system, user) -> raw_text`

That keeps prompts, parsing, verification, retries, and rendering independent
from a specific vendor.

## Gemini / school-network path

A Gemini Gem can be a strong companion, but it should not replace the app.
Use the Gem as a guided teacher assistant for:

- explaining how to upload or scan a test cleanly
- helping a teacher decide whether extracted problem types look right
- suggesting easier/same/harder variants in plain language
- documenting department norms for wording, accommodations, and retake prep

Keep these inside the app:

- PDF upload and parsing
- generated problem JSON contracts
- SymPy verification and retry loops
- answer-key rendering
- usage logs, cost controls, and audit trails

When the school wants Gemini inside its own environment, implement a
`GeminiProvider` behind `llm_provider.py` instead of forking the product. The
Gemini provider should return the same raw JSON contracts that Anthropic
returns today, so the rest of the pipeline stays unchanged.

## Test expansion checklist

Before inviting the whole department:

- Add anonymized extraction fixtures from at least five real tests.
- Add renderer smoke PDFs for every new layout that appears.
- Add verifier tests for each new `verifier_kind` or answer format.
- Add one integration-style test that parses saved extraction JSON, generates
  renderer dataclasses, and renders a PDF without calling an AI provider.
- Record false-positive verifier flags separately from true math errors so
  prompt and verifier tuning can improve over time.
