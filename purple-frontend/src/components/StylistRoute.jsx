import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function StylistRoute({ children }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) return <div className="loading-text container">Loading…</div>;
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />;
  if (user.role !== "stylist") return <Navigate to="/dashboard" replace />;
  return children;
}
