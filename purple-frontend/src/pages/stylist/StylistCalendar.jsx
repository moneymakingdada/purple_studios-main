import { useEffect, useMemo, useState } from "react";
import { cancelBooking, completeBooking, confirmBooking, fetchMyBookings } from "../../api/bookings";

const STATUS_COLORS = {
  pending: "#B8912B",
  confirmed: "#1e8449",
  completed: "#6C2BD9",
  cancelled: "#8a7397",
  no_show: "#c0392b",
};

function startOfWeek(date) {
  const d = new Date(date);
  const day = (d.getDay() + 6) % 7; // Monday = 0
  d.setDate(d.getDate() - day);
  d.setHours(0, 0, 0, 0);
  return d;
}

function toISODate(d) {
  return d.toISOString().slice(0, 10);
}

export default function StylistCalendar() {
  const [weekStart, setWeekStart] = useState(startOfWeek(new Date()));
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  const days = useMemo(() => {
    return Array.from({ length: 7 }, (_, i) => {
      const d = new Date(weekStart);
      d.setDate(d.getDate() + i);
      return d;
    });
  }, [weekStart]);

  function load() {
    setLoading(true);
    fetchMyBookings().then(setBookings).finally(() => setLoading(false));
  }

  useEffect(load, []);

  async function handleAction(actionFn, id) {
    await actionFn(id);
    load();
  }

  function bookingsForDay(day) {
    const iso = toISODate(day);
    return bookings
      .filter((b) => b.date === iso)
      .sort((a, b) => a.start_time.localeCompare(b.start_time));
  }

  return (
    <div className="section" style={{ paddingBottom: 100 }}>
      <div className="section-head calendar-head">
        <div>
          <span className="eyebrow">Your week</span>
          <h2>
            {weekStart.toLocaleDateString(undefined, { month: "short", day: "numeric" })} –{" "}
            {days[6].toLocaleDateString(undefined, { month: "short", day: "numeric" })}
          </h2>
        </div>
        <div className="calendar-nav">
          <button className="btn-ghost btn-sm" onClick={() => setWeekStart((d) => { const nd = new Date(d); nd.setDate(nd.getDate() - 7); return nd; })}>← Prev</button>
          <button className="btn-ghost btn-sm" onClick={() => setWeekStart(startOfWeek(new Date()))}>Today</button>
          <button className="btn-ghost btn-sm" onClick={() => setWeekStart((d) => { const nd = new Date(d); nd.setDate(nd.getDate() + 7); return nd; })}>Next →</button>
        </div>
      </div>

      {loading && <p className="loading-text">Loading your calendar…</p>}

      <div className="week-grid">
        {days.map((day) => {
          const dayBookings = bookingsForDay(day);
          const isToday = toISODate(day) === toISODate(new Date());
          return (
            <div key={day.toISOString()} className="calendar-day-col">
              <div className={`calendar-day-header ${isToday ? "today" : ""}`}>
                <div className="dow">{day.toLocaleDateString(undefined, { weekday: "short" })}</div>
                <div className="dnum">{day.getDate()}</div>
              </div>
              {dayBookings.length === 0 && <div className="calendar-empty">—</div>}
              {dayBookings.map((b) => (
                <div key={b.id} className="card calendar-booking" style={{ borderLeft: `3px solid ${STATUS_COLORS[b.status]}` }}>
                  <div className="time">{b.start_time?.slice(0, 5)}</div>
                  <div className="service">{b.service_name}</div>
                  <div className="customer">{b.customer_name}</div>
                  <div className="calendar-booking-actions">
                    {b.status === "pending" && (
                      <button className="btn-primary" onClick={() => handleAction(confirmBooking, b.id)}>Confirm</button>
                    )}
                    {b.status === "confirmed" && (
                      <button className="btn-primary" onClick={() => handleAction(completeBooking, b.id)}>Complete</button>
                    )}
                    {(b.status === "pending" || b.status === "confirmed") && (
                      <button className="btn-ghost" onClick={() => handleAction(cancelBooking, b.id)}>Cancel</button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          );
        })}
      </div>
    </div>
  );
}
