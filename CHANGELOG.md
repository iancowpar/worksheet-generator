# Changelog

All notable user-facing changes to Round Two.

## 2026-05-29

### Fixed
- **Far fewer false "can't verify the answer" flags.** The auto-checker used
  to flag any answer it couldn't parse — including correct answers written in
  a slightly different format — which blocked the whole worksheet behind a
  manual review. The checker now separates "I solved it and the answer is
  wrong" from "I couldn't read this format," and only the former counts as a
  real problem. Unreadable-format cases get a fresh Claude solve-from-scratch
  check before anything is flagged.
- **The checker now understands more answer formats.** It accepts common
  variations teachers and the generator naturally produce — `Arithmetic, d = -9`
  without parentheses, a bare `Geometric`, `f(n) = 5 · 3^{n-1}` with a middot,
  `r = 1/3` or just `1/3`, multiple-choice answers given as just `(B)`, and
  spacing differences in multiple-choice option text.

### Changed
- **The generator is now told the exact answer format** the checker expects
  for each problem type, so correct answers land in a verifiable shape on the
  first try instead of being flagged and regenerated.

## 2026-05-04

### Added
- **Math + Language difficulty knobs** on the Types page — two independent
  axes (`Easier` / `Same` / `Harder`). A student who can do the algebra but
  struggles with dense word problems can get the same arithmetic in simpler
  sentence structure.
- **"Accept anyway"** override on flagged problems for cases where the
  verifier is too strict. The teacher's manual review wins.
- **Loading overlay** with a centered card and glacier progress bar during
  the three slow operations (extraction, generation, PDF render).
- **Sample worksheet download** on the upload page so the teacher can verify
  the output format before spending API credit.
- **Custom worksheet title input** on upload, with a live preview of the
  slugified `.pdf` filename.
- **What's new link** in the sidebar pointing to this file.

### Changed
- **PDF generation is now gated** behind flagged-problem resolution — the
  teacher must regenerate or explicitly accept each ⚠️ problem before the
  download button enables. No more wrong math shipping by accident.
- **Polynomial substitution arithmetic** in word-problem answers is now
  recomputed deterministically with SymPy and rewritten before verification.
  Eliminates the most common Claude-arithmetic failure ("Profit = ...; at
  x = 5, profit = $400" when it should be `-$100`).
- **Verifier auto-falls back to Claude second-pass** when a SymPy verifier
  crashes parsing a non-expression body. Fixes the perimeter / profit
  word-problem failures where Claude misassigned `verifier_kind` during
  extraction.
- **Two-tier visual** — glacier-wash gradient hero on the upload page;
  internal pages stay Notion-quiet (1 px borders, no shadows).
- **Hero on the upload page** — three-line oversized headline ("Test on
  Friday. / Practice by Monday. / Math you can trust.") with a small brand
  lockup above and the four capability cards below.
- **Sidebar** redesigned in Notion-row style — tight 14 px status icons
  (glacier checkmark for done, glacier dot for active, hollow circle for
  upcoming) with subtle hover.
- **Inline-styled** every block on the upload, types, problems, and PDF
  pages so styling survives Streamlit's HTML sanitizer.

### Fixed
- Primary button labels rendering charcoal-on-charcoal (Streamlit's `<p>`
  color rule was beating the button color).
- Type-section badges (T1, T2…) mashed against the type title because the
  inline span style was being stripped by the sanitizer — now a flex layout
  with sibling divs.
- Progress bar drawing inverted (charcoal fill on glacier track instead of
  the reverse).
- The `&lt;style&gt;` tag inside `assets/theme.css` comments closing the
  outer style element early and dumping the entire stylesheet into the
  body as visible text.
- Math correctness: `Profit = 12x³ - 40x² - 600` evaluated at `x = 5` now
  ships as `-$100` (correct) rather than getting flagged or auto-rejected.
