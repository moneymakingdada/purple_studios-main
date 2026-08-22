import { useEffect, useState } from "react";
import { cancelBooking, completeBooking, confirmBooking, fetchMyBookings } from "../../api/bookings";
import { fetchBookingStats } from "../../api/stylistPortal";
import { useAuth } from "../../context/AuthContext";

const STATUS_COLORS = {
  pending: "#B8912B",
  confirmed: "#1e8449",
  completed: "#6C2BD9",
  cancelled: "#8a7397",
  no_show: "#c0392b",
};

export default function StylistOverview() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [todayBookings, setTodayBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  const today = new Date().toISOString().slice(0, 10);

  function load() {
    setLoading(true);
    Promise.all([
      fetchBookingStats(),
      fetchMyBookings({ date: today }),
    ])
      .then(([statsData, bookings]) => {
        setStats(statsData);
        setTodayBookings(bookings);
      })
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  async function handleAction(actionFn, id) {
    await actionFn(id);
    load();
  }

  return (
    <>
      <section className="stylist-overview-hero">
        <div className="container">
          <span className="eyebrow">Stylist portal</span>
          <h1>Hey {user?.first_name || user?.username}, here's your day.</h1>
          <p>Track your bookings, revenue, and schedule from one place.</p>
        </div>
      </section>

      <div className="section">
        {loading ? (
          <p className="loading-text">Loading your stats…</p>
        ) : (
          <div className="grid-4" style={{ marginBottom: 50 }}>
            <StatCard label="Today" count={stats.today.count} revenue={stats.today.revenue} />
            <StatCard label="This week" count={stats.this_week.count} revenue={stats.this_week.revenue} />
            <StatCard label="This month" count={stats.this_month.count} revenue={stats.this_month.revenue} />
            <div className="card stat-card">
              <div className="stat-card-label">Upcoming</div>
              <div className="stat-card-value">{stats.upcoming_count}</div>
              <div className="stat-card-sub">appointments booked ahead</div>
            </div>
          </div>
        )}

        <div className="section-head">
          <span className="eyebrow">Today's schedule</span>
          <h2>{new Date().toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" })}</h2>
        </div>

        {!loading && todayBookings.length === 0 && <p className="empty-text">No appointments today.</p>}

        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {todayBookings.map((b) => (
            <div key={b.id} className="card today-row">
              <div>
                <h4>{b.start_time?.slice(0, 5)} · {b.service_name}</h4>
                <p>{b.customer_name}</p>
              </div>
              <div className="today-row-actions">
                <span style={{ color: STATUS_COLORS[b.status], fontWeight: 700, fontSize: "0.78rem", textTransform: "capitalize" }}>
                  {b.status.replace("_", " ")}
                </span>
                {b.status === "pending" && (
                  <button className="btn-primary btn-sm" onClick={() => handleAction(confirmBooking, b.id)}>Confirm</button>
                )}
                {b.status === "confirmed" && (
                  <button className="btn-primary btn-sm" onClick={() => handleAction(completeBooking, b.id)}>Mark complete</button>
                )}
                {(b.status === "pending" || b.status === "confirmed") && (
                  <button className="btn-ghost btn-sm" onClick={() => handleAction(cancelBooking, b.id)}>Cancel</button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

function StatCard({ label, count, revenue }) {
  return (
    <div className="card stat-card">
      <div className="stat-card-label">{label}</div>
      <div className="stat-card-value">{count}</div>
      <div className="stat-card-sub">GHS {revenue.toFixed(2)} revenue</div>
    </div>
  );
}
