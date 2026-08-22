import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: "",
    username: "",
    first_name: "",
    last_name: "",
    phone: "",
    password: "",
    password_confirm: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function update(field) {
    return (e) => setForm({ ...form, [field]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(form);
      navigate("/dashboard");
    } catch (err) {
      const data = err.response?.data;
      const message = data
        ? Object.values(data).flat().join(" ")
        : "Something went wrong. Please try again.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-wrap">
      <div className="auth-card wide">
        <h1>Join Purple</h1>
        <p className="sub">Create an account to start booking.</p>
        {error && <div className="form-banner-error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="auth-name-row">
            <div className="field">
              <label>First name</label>
              <input
                required
                value={form.first_name}
                onChange={update("first_name")}
              />
            </div>
            <div className="field">
              <label>Last name</label>
              <input
                required
                value={form.last_name}
                onChange={update("last_name")}
              />
            </div>
          </div>
          <div className="field">
            <label>Username</label>
            <input
              required
              value={form.username}
              onChange={update("username")}
            />
          </div>
          <div className="field">
            <label>Email</label>
            <input
              type="email"
              required
              value={form.email}
              onChange={update("email")}
            />
          </div>
          <div className="field">
            <label>Phone (e.g. +233241234567)</label>
            <input
              value={form.phone}
              onChange={update("phone")}
              placeholder="+233241234567"
            />
          </div>
          <div className="field">
            <label>Password</label>
            <input
              type="password"
              required
              value={form.password}
              onChange={update("password")}
            />
          </div>
          <div className="field">
            <label>Confirm password</label>
            <input
              type="password"
              required
              value={form.password_confirm}
              onChange={update("password_confirm")}
            />
          </div>
          <button className="btn-primary btn-block" disabled={loading}>
            {loading ? "Creating account…" : "Create account"}
          </button>
        </form>
        <div className="auth-switch">
          Already have an account? <Link to="/login">Log in</Link>
        </div>
      </div>
    </div>
  );
}
