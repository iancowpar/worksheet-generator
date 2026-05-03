/** @type {import('tailwindcss').Config} */
// Cold Open — Notion-adjacent quiet aesthetic.
// Warm cream surfaces + charcoal CTAs + the wordmark gradient as the singular
// brand color. Indigo is a quiet functional accent (focus rings, label tags,
// tier-1 badge) — never a primary action.
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#FFFFFF",            // pure white page surface — Notion-workspace tone
        surface: "#FFFFFF",       // white cards (same as page; the border defines the block)
        "surface-soft": "#F7F7F5", // faint cool-neutral grey for sidebar — matches Notion sidebar
        border: "#E5E5E2",        // soft cool-neutral border, defines blocks without shouting
        "text-primary": "#0B1220", // confident slate-near-black — now also the CTA color
        "text-muted": "#475569",   // slate-600
        "text-faint": "#94A3B8",   // slate-400
        accent: "#4338CA",         // indigo-700 — quiet functional accent only (focus, label tags)
        "accent-soft": "#E0E7FF",  // indigo-100 — kept for compatibility, used sparingly
        glacier: "#7CC0B8",        // brand color — Forward C mark, checkbox active state, brand surfaces
        warm: "#F59E0B",           // amber-500 — energy, hope, "wins"
        "warm-soft": "#FEF3C7",    // amber-100 — soft warm bg for callouts
        "tier-1": "#4338CA",       // indigo — premium target (functional, low-saturation use)
        "tier-2": "#F59E0B",       // amber — bridges energy
        "tier-3": "#94A3B8",       // slate — quiet
        success: "#10B981",        // emerald — "you got this"
      },
      fontFamily: {
        // Drop serif. DM Sans handles everything; we vary weight + size for hierarchy.
        sans: ["'DM Sans'", "system-ui", "sans-serif"],
        display: ["'DM Sans'", "system-ui", "sans-serif"],
        body: ["'DM Sans'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(11, 18, 32, 0.04), 0 4px 12px rgba(11, 18, 32, 0.04)",
        "card-hover":
          "0 2px 4px rgba(11, 18, 32, 0.06), 0 12px 24px rgba(11, 18, 32, 0.08)",
        glow: "0 0 0 4px rgba(67, 56, 202, 0.15)",
      },
      backgroundImage: {
        "brand-gradient":
          "linear-gradient(110deg, #4338CA 0%, #7C3AED 45%, #F59E0B 100%)",
        "brand-soft":
          "linear-gradient(180deg, rgba(67,56,202,0.05) 0%, rgba(245,158,11,0.04) 100%)",
      },
    },
  },
  plugins: [],
};
