import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { fetchService } from "../api/catalog";
import { getServiceImage } from "../utils/serviceImages";

export default function ServiceDetail() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [service, setService] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchService(slug)
      .then(setService)
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) return <p className="loading-text container">Loading…</p>;
  if (!service)
    return <p className="empty-text container">Service not found.</p>;

  const heroImage = getServiceImage(service);

  return (
    <>
      <section className="service-detail-hero">
        <div className="container">
          <Link to="/services" className="service-detail-crumb">
            ← Back to services
          </Link>
          <div className="split-hero even">
            <div>
              <span className="eyebrow">{service.category_name}</span>
              <h1>{service.name}</h1>
              <p>
                {service.description ||
                  "A signature Purple treatment, delivered by a certified specialist."}
              </p>
            </div>
            <div className="service-detail-hero-image">
              <img src={heroImage} alt={service.name} />
            </div>
          </div>
        </div>
      </section>

      <div className="container service-detail-pricebar">
        <div className="card">
          <div className="price-item">
            <h4>Price</h4>
            <p>GHS {service.price}</p>
          </div>
          <div className="price-item">
            <h4>Duration</h4>
            <p>{service.duration_minutes} min</p>
          </div>
          <div className="price-item">
            <h4>For</h4>
            <p>{service.audience}</p>
          </div>
          <button
            className="btn-primary"
            onClick={() =>
              navigate("/book", { state: { serviceId: service.id } })
            }
          >
            Book this service
          </button>
        </div>
      </div>

      <div className="section">
        <div className="section-head">
          <span className="eyebrow">Gallery</span>
          <h2>What this looks like</h2>
        </div>
        <div className="grid-3">
          <div className="service-detail-gallery-item">
            <img src={heroImage} alt="" />
          </div>
          <div className="service-detail-gallery-item">
            <img
              src="https://images.unsplash.com/photo-1522337660859-02fbefca4702?q=80&w=500&auto=format&fit=crop"
              alt=""
            />
          </div>
          <div className="service-detail-gallery-item">
            <img
              src="https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?q=80&w=500&auto=format&fit=crop"
              alt=""
            />
          </div>
        </div>
      </div>
    </>
  );
}
