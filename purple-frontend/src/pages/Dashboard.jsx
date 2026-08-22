import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { cancelBooking, fetchMyBookings, leaveReview } from "../api/bookings";
import { fetchSalons } from "../api/catalog";
import { useAuth } from "../context/AuthContext";

const STATUS_COLORS = {
  pending: "#B8912B",
  confirmed: "#1e8449",
  completed: "#6C2BD9",
  cancelled: "#8a7397",
  no_show: "#c0392b",
};

export default function Dashboard() {
  const { user } = useAuth();
  const [bookings, setBookings] = useState([]);
  const [salons, setSalons] = useState([]);
  const [loading, setLoading] = useState(true);

  function load() {
    setLoading(true);
    fetchMyBookings()
      .then(setBookings)
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
    fetchSalons()
      .then(setSalons)
      .catch(() => setSalons([]));
  }, []);

  async function handleCancel(id) {
    await cancelBooking(id);
    load();
  }

  const completedNeedingReview = bookings.filter(
    (b) => b.status === "completed" && !b.review,
  );
  const myReviews = bookings.filter((b) => b.review);

  return (
    <>
      {/* HERO */}
      <section className="dashboard-hero">
        <div className="container split-hero">
          <div>
            <span className="eyebrow">Your Purple account</span>
            <h1>Welcome back, {user?.first_name || user?.username}.</h1>
            <p>
              Manage your appointments, leave reviews for your stylist, and find
              your nearest studio — all in one place.
            </p>
            <Link to="/book" className="btn-primary">
              Book a new appointment
            </Link>
          </div>
          <div className="dashboard-hero-image">
            <img
              src="https://images.unsplash.com/photo-1560066984-138dadb4c035?q=80&w=800&auto=format&fit=crop"
              alt="Purple studio"
            />
          </div>
        </div>
      </section>

      {/* UPCOMING BOOKINGS */}
      <div className="section">
        <div className="section-head">
          <span className="eyebrow">Your appointments</span>
          <h2>What's coming up</h2>
        </div>

        {loading && <p className="loading-text">Loading your bookings…</p>}
        {!loading && bookings.length === 0 && (
          <p className="empty-text">
            No bookings yet — book your first Purple appointment above.
          </p>
        )}

        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {bookings.map((b) => (
            <div key={b.id} className="card booking-row">
              <div>
                <h4>{b.service_name}</h4>
                <p>
                  with {b.stylist_name} · {b.date} at {b.start_time} ·{" "}
                  {b.salon_name}
                </p>
              </div>
              <div className="booking-row-actions">
                <span
                  style={{
                    color: STATUS_COLORS[b.status] || "var(--muted)",
                    fontWeight: 700,
                    fontSize: "0.8rem",
                    textTransform: "capitalize",
                  }}
                >
                  {b.status.replace("_", " ")}
                </span>
                <span className="booking-row-price">GHS {b.price}</span>
                {(b.status === "pending" || b.status === "confirmed") && (
                  <button
                    className="btn-ghost btn-sm"
                    onClick={() => handleCancel(b.id)}
                  >
                    Cancel
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* REVIEWS */}
      <div className="section">
        <div className="section-head">
          <span className="eyebrow">Your reviews</span>
          <h2>Rate your recent visits</h2>
        </div>

        {completedNeedingReview.length === 0 && myReviews.length === 0 && (
          <p className="empty-text">
            Once you complete an appointment, you can leave a review for your
            stylist here.
          </p>
        )}

        {completedNeedingReview.length > 0 && (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 14,
              marginBottom: 24,
            }}
          >
            {completedNeedingReview.map((b) => (
              <ReviewForm key={b.id} booking={b} onSubmitted={load} />
            ))}
          </div>
        )}

        {myReviews.length > 0 && (
          <div className="grid-auto">
            {myReviews.map((b) => (
              <div key={b.id} className="card review-card">
                <div className="stars">
                  {"★".repeat(b.review.rating)}
                  {"☆".repeat(5 - b.review.rating)}
                </div>
                <p>{b.review.comment || "No comment left."}</p>
                <p className="meta">
                  {b.service_name} with {b.stylist_name}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}

function ReviewForm({ booking, onSubmitted }) {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await leaveReview(booking.id, rating, comment);
      onSubmitted();
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card review-form">
      <div className="review-form-info">
        <h4>{booking.service_name}</h4>
        <p>
          with {booking.stylist_name} · {booking.date}
        </p>
      </div>
      <div className="review-form-stars">
        {[1, 2, 3, 4, 5].map((n) => (
          <span
            key={n}
            onClick={() => setRating(n)}
            style={{ color: n <= rating ? "var(--gold)" : "#E4D5F2" }}
          >
            ★
          </span>
        ))}
      </div>
      <input
        className="review-form-comment"
        placeholder="Add a comment (optional)"
        value={comment}
        onChange={(e) => setComment(e.target.value)}
      />
      <button className="btn-primary btn-sm" disabled={submitting}>
        {submitting ? "Saving…" : "Submit review"}
      </button>
    </form>
  );
}
