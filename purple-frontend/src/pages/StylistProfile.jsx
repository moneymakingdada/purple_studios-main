import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { fetchStylist } from "../api/catalog";

export default function StylistProfile() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [stylist, setStylist] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStylist(id)
      .then(setStylist)
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <p className="loading-text container">Loading…</p>;
  if (!stylist)
    return <p className="empty-text container">Stylist not found.</p>;

  return (
    <div className="section" style={{ paddingBottom: 100 }}>
      <Link to="/stylists" className="stylist-profile-crumb">
        ← Back to stylists
      </Link>

      <div className="split-hero narrow" style={{ marginTop: 20 }}>
        <div className="stylist-profile-avatar">
          {stylist.avatar && (
            <img src={stylist.avatar} alt={stylist.full_name} />
          )}
        </div>
        <div className="stylist-profile-info">
          <span className="eyebrow">{stylist.title}</span>
          <h1>{stylist.full_name}</h1>
          <p className="meta">
            {stylist.years_experience} years experience · ★{" "}
            {stylist.average_rating || "New"}
          </p>
          <p className="bio">
            {stylist.bio || "A Purple specialist ready to take care of you."}
          </p>

          <div className="stylist-profile-tags">
            {stylist.specialties.map((sp) => (
              <span key={sp.id} className="pill">
                {sp.name}
              </span>
            ))}
          </div>

          <button
            className="btn-primary"
            onClick={() =>
              navigate("/book", { state: { stylistId: stylist.id } })
            }
          >
            Book with {stylist.full_name?.split(" ")[0]}
          </button>
        </div>
      </div>

      {stylist.portfolio?.length > 0 && (
        <div className="stylist-profile-portfolio">
          <h3>Portfolio</h3>
          <div className="stylist-profile-portfolio-grid">
            {stylist.portfolio.map((p) => (
              <div key={p.id} className="stylist-profile-portfolio-item">
                <img src={p.image} alt={p.caption} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
