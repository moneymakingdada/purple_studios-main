import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  function handleLogout() {
    setOpen(false);
    logout();
    navigate("/");
  }

  function close() {
    setOpen(false);
  }

  return (
    <nav className="site-nav">
      <Link to="/" className="logo" onClick={close}>Purple<span>.</span></Link>

      <button className="nav-toggle" onClick={() => setOpen((o) => !o)} aria-label="Toggle menu">
        {open ? "✕" : "☰"}
      </button>

      <div className={`nav-links ${open ? "open" : ""}`}>
        <NavLink to="/services" onClick={close}>Services</NavLink>
        <NavLink to="/stylists" onClick={close}>Stylists</NavLink>
        <NavLink to="/gallery" onClick={close}>Gallery</NavLink>
        {user && user.role === "stylist" && <NavLink to="/portal" onClick={close}>Stylist portal</NavLink>}
        {user && user.role !== "stylist" && <NavLink to="/dashboard" onClick={close}>My bookings</NavLink>}
        {user ? (
          <>
            <span className="nav-user" style={{ color: "#D9C7EA", fontSize: "0.85rem", padding: "16px 6%" }}>
              Hi, {user.first_name || user.username}
            </span>
            <button className="btn-ghost on-dark btn-sm" onClick={handleLogout}>Log out</button>
          </>
        ) : (
          <>
            <NavLink to="/login" onClick={close}>Log in</NavLink>
            <NavLink to="/book" className="nav-cta" onClick={close}>Book now</NavLink>
          </>
        )}
      </div>
    </nav>
  );
}
