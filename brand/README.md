# Round Two — brand assets

The visual system for the worksheet generator. Built in the same
language as Cold Open: glacier teal stroke + charcoal dot, DM Sans
bold wordmark, Notion-adjacent quiet aesthetic.

## Files

| File | Use |
|---|---|
| `mark.svg` | The mark on its own (light backgrounds). 64×64 viewBox. |
| `mark-dark.svg` | Same mark, white dot, for dark backgrounds. |
| `wordmark.svg` | "Round Two" in DM Sans Bold, charcoal. 180×40 viewBox. |
| `logo.svg` | Lockup: mark + wordmark side-by-side. 178×36 viewBox. |
| `logo-dark.svg` | Lockup for dark backgrounds (white wordmark + white dot). |
| `favicon.svg` | Mark optimized for favicon contexts (no fixed pixel size). |
| `favicon-16.png` | 16×16 raster favicon. |
| `favicon-32.png` | 32×32 raster favicon. |
| `favicon-180.png` | 180×180 apple-touch-icon. |
| `favicon.ico` | Multi-size ICO (16+32) for legacy browsers. |
| `candidates/` | The three mark options proposed before selection. Kept for record. |

## Tokens

```
glacier   #7CC0B8   primary brand color (mark stroke)
charcoal  #0B1220   text-primary, mark dot, primary CTA fill
white     #FFFFFF   bg, surface
```

```
font-sans   "DM Sans", system-ui, sans-serif
font-mono   "JetBrains Mono", monospace
```

Mark geometry: 64×64 viewBox, 10pt stroke, round caps and joins,
4.5-radius dot. The path is `M 16 34 L 27 46 L 50 18`.

## Notes

- The wordmark and lockup use `<text>` elements that depend on DM Sans
  being loaded by the rendering context. Inside the Streamlit app this
  is guaranteed by `assets/theme.css`. For external use (slide decks,
  printed material, contexts where the font isn't loaded), convert the
  text to paths first.
- Favicon PNGs and the `.ico` are generated from `favicon.svg` via
  `cairosvg` + `Pillow`. To regenerate after editing `favicon.svg`,
  rerun the conversion script (or ask).
- `candidates/` is the audit trail of the three marks proposed during
  selection. Don't delete; useful when revisiting brand direction.
