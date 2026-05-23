import Reveal from "./Reveal.jsx";
import { education } from "../data/resume.js";

export default function Education() {
  return (
    <Reveal>
      <section id="education" className="mb-14 sm:mb-20">
        <h2 className="label mb-7">Education</h2>
        {education.map((e, i) => (
          <div key={i} className="text-charcoal-mid leading-relaxed">
            <strong className="block text-charcoal font-bold mb-1">
              {e.degree}
            </strong>
            {e.school}  ·  {e.year}
          </div>
        ))}
      </section>
    </Reveal>
  );
}
