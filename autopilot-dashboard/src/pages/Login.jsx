 //src/pages/Login.jsx`

 
import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Eye, EyeOff, Loader2, Sparkles, ShieldCheck, ArrowRight } from "lucide-react";
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
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [successMessage, setSuccessMessage] = useState(location.state?.message || "");

  useEffect(() => {
    if (location.state?.message) {
      setSuccessMessage(location.state.message);
      window.history.replaceState({}, document.title);
    }
  }, [location.state]);

  const emailHint = useMemo(() => {
    if (!form.email) return "Use your work email";
    if (!form.email.includes("@")) return "Enter a valid email address";
    return "Looks good";
  }, [form.email]);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSuccessMessage("");

    if (loading) return;

    if (!form.email.trim()) {
      setError("Email address is required.");
      return;
    }

    if (!form.password) {
      setError("Password is required.");
      return;
    }

    try {
      setLoading(true);
      const res = await loginApi(form);

      localStorage.setItem("token", res.data.access);
      localStorage.setItem("refresh", res.data.refresh);

      const success = await login(res.data.access);

      if (success) {
        navigate(next || "/overview");
      } else {
        setError("Login failed. Please try again.");
      }
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.response?.data?.message ||
          "Invalid email or password. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  const inputBase =
    "w-full rounded-2xl border border-border bg-background px-4 py-3.5 text-sm outline-none transition placeholder:text-muted-foreground/70 focus:border-primary focus:ring-4 focus:ring-primary/10 disabled:cursor-not-allowed disabled:opacity-70";

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-6xl grid lg:grid-cols-2 overflow-hidden rounded-[2rem] border border-border bg-card shadow-2xl shadow-black/5">
        {/* LEFT PANEL */}
        <div className="relative hidden lg:flex flex-col justify-between p-10 xl:p-12 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.16),transparent_38%),linear-gradient(180deg,rgba(255,255,255,0.02),rgba(255,255,255,0))] border-r border-border">
          <div className="absolute inset-0 opacity-60 bg-[linear-gradient(to_bottom_right,transparent_0%,transparent_42%,rgba(59,130,246,0.06)_42%,rgba(59,130,246,0.06)_58%,transparent_58%,transparent_100%)] bg-[length:24px_24px]" />

          <div className="relative z-10 space-y-8">
            <div className="flex items-center gap-3">
              <div className="h-12 w-12 rounded-2xl bg-primary/10 flex items-center justify-center text-primary">
                <Sparkles className="h-6 w-6" />
              </div>
              <div>
                <div className="text-xl font-semibold tracking-tight">Autopilot</div>
                <div className="text-sm text-muted-foreground">Welcome back</div>
              </div>
            </div>

            <div className="space-y-5 max-w-md">
              <span className="inline-flex items-center gap-2 rounded-full border border-border bg-background/70 px-3 py-1 text-xs font-medium text-muted-foreground shadow-sm">
                <ShieldCheck className="h-3.5 w-3.5 text-primary" />
                Secure access for your team
              </span>

              <h1 className="text-4xl xl:text-5xl font-semibold tracking-tight leading-tight">
                Sign in to review insights, approvals, and savings in one place.
              </h1>

              <p className="text-base xl:text-lg text-muted-foreground leading-8 max-w-md">
                Continue where you left off and get back to the metrics that matter.
              </p>
            </div>
          </div>

          <div className="relative z-10 grid gap-4">
            {[
              "Fast access to your organization dashboard",
              "Protected login with clear feedback",
              "Built for secure cloud operations",
            ].map((item) => (
              <div key={item} className="flex items-center gap-3 rounded-2xl border border-border bg-background/70 px-4 py-3 shadow-sm backdrop-blur">
                <div className="h-9 w-9 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-500">
                  <ShieldCheck className="h-4.5 w-4.5" />
                </div>
                <span className="text-sm font-medium">{item}</span>
              </div>
            ))}
          </div>
        </div>

        {/* RIGHT PANEL */}
        <div className="p-6 sm:p-8 lg:p-10 xl:p-12 flex items-center justify-center">
          <form onSubmit={handleSubmit} className="w-full max-w-md space-y-6">
            <div className="text-center space-y-3">
              <div className="mx-auto h-16 w-16 rounded-3xl border border-border bg-primary/10 flex items-center justify-center lg:hidden">
                <img src="/logo.png" alt="Autopilot" className="h-10 w-10 object-contain" />
              </div>
              <div className="hidden lg:block">
                <img src="/logo.png" alt="Autopilot" className="h-14 mx-auto object-contain" />
              </div>
              <h2 className="text-3xl font-semibold tracking-tight">Sign in</h2>
              <p className="text-sm sm:text-base text-muted-foreground leading-6">
                Access your workspace and continue managing your cloud savings.
              </p>
            </div>

            {successMessage && (
              <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-700">
                {successMessage}
              </div>
            )}

            {error && (
              <div className="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-600">
                {error}
              </div>
            )}

            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Work email</label>
                <input
                  className={inputBase}
                  placeholder="name@company.com"
                  type="email"
                  autoComplete="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                />
                <div className="text-xs text-muted-foreground">{emailHint}</div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Password</label>
                <div className="relative">
                  <input
                    className={`${inputBase} pr-12`}
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    autoComplete="current-password"
                    value={form.password}
                    onChange={(e) => setForm({ ...form, password: e.target.value })}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    className="absolute inset-y-0 right-0 flex items-center px-4 text-muted-foreground hover:text-foreground transition"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full inline-flex items-center justify-center gap-2 rounded-2xl bg-primary px-6 py-3.5 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/20 transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-70 disabled:hover:translate-y-0"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Signing you in...
                </>
              ) : (
                <>
                  Sign in <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>

            <div className="text-sm text-center text-muted-foreground">
              Don’t have an account?{" "}
              <Link to="/register" className="font-medium text-primary hover:underline">
                Create one
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

