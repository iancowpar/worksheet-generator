# Deploy brief — paste into the iancowpar.github.io code session

Copy everything inside the fenced block below into the Claude Code
session attached to your `iancowpar.github.io` repo. It has the context
and the constraints baked in.

---

```
I need to deploy two static artifacts into this GitHub Pages repo
(iancowpar.github.io). Both should be reachable by URL but NOT linked
from my homepage yet — I'll add links myself later. Do not modify
index.html or any existing nav.

The source files live in another repo of mine: iancowpar/worksheet-generator,
on the branch `claude/tailor-crunchbase-application-Q7EDn`.

ARTIFACT 1 — AI adoption dashboard (priority)
- Source: dashboard/index.html in that repo/branch. It's a single
  self-contained HTML file (no build step, no dependencies except a
  Google Fonts link).
- Destination: /dashboard/index.html in this repo.
- Live URL target: iancowpar.github.io/dashboard/

ARTIFACT 2 — React resume page (optional, do only if quick)
- Source: portfolio-app/ in that repo/branch. It's a Vite + React +
  Tailwind app. It must be BUILT before deploy: `npm install && npm run build`
  produces a dist/ folder. vite.config.js already sets base:"./", so the
  built output is path-portable.
- Destination: copy the CONTENTS of portfolio-app/dist/ into /resume/
  in this repo (so /resume/index.html + /resume/assets/...).
- Live URL target: iancowpar.github.io/resume/

HOW TO GET THE SOURCE FILES — try in this order:
1. If you can clone/fetch: 
   git clone --branch claude/tailor-crunchbase-application-Q7EDn \
     https://github.com/iancowpar/worksheet-generator.git /tmp/wg
   Then copy from /tmp/wg/dashboard/index.html and /tmp/wg/portfolio-app/.
2. If you can't reach that repo, tell me and I'll paste/attach the files
   directly.

CONSTRAINTS:
- Do NOT add any link to these from index.html or site nav. Unlinked is intentional.
- Do NOT touch existing pages, CSS, or config beyond adding the two new folders.
- Preserve the dashboard HTML byte-for-byte — do not reformat or "improve" it.
- After placing files, verify locally if possible (python3 -m http.server,
  load /dashboard/ and /resume/), then commit and push to the branch
  Pages builds from (main or gh-pages — check the repo).
- Use clear commit messages: "Add /dashboard/ (unlinked)" and
  "Add /resume/ (unlinked)".

Start with Artifact 1. Report the live URLs when done.
```

---

## Notes for you (not part of the paste)

- **Artifact 1 is the safe bet.** Single self-contained HTML, no build,
  nothing to break. It'll deploy clean.
- **Artifact 2 (the React resume) needs Node** in that session to run
  `npm run build`. If the session can't build it, skip it for now and
  deploy just the dashboard — the dashboard is the time-sensitive one
  for Wednesday's panel.
- **If the other session can't reach the worksheet-generator repo**
  (private repo, no auth), it'll tell you, and you can either: (a) make
  that repo readable to it, or (b) come back here and I'll hand you the
  raw dashboard file to drop in directly. The file I sent you in chat is
  the same bytes — you can attach it to that session.
- **Pages branch gotcha:** some Pages repos build from `main`, others
  from a `gh-pages` branch or a `/docs` folder. The brief tells the
  session to check. If yours builds from `/docs`, the destinations
  become `/docs/dashboard/` and `/docs/resume/`.
