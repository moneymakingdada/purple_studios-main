import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchCategories } from "../api/catalog";
import { getServiceImage } from "../utils/serviceImages";
import Reveal from "../components/Reveal";
import FadeImage from "../components/FadeImage";


export default function Services() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCategories()
      .then(setCategories)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="section" style={{ paddingBottom: 100 }}>
      <div className="section-head">
        <span className="eyebrow">Our menu</span>
        <h2>Every service, one purple standard.</h2>
      </div>

      {loading && (
        <div className="services-category-grid">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="card skeleton-card">
              <div className="skeleton skeleton-thumb" />
              <div className="skeleton-card-body">
                <div className="skeleton skeleton-line w-60" />
                <div className="skeleton skeleton-line w-40" />
              </div>
            </div>
          ))}
        </div>
      )}
      {!loading && categories.length === 0 && (
        <p className="empty-text">No services found. Make sure the Django API is running and seeded (`python manage.py seed_demo`).</p>
      )}

      {categories.map((cat) => (
        <div key={cat.id} className="services-category">
          <h3>{cat.name}</h3>
          <Reveal stagger className="services-category-grid">
            {cat.services.map((s) => (
              <Link to={`/services/${s.slug}`} key={s.id} className="card service-card">
                <div className="service-card-thumb">
                  <FadeImage src={getServiceImage(s)} alt={s.name} />
                </div>
                <div className="service-card-body">
                  <h4>{s.name}</h4>
                  <p>{s.duration_minutes} min · {s.audience}</p>
                  <div className="service-card-price">GHS {s.price}</div>
                </div>
              </Link>
            ))}
          </Reveal>
        </div>
      ))}
    </div>
  );
}
