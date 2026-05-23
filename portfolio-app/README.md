# iancowpar / portfolio-app

The React + Vite + Tailwind version of the Principal-scope portfolio page.
Linked from the main `iancowpar` portfolio.

## Local

```
npm install
npm run dev      # http://localhost:5173
```

## Build / preview the static bundle

```
npm run build    # writes ./dist
npm run preview  # serves ./dist on http://localhost:4173
```

`vite.config.js` sets `base: "./"` so `dist/` is portable — drop it
into any static host (GitHub Pages, Vercel, Netlify, S3, Cloudflare
Pages) without a separate path config.

## Design system

Tokens live in `tailwind.config.js`, mirroring the Round Two / Cold Open
brand:

| token            | hex      | use                                |
|------------------|----------|------------------------------------|
| `charcoal`       | `#0B1220`| primary text                       |
| `charcoal-mid`   | `#3A4258`| secondary text                     |
| `charcoal-soft`  | `#6B7280`| tertiary (mono labels, dates)      |
| `glacier`        | `#7CC0B8`| brand mark / hover                 |
| `glacier-deep`   | `#5BA89E`| section labels, accent text        |
| `amber`          | `#F59E0B`| metric underlines (wins only)      |
| `indigo`         | `#4338CA`| focus rings only                   |
| `surface-soft`   | `#F7F7F5`| outcome card hover wash            |
| `border`         | `#E5E5E2`| 1px hairlines                      |

Typography is DM Sans throughout, JetBrains Mono for metadata. No
shadows, no third color, no extra typefaces.

## Files

```
src/
  App.jsx                  composition
  main.jsx                 entry
  index.css                Tailwind + component classes (label, metric, bullet-hairline)
  data/resume.js           all content as data
  components/
    Hero.jsx
    Summary.jsx
    Outcomes.jsx
    Experience.jsx
    Skills.jsx
    Education.jsx
    Writing.jsx
    Footer.jsx
    SectionNav.jsx         desktop-only sticky scroll-spy rail
    Reveal.jsx             scroll-triggered fade-up wrapper
```
