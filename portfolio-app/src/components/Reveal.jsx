import { motion, useReducedMotion } from "framer-motion";

/**
 * Reveal — section wrapper that fades up subtly on first viewport entry.
 * Respects prefers-reduced-motion. Once per session, not on every scroll.
 */
export default function Reveal({ children, delay = 0, className = "" }) {
  const reduce = useReducedMotion();

  if (reduce) {
    return <div className={className}>{children}</div>;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2, margin: "0px 0px -80px 0px" }}
      transition={{ duration: 0.55, ease: [0.21, 0.61, 0.35, 1], delay }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
