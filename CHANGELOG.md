# Changelog

All notable user-facing changes to Round Two.

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
