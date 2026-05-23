import Reveal from "./Reveal.jsx";
import { skills } from "../data/resume.js";

export default function Skills() {
  return (
    <section id="skills" className="mb-14 sm:mb-20">
      <Reveal>
        <h2 className="label mb-7">Skills &amp; Focus Areas</h2>
      </Reveal>
      <dl className="flex flex-col">
        {skills.map((s, i) => (
          <Reveal key={s.category} delay={i * 0.04}>
            <div
              className={`py-6 ${
                i === 0 ? "pt-0" : "border-t border-border"
              } ${i === skills.length - 1 ? "pb-0" : ""}`}
            >
              <dt className="font-bold text-charcoal mb-2 text-[0.9375rem] tracking-tighter">
                {s.category}
              </dt>
              <dd className="text-charcoal-mid leading-[1.65] text-[0.9375rem]">
                {s.body}
              </dd>
            </div>
          </Reveal>
        ))}
      </dl>
    </section>
  );
}
