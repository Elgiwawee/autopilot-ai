// src/pages/Login.jsx

import { useState } from "react";
import { useNavigate, useLocation ,Link } from "react-router-dom"; // ✅ add Link
import { login as loginApi } from "../api/auth.api";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const next = new URLSearchParams(location.search).get("next");

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    try {
      const res = await loginApi(form);
      await login(res.data.access);
      navigate(next || "/overview");
    } catch (err) {
      setError("Invalid credentials");
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center">

      {/* ✅ LOGO */}
      <img
        src="/logo.png"
        alt="Autopilot"
        className="h-16 mb-6"
      />

      <form
        onSubmit={handleSubmit}
        className="bg-panel border border-border p-8 rounded-lg w-96"
      >
        <h1 className="text-2xl font-semibold mb-6 text-center">
          Sign In
        </h1>

        {error && (
          <div className="mb-4 text-danger text-sm text-center">
            {error}
          </div>
        )}

        <input
          className="input mb-4 w-full"
          placeholder="Email"
          value={form.email}
          onChange={e =>
            setForm({ ...form, email: e.target.value })
          }
        />

        <input
          className="input mb-6 w-full"
          type="password"
          placeholder="Password"
          value={form.password}
          onChange={e =>
            setForm({ ...form, password: e.target.value })
          }
        />

        <button className="w-full bg-primary py-2 rounded-lg font-medium">
          Login
        </button>

        {/* ✅ SWITCH TO REGISTER */}
        <div className="mt-4 text-sm text-center text-muted">
          Don’t have an account?{" "}
          <Link to="/register" className="text-primary hover:underline">
            Register
          </Link>
        </div>

      </form>
    </div>
  );
}