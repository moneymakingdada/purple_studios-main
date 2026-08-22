import { useEffect, useState } from "react";
import { fetchGallery } from "../api/gallery";
import Reveal from "../components/Reveal";
import FadeImage from "../components/FadeImage";


export default function Gallery() {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [active, setActive] = useState(null);

  useEffect(() => {
    fetchGallery().then(setImages).catch(() => setImages([])).finally(() => setLoading(false));
  }, []);

  return (
    <div className="section" style={{ paddingBottom: 100 }}>
      <div className="section-head">
        <span className="eyebrow">Our work</span>
        <h2>A look inside Purple</h2>
      </div>

      {loading && (
        <div className="gallery-grid">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="skeleton skeleton-thumb" />
          ))}
        </div>
      )}

      {!loading && images.length === 0 && (
        <p className="empty-text">No portfolio images yet — check back soon as our stylists add their work.</p>
      )}

      {!loading && images.length > 0 && (
        <Reveal stagger className="gallery-grid">
          {images.map((img) => (
            <div key={img.id} className="gallery-item" onClick={() => setActive(img)}>
              <FadeImage src={img.image} alt={img.caption || img.stylist_name} />
              <div className="gallery-item-overlay">
                <div className="name">{img.stylist_name}</div>
                {img.stylist_title && <div className="title">{img.stylist_title}</div>}
              </div>
            </div>
          ))}
        </Reveal>
      )}

      {active && (
        <div className="lightbox-backdrop" onClick={() => setActive(null)}>
          <button className="lightbox-close" onClick={() => setActive(null)}>✕</button>
          <div className="lightbox-content" onClick={(e) => e.stopPropagation()}>
            <div className="lightbox-image">
              <img src={active.image} alt={active.caption || active.stylist_name} />
            </div>
            <div className="lightbox-caption">
              <div className="name">{active.stylist_name}</div>
              {active.caption && <div className="title">{active.caption}</div>}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
