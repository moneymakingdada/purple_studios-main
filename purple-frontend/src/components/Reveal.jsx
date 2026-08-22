import { useEffect, useRef, useState } from "react";

/**
 * Wraps content that should fade/slide up into view as the user scrolls to it.
 * Usage: <Reveal><div className="grid-4">...</div></Reveal>
 * Pass stagger to animate direct children one after another (for grids/lists).
 */
export default function Reveal({ children, stagger = false, as: Tag = "div", className = "", ...rest }) {
  const ref = useRef(null);
  const [inView, setInView] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true);
          observer.disconnect();
        }
      },
      { threshold: 0.12 }
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  const base = stagger ? "reveal-stagger" : "reveal";

  return (
    <Tag ref={ref} className={`${base} ${inView ? "in-view" : ""} ${className}`} {...rest}>
      {children}
    </Tag>
  );
}
