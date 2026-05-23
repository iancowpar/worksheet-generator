import { useEffect, useState } from "react";
import { sections } from "../data/resume.js";

/**
 * SectionNav — sticky vertical rail (desktop only) with scroll-spy.
 * Restrained: hairlines that thicken for the active section, mono labels on hover.
 */
export default function SectionNav() {
  const [active, setActive] = useState(sections[0].id);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        // Pick the entry closest to the top that's intersecting
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.target.offsetTop - b.target.offsetTop);
        if (visible.length > 0) {
          setActive(visible[0].target.id);
        }
      },
      {
        rootMargin: "-40% 0px -55% 0px",
        threshold: 0,
      }
    );

    sections.forEach(({ id }) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  return (
    <nav
      aria-label="Section navigation"
      className="no-print fixed right-8 top-1/2 -translate-y-1/2 z-10 hidden xl:block"
    >
      <ul className="flex flex-col gap-3">
        {sections.map(({ id, label }) => {
          const isActive = active === id;
          return (
            <li key={id}>
              <a
                href={`#${id}`}
                className="group flex items-center justify-end gap-3"
                aria-current={isActive ? "true" : undefined}
              >
                <span
                  className={`font-mono text-[0.7rem] tracking-[0.1em] uppercase transition-opacity duration-200 ${
                    isActive
                      ? "text-charcoal opacity-100"
                      : "text-charcoal-soft opacity-0 group-hover:opacity-100"
                  }`}
                >
                  {label}
                </span>
                <span
                  className={`block transition-all duration-300 ${
                    isActive
                      ? "h-px w-8 bg-glacier-deep"
                      : "h-px w-4 bg-border group-hover:w-6 group-hover:bg-charcoal-soft"
                  }`}
                />
              </a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
