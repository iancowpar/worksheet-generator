import Reveal from "./Reveal.jsx";
import { experience } from "../data/resume.js";

function Role({ role, isLast }) {
  return (
    <article
      className={`pb-10 ${isLast ? "" : "border-b border-border mb-10"}`}
    >
      <header className="flex flex-col gap-1.5 mb-4">
        <h3 className="text-[1.1875rem] font-bold tracking-tighter text-charcoal leading-tight">
          {role.role} <span className="text-charcoal-mid">·</span> {role.org}
        </h3>
        <p className="font-mono text-[0.8125rem] text-charcoal-soft">
          {role.location} &nbsp;·&nbsp; {role.dates}
        </p>
      </header>

      <p className="italic text-charcoal-mid leading-relaxed mb-5">
        {role.summary}
      </p>

      {role.bullets.length > 0 && (
        <ul className="flex flex-col gap-[1.1rem]">
          {role.bullets.map((b, i) => (
            <li
              key={i}
              className="bullet-hairline text-charcoal-mid leading-[1.65]"
            >
              <strong className="text-charcoal font-medium">{b.lead}</strong>
              {b.body}
            </li>
          ))}
        </ul>
      )}

      {role.footer && (
        <p className="italic text-charcoal-soft mt-5 text-[0.9375rem] leading-relaxed">
          {role.footer}
        </p>
      )}
    </article>
  );
}

export default function Experience() {
  return (
    <section id="experience" className="mb-14 sm:mb-20">
      <Reveal>
        <h2 className="label mb-7">Experience</h2>
      </Reveal>
      {experience.map((role, i) => (
        <Reveal key={i} delay={i * 0.05}>
          <Role role={role} isLast={i === experience.length - 1} />
        </Reveal>
      ))}
    </section>
  );
}
