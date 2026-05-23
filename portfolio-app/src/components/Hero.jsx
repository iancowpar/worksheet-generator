import { motion, useReducedMotion } from "framer-motion";
import { profile } from "../data/resume.js";

export default function Hero() {
  const reduce = useReducedMotion();
  const motionProps = reduce
    ? {}
    : {
        initial: { opacity: 0, y: 12 },
        animate: { opacity: 1, y: 0 },
      };

  return (
    <header className="mb-14 sm:mb-20 lg:mb-24">
      <motion.h1
        {...motionProps}
        transition={{ duration: 0.7, ease: [0.21, 0.61, 0.35, 1] }}
        className="text-[2.5rem] sm:text-6xl lg:text-[4.25rem] font-bold leading-none tracking-tightest text-charcoal mb-6"
      >
        {profile.name}
      </motion.h1>

      <motion.p
        {...motionProps}
        transition={{
          duration: 0.7,
          ease: [0.21, 0.61, 0.35, 1],
          delay: 0.1,
        }}
        className="text-[1.125rem] sm:text-xl lg:text-[1.375rem] font-normal leading-snug tracking-tighter text-charcoal-mid max-w-[600px] mb-9"
      >
        {profile.tagline.body}
        <span className="text-glacier-deep font-medium">
          {profile.tagline.accent}
        </span>
      </motion.p>

      <motion.ul
        {...motionProps}
        transition={{
          duration: 0.7,
          ease: [0.21, 0.61, 0.35, 1],
          delay: 0.2,
        }}
        className="flex flex-wrap gap-y-2 gap-x-5 font-mono text-[0.8125rem] text-charcoal-soft"
      >
        {profile.contact.map((item) => (
          <li key={item.label}>
            {item.href ? (
              <a href={item.href} className="link-underline hover:text-charcoal">
                {item.label}
              </a>
            ) : (
              <span>{item.label}</span>
            )}
          </li>
        ))}
      </motion.ul>
    </header>
  );
}
