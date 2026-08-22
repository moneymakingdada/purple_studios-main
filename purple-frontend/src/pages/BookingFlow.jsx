import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { fetchServices, fetchStylists, fetchStylistSlots, fetchSalons } from "../api/catalog";
import { createBooking } from "../api/bookings";
import { useAuth } from "../context/AuthContext";


const STEPS = ["Service", "Stylist", "Date & time", "Confirm"];

export default function BookingFlow() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [step, setStep] = useState(0);
  const [services, setServices] = useState([]);
  const [stylists, setStylists] = useState([]);
  const [salon, setSalon] = useState(null);

  const [serviceId, setServiceId] = useState(location.state?.serviceId || null);
  const [stylistId, setStylistId] = useState(location.state?.stylistId || null);
  const [date, setDate] = useState(location.state?.date || "");
  const [time, setTime] = useState("");
  const [slots, setSlots] = useState([]);
  const [slotsLoading, setSlotsLoading] = useState(false);

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [confirmedBooking, setConfirmedBooking] = useState(null);

  const service = useMemo(() => services.find((s) => s.id === serviceId), [services, serviceId]);
  const stylist = useMemo(() => stylists.find((s) => s.id === stylistId), [stylists, stylistId]);

  useEffect(() => {
    fetchServices({ is_active: true }).then(setServices);
    fetchStylists({ is_accepting_bookings: true }).then(setStylists);
    fetchSalons().then((data) => setSalon(data[0] || null));
  }, []);

  useEffect(() => {
    if (step === 2 && stylistId && date && service) {
      setSlotsLoading(true);
      setTime("");
      fetchStylistSlots(stylistId, date, service.duration_minutes)
        .then((data) => setSlots(data.slots))
        .catch(() => setSlots([]))
        .finally(() => setSlotsLoading(false));
    }
  }, [step, stylistId, date, service]);

  function goNext() {
    setError("");
    setStep((s) => Math.min(s + 1, STEPS.length - 1));
  }
  function goBack() {
    setError("");
    setStep((s) => Math.max(s - 1, 0));
  }

  async function handleConfirm() {
    if (!user) {
      navigate("/login", { state: { from: { pathname: "/book" } } });
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      const booking = await createBooking({
        salon: salon.id,
        stylist: stylistId,
        service: serviceId,
        date,
        start_time: time,
        notes: "",
      });
      setConfirmedBooking(booking);
    } catch (err) {
      const data = err.response?.data;
      setError(data ? Object.values(data).flat().join(" ") : "Could not create booking. Please try another slot.");
    } finally {
      setSubmitting(false);
    }
  }

  if (confirmedBooking) {
    return (
      <div className="section booking-flow-wrap" style={{ maxWidth: 560 }}>
        <div className="card success-card">
          <div className="success-icon">✓</div>
          <h2 style={{ marginBottom: 10 }}>You're booked!</h2>
          <p style={{ color: "var(--muted)", marginBottom: 24 }}>
            {service?.name} with {stylist?.full_name} on {confirmedBooking.date} at {confirmedBooking.start_time}.
          </p>
          <button className="btn-primary" onClick={() => navigate("/dashboard")}>View my bookings</button>
        </div>
      </div>
    );
  }

  return (
    <div className="section booking-flow-wrap">
      <div className="progress">
        {STEPS.map((label, i) => (
          <div key={label} style={{ display: "contents" }}>
            <div className={`p-step ${i < step ? "done" : i === step ? "active" : ""}`}>
              <div className="p-circle">{i < step ? "✓" : i + 1}</div>
              <div className="p-label">{label}</div>
            </div>
            {i < STEPS.length - 1 && <div className={`p-line ${i < step ? "done" : ""}`} />}
          </div>
        ))}
      </div>

      <div className="card booking-flow-card">
        {error && <div className="form-banner-error">{error}</div>}

        {step === 0 && (
          <>
            <h2>Choose your service</h2>
            <div className="grid-2">
              {services.map((s) => (
                <div
                  key={s.id}
                  onClick={() => setServiceId(s.id)}
                  className={`option-tile ${serviceId === s.id ? "selected" : ""}`}
                >
                  <h4>{s.name}</h4>
                  <p>{s.duration_minutes} min</p>
                  <div className="price">GHS {s.price}</div>
                </div>
              ))}
            </div>
          </>
        )}

        {step === 1 && (
          <>
            <h2>Choose your stylist</h2>
            <div className="grid-3">
              {stylists.map((s) => (
                <div
                  key={s.id}
                  onClick={() => setStylistId(s.id)}
                  className={`option-tile stylist-tile ${stylistId === s.id ? "selected" : ""}`}
                >
                  <div className="stylist-tile-avatar">
                    {s.avatar && <img src={s.avatar} alt={s.full_name} />}
                  </div>
                  <h4>{s.full_name}</h4>
                  <p>{s.title}</p>
                </div>
              ))}
            </div>
          </>
        )}

        {step === 2 && (
          <>
            <h2>When works for you?</h2>
            <div className="field">
              <label>Date</label>
              <input type="date" value={date} onChange={(e) => setDate(e.target.value)} min={new Date().toISOString().slice(0, 10)} />
            </div>
            {date && (
              <div style={{ marginTop: 18 }}>
                <label className="slots-label">Available times</label>
                {slotsLoading && <p className="loading-text">Checking availability…</p>}
                {!slotsLoading && slots.length === 0 && <p className="empty-text">No slots available this day — try another date.</p>}
                <div className="slots-wrap">
                  {slots.map((t) => (
                    <div
                      key={t}
                      onClick={() => setTime(t)}
                      className={`slot-tile ${time === t ? "selected" : ""}`}
                    >
                      {t}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {step === 3 && (
          <>
            <h2>Confirm your booking</h2>
            <SummaryRow label="Service" value={service?.name} />
            <SummaryRow label="Stylist" value={stylist?.full_name} />
            <SummaryRow label="Date" value={date} />
            <SummaryRow label="Time" value={time} />
            <div className="summary-total">
              <span>Total</span>
              <span style={{ color: "var(--violet)", fontWeight: 800 }}>GHS {service?.price}</span>
            </div>
            {!user && (
              <div className="form-banner-error" style={{ marginTop: 20 }}>
                You'll need to log in to confirm this booking.
              </div>
            )}
          </>
        )}

        <div className="booking-flow-actions">
          {step > 0 ? (
            <button className="btn-ghost" onClick={goBack}>← Back</button>
          ) : <span />}
          {step < STEPS.length - 1 ? (
            <button
              className="btn-primary"
              disabled={
                (step === 0 && !serviceId) ||
                (step === 1 && !stylistId) ||
                (step === 2 && !time)
              }
              onClick={goNext}
            >
              Continue
            </button>
          ) : (
            <button className="btn-primary" disabled={submitting} onClick={handleConfirm}>
              {submitting ? "Booking…" : user ? "Confirm booking" : "Log in to confirm"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function SummaryRow({ label, value }) {
  return (
    <div className="summary-row">
      <span>{label}</span>
      <span>{value || "—"}</span>
    </div>
  );
}
