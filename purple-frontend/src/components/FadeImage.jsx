import { useState } from "react";

/** <img> that fades in once actually loaded, instead of popping in abruptly or showing broken-image flashes. */
export default function FadeImage({ src, alt = "", className = "", ...rest }) {
  const [loaded, setLoaded] = useState(false);
  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      onLoad={() => setLoaded(true)}
      className={`img-fade ${loaded ? "loaded" : ""} ${className}`}
      {...rest}
    />
  );
}
