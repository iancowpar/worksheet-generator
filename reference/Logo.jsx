/**
 * Cold Open logo — Forward C in Glacier teal (#7CC0B8) with a charcoal
 * directional dot, paired with the "Cold Open" wordmark in DM Sans bold.
 *
 * Two exports:
 *   - LogoMark — the mark alone (favicon, avatar, tight-space contexts)
 *   - Logo     — the lockup (mark + wordmark side-by-side)
 *
 * Both accept a size prop. Logo's size sets the wordmark font-size; the
 * mark scales to ~1.5x of that automatically. dotColor and textColor
 * default to charcoal but can flip to white on dark backgrounds.
 */

export const GLACIER = "#7CC0B8";
export const CHARCOAL = "#0B1220";

export function LogoMark({ size = 32, accent = GLACIER, dotColor = CHARCOAL }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="Cold Open"
    >
      <path
        d="M 50 18 A 22 22 0 1 0 50 46"
        stroke={accent}
        strokeWidth="10"
        strokeLinecap="round"
        fill="none"
      />
      <circle cx="52" cy="32" r="4.5" fill={dotColor} />
    </svg>
  );
}

export function Logo({
  size = 18,
  accent = GLACIER,
  dotColor = CHARCOAL,
  textColor = CHARCOAL,
  className = "",
}) {
  return (
    <span className={`inline-flex items-center gap-2.5 ${className}`}>
      <LogoMark
        size={Math.round(size * 1.5)}
        accent={accent}
        dotColor={dotColor}
      />
      <span
        className="font-bold tracking-tight leading-none"
        style={{ color: textColor, fontSize: size }}
      >
        Cold Open
      </span>
    </span>
  );
}

export default Logo;
