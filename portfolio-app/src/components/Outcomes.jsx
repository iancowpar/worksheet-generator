import Reveal from "./Reveal.jsx";
import { outcomes } from "../data/resume.js";

function Outcome({ outcome, index }) {
  const lead = outcome.lead ? (
    <p className="font-bold text-[1.0625rem] leading-snug text-charcoal mb-2 tracking-tighter">
      {outcome.lead}
    </p>
  ) : (
    <p className="font-bold text-[1.0625rem] leading-snug text-charcoal mb-2 tracking-tighter">
      {outcome.leadBefore}
      <span className="metric">{outcome.leadMetric}</span>
      {outcome.leadAfter}
    </p>
  );

  return (
    <Reveal delay={index * 0.05}>
      <li
        className={`grid grid-cols-[3rem_1fr] gap-6 items-start py-7 ${
          index === 0 ? "" : "border-t border-border"
        } group transition-colors duration-300 hover:bg-surface-soft/40 -mx-4 px-4 rounded-sm`}
      >
        <span className="font-mono text-[0.8125rem] text-glacier-deep font-medium pt-[0.35rem] tracking-wider">
          {outcome.n}
        </span>
        <div>
          {lead}
          <p className="text-charcoal-mid leading-[1.65]">
            {outcome.bodyBefore}
            {outcome.metric && <span className="metric">{outcome.metric}</span>}
            {outcome.bodyAfter}
          </p>
        </div>
      </li>
    </Reveal>
  );
}

export default function Outcomes() {
  return (
    <section id="outcomes" className="mb-14 sm:mb-20">
      <Reveal>
        <h2 className="label mb-7">Selected Outcomes</h2>
      </Reveal>
      <ol className="list-none">
        {outcomes.map((outcome, i) => (
          <Outcome key={outcome.n} outcome={outcome} index={i} />
        ))}
      </ol>
    </section>
  );
}
