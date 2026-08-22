import { useEffect, useState } from "react";
import { fetchFeaturedReviews } from "../api/bookings";
import Reveal from "./Reveal";


/** Top-rated client reviews — reused wherever social proof is useful (currently Landing). */
export default function FeaturedReviews() {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFeaturedReviews().then(setReviews).catch(() => setReviews([])).finally(() => setLoading(false));
  }, []);

  if (!loading && reviews.length === 0) return null;

  return (
    <div className="section">
      <div className="section-head">
        <span className="eyebrow">Client love</span>
        <h2>What Accra is saying</h2>
      </div>

      {loading ? (
        <div className="featured-reviews-grid">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="card skeleton-card" style={{ padding: 26 }}>
              <div className="skeleton skeleton-line w-40" />
              <div className="skeleton skeleton-line" />
              <div className="skeleton skeleton-line w-60" />
            </div>
          ))}
        </div>
      ) : (
        <Reveal stagger className="featured-reviews-grid">
          {reviews.map((r) => (
            <div key={r.id} className="card featured-review-card">
              <div className="stars">{"★".repeat(r.rating)}{"☆".repeat(5 - r.rating)}</div>
              <p className="quote">"{r.comment}"</p>
              <div className="by">{r.customer_first_name}</div>
              <div className="meta">{r.service_name} with {r.stylist_name}</div>
            </div>
          ))}
        </Reveal>
      )}
    </div>
  );
}
