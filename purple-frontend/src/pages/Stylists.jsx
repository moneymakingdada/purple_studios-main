import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchStylists } from "../api/catalog";
import Reveal from "../components/Reveal";
import FadeImage from "../components/FadeImage";


export default function Stylists() {
  const [stylists, setStylists] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStylists().then(setStylists).finally(() => setLoading(false));
  }, []);

  return (
    <div className="section" style={{ paddingBottom: 100 }}>
      <div className="section-head">
        <span className="eyebrow">Meet the team</span>
        <h2>Purple's master stylists</h2>
      </div>
      {loading && (
        <div className="stylists-grid">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="card skeleton-card" style={{ padding: 24 }}>
              <div className="skeleton" style={{ width: 64, height: 64, borderRadius: "50%", marginBottom: 14 }} />
              <div className="skeleton skeleton-line w-60" />
              <div className="skeleton skeleton-line w-40" />
            </div>
          ))}
        </div>
      )}
      {!loading && stylists.length === 0 && <p className="empty-text">No stylists found yet.</p>}
      <Reveal stagger className="stylists-grid">
        {stylists.map((s) => (
          <Link to={`/stylists/${s.id}`} key={s.id} className="card stylist-card">
            <div className="stylist-card-avatar">
              {s.avatar && <FadeImage src={s.avatar} alt={s.full_name} />}
            </div>
            <h4>{s.full_name}</h4>
            <p>{s.title}</p>
            <div className="stylist-card-meta">
              <span>★ {s.average_rating || "New"}</span>
              <span>{s.years_experience} yrs</span>
            </div>
          </Link>
        ))}
      </Reveal>
    </div>
  );
}
