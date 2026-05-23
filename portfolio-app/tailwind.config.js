/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        charcoal: {
          DEFAULT: "#0B1220",
          mid: "#3A4258",
          soft: "#6B7280",
        },
        glacier: {
          DEFAULT: "#7CC0B8",
          deep: "#5BA89E",
        },
        amber: {
          DEFAULT: "#F59E0B",
        },
        indigo: {
          DEFAULT: "#4338CA",
        },
        surface: {
          soft: "#F7F7F5",
        },
        border: {
          DEFAULT: "#E5E5E2",
        },
      },
      fontFamily: {
        sans: [
          "DM Sans",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "sans-serif",
        ],
        mono: [
          "JetBrains Mono",
          "ui-monospace",
          "SF Mono",
          "Menlo",
          "monospace",
        ],
      },
      letterSpacing: {
        tightest: "-0.035em",
        tighter: "-0.02em",
        labels: "0.14em",
      },
      maxWidth: {
        content: "720px",
      },
    },
  },
  plugins: [],
};
