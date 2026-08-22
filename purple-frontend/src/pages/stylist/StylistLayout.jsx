import { NavLink, Outlet } from "react-router-dom";

export default function StylistLayout() {
  return (
    <div>
      <div className="portal-subnav">
        <div className="container portal-subnav-inner">
          <PortalTab to="/portal" end>Overview</PortalTab>
          <PortalTab to="/portal/calendar">Calendar</PortalTab>
          <PortalTab to="/portal/availability">Availability</PortalTab>
        </div>
      </div>
      <Outlet />
    </div>
  );
}

function PortalTab({ to, end, children }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) => `portal-tab ${isActive ? "active" : ""}`}
    >
      {children}
    </NavLink>
  );
}
