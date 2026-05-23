import Reveal from "./Reveal.jsx";
import { writing } from "../data/resume.js";

export default function Writing() {
  return (
    <Reveal>
      <section id="writing" className="mb-14 sm:mb-20">
        <h2 className="label mb-7">Writing &amp; Thought Leadership</h2>
        <p className="mb-3">
          <strong className="text-charcoal font-bold">{writing.title}</strong>{" "}
          <span className="text-charcoal-mid">{writing.context}</span>
          {" · "}
          <a
            href={writing.href}
            className="link-underline text-charcoal-mid hover:text-charcoal"
          >
            {writing.hrefLabel}
          </a>
        </p>
        <p className="text-charcoal-mid leading-[1.65] max-w-[640px]">
          {writing.body}
        </p>
      </section>
    </Reveal>
  );
}
