import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { fetchServices, fetchStylists, fetchSalons } from "../api/catalog";
import { getServiceImage } from "../utils/serviceImages";
import AboutUs from "../components/AboutUs";
import Locations from "../components/Locations";
import FeaturedReviews from "../components/FeaturedReviews";
import Reveal from "../components/Reveal";
import FadeImage from "../components/FadeImage";

export default function Landing() {
  const navigate = useNavigate();
  const [services, setServices] = useState([]);
  const [stylists, setStylists] = useState([]);
  const [salons, setSalons] = useState([]);

  const [serviceId, setServiceId] = useState("");
  const [stylistId, setStylistId] = useState("");
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");

  useEffect(() => {
    fetchServices().then(setServices).catch(() => setServices([]));
    fetchStylists().then(setStylists).catch(() => setStylists([]));
    fetchSalons().then(setSalons).catch(() => setSalons([]));
  }, []);

  function handleCheckAvailability(e) {
    e.preventDefault();
    navigate("/book", {
      state: {
        serviceId: serviceId || undefined,
        stylistId: stylistId || undefined,
        date: date || undefined,
        time: time || undefined,
      },
    });
  }

  return (
    <>
      <section className="landing-hero">
        <div className="container split-hero">
          <div>
            <span className="eyebrow">Accra's most booked beauty studio</span>
            <h1>
              Look extraordinary. <em>Feel royal.</em>
            </h1>
            <p>
              From sharp fades to fresh lashes, gel pedicures to full glam — Purple brings every beauty ritual under one roof, booked in under a minute.
            </p>
            <div className="landing-hero-actions">
              <a href="#book" className="btn-primary">Book an appointment</a>
              <Link to="/services" className="btn-ghost on-dark">Explore services</Link>
            </div>
          </div>
          <div className="landing-hero-image">
            <img src="https://images.unsplash.com/photo-1560066984-138dadb4c035?q=80&w=900&auto=format&fit=crop" alt="Purple salon interior" />
          </div>
        </div>
      </section>

      {/* RIBBON + FLOATING BOOKING */}
      <div className="ribbon-wrap">
        <div className="ribbon">
          <div className="ribbon-track">
            <span>Men's Cuts</span>
            <span>Women's Styling</span>
            <span>Lash Extensions</span>
            <span>Pedicure &amp; Manicure</span>
            <span>Bridal Glam</span>
            <span>Men's Cuts</span>
            <span>Women's Styling</span>
            <span>Lash Extensions</span>
          </div>
        </div>
      </div>

      <div className="booking-float" id="book">
        <form className="booking-card" onSubmit={handleCheckAvailability}>
          <div className="field">
            <label>Service</label>
            <select value={serviceId} onChange={(e) => setServiceId(e.target.value)}>
              <option value="">Any service</option>
              {services.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>

          <div className="field">
            <label>Stylist</label>
            <select value={stylistId} onChange={(e) => setStylistId(e.target.value)}>
              <option value="">Any available</option>
              {stylists.map((s) => (
                <option key={s.id} value={s.id}>{s.full_name}</option>
              ))}
            </select>
          </div>

          <div className="field">
            <label>Date</label>
            <input type="date" value={date} min={new Date().toISOString().slice(0, 10)} onChange={(e) => setDate(e.target.value)} />
          </div>

          <div className="field">
            <label>Time</label>
            <select value={time} onChange={(e) => setTime(e.target.value)}>
              <option value="">Any time</option>
              <option>10:00 AM</option>
              <option>1:00 PM</option>
              <option>4:00 PM</option>
              <option>6:30 PM</option>
            </select>
          </div>

          <button type="submit" className="btn-primary">Check availability</button>
        </form>
      </div>

      <section className="section">
              <div className="section-head">
                <span className="eyebrow">What we do</span>
                <h2>Every service, one purple standard.</h2>
              </div>
              {services.length === 0 ? (
                <div className="grid-4">
                  {Array.from({ length: 4 }).map((_, i) => (
                    <div key={i} className="card skeleton-card">
                      <div className="skeleton skeleton-thumb" />
                      <div className="skeleton-card-body">
                        <div className="skeleton skeleton-line w-40" />
                        <div className="skeleton skeleton-line w-60" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <Reveal stagger className="grid-4">
                  {services.slice(0, 4).map((s) => (
                    <Link to={`/services/${s.slug}`} key={s.id} className="card landing-service-card">
                      <div className="landing-service-thumb">
                        <FadeImage src={getServiceImage(s)} alt={s.name} />
                      </div>
                      <div className="landing-service-body">
                        <span className="eyebrow">{s.category_name}</span>
                        <h3>{s.name}</h3>
                        <p>GHS {s.price} · {s.duration_minutes} min</p>
                      </div>
                    </Link>
                  ))}
                </Reveal>
              )}
            </section>
      
            <FeaturedReviews />
      
            <AboutUs />


      <div className="landing-cta-banner">
        <h2>Your seat is one tap away.</h2>
        <p>Pick a service, a stylist, a time. Purple holds the rest.</p>
        <a href="#book" className="btn-primary">Book your slot</a>
      </div>


       <Locations />
    </>
  );
}
