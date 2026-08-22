import { useEffect, useState } from "react";
import { fetchSalons } from "../api/catalog";

/**
 * "Our studios" block — reused on Landing and Dashboard.
 * Fetches its own salon data, so any page that renders <Locations />
 * automatically gets the list without needing to wire up state itself.
 */
export default function Locations() {
  const [salons, setSalons] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSalons()
      .then(setSalons)
      .catch(() => setSalons([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="section" style={{ paddingBottom: 100 }}>
      <div className="section-head">
        <span className="eyebrow">Find us</span>
        <h2>Our studios</h2>
      </div>
      {loading ? (
        <p className="loading-text">Loading studio locations…</p>
      ) : salons.length === 0 ? (
        <p className="empty-text">No studio locations available right now.</p>
      ) : (
        <div className="locations-grid">
          {salons.map((s) => (
            <div key={s.id} className="card location-card">
              <h4>{s.name}</h4>
              <p>{s.address}</p>
              <p>{s.city}, {s.region.replace("_", " ")}</p>
              <p>Open {s.opens_at?.slice(0, 5)} – {s.closes_at?.slice(0, 5)}</p>
              {s.phone && <p className="phone">{s.phone}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
