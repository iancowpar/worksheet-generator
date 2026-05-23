import Reveal from "./Reveal.jsx";
import { summary } from "../data/resume.js";

export default function Summary() {
  return (
    <Reveal>
      <section id="summary" className="mb-14 sm:mb-20">
        <h2 className="label mb-7">Summary</h2>
        <p className="text-[1.0625rem] leading-[1.7] text-charcoal max-w-[640px]">
          {summary}
        </p>
      </section>
    </Reveal>
  );
}
