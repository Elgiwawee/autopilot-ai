//src/pages/Register.jsx

import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff, Loader2, ShieldCheck, Sparkles } from "lucide-react";
import { register } from "../api/auth.api";

export default function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    organization_name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const passwordStrength = useMemo(() => {
    const value = form.password;
    if (!value) return { label: "Use 8+ characters", width: "0%", tone: "bg-muted" };

    let score = 0;
    if (value.length >= 8) score += 1;
    if (/[A-Z]/.test(value)) score += 1;
    if (/[0-9]/.test(value)) score += 1;
    if (/[^A-Za-z0-9]/.test(value)) score += 1;

    if (score <= 1) return { label: "Weak password", width: "25%", tone: "bg-red-500" };
    if (score === 2) return { label: "Fair password", width: "50%", tone: "bg-amber-500" };
    if (score === 3) return { label: "Strong password", width: "75%", tone: "bg-blue-500" };
    return { label: "Very strong", width: "100%", tone: "bg-emerald-500" };
  }, [form.password]);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    if (loading) return;

    if (!form.organization_name.trim()) {
      setError("Organization name is required.");
      return;
    }

    if (!form.email.trim()) {
      setError("Email address is required.");
      return;
    }

    if (form.password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      setLoading(true);
      await register({
        email: form.email,
        password: form.password,
        organization_name: form.organization_name,
      });

      navigate("/login", {
        state: {
          message: "Organization created successfully. Please sign in.",
        },
      });
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.response?.data?.message ||
          "Registration failed. Please check your details and try again."
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
                <div className="text-sm text-muted-foreground">Cloud optimization built for real teams</div>
              </div>
            </div>

            <div className="space-y-5 max-w-md">
              <span className="inline-flex items-center gap-2 rounded-full border border-border bg-background/70 px-3 py-1 text-xs font-medium text-muted-foreground shadow-sm">
                <ShieldCheck className="h-3.5 w-3.5 text-primary" />
                Trusted by cloud-first teams
              </span>

              <h1 className="text-4xl xl:text-5xl font-semibold tracking-tight leading-tight">
                Create your workspace and start tracking savings with confidence.
              </h1>

              <p className="text-base xl:text-lg text-muted-foreground leading-8 max-w-md">
                Set up your organization in minutes, connect your cloud accounts, and get a clear view of where savings can be unlocked safely.
              </p>
            </div>
          </div>

          <div className="relative z-10 grid gap-4">
            {[
              "Secure onboarding with least-privilege access",
              "Policy-based controls for every action",
              "Audit-ready activity tracking from day one",
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
              <h2 className="text-3xl font-semibold tracking-tight">Create your organization</h2>
              <p className="text-sm sm:text-base text-muted-foreground leading-6">
                Start with a secure workspace for your team.
              </p>
            </div>

            {error && (
              <div className="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-600">
                {error}
              </div>
            )}

            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Organization name</label>
                <input
                  className={inputBase}
                  placeholder="e.g. Horizon Cloud Team"
                  value={form.organization_name}
                  onChange={(e) => setForm({ ...form, organization_name: e.target.value })}
                />
              </div>

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
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Password</label>
                <div className="relative">
                  <input
                    className={`${inputBase} pr-12`}
                    type={showPassword ? "text" : "password"}
                    placeholder="Create a strong password"
                    autoComplete="new-password"
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
                <div className="space-y-2">
                  <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
                    <div className={`h-full ${passwordStrength.tone} transition-all`} style={{ width: passwordStrength.width }} />
                  </div>
                  <div className="text-xs text-muted-foreground">{passwordStrength.label}</div>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Confirm password</label>
                <div className="relative">
                  <input
                    className={`${inputBase} pr-12`}
                    type={showConfirmPassword ? "text" : "password"}
                    placeholder="Re-enter your password"
                    autoComplete="new-password"
                    value={form.confirmPassword}
                    onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword((v) => !v)}
                    className="absolute inset-y-0 right-0 flex items-center px-4 text-muted-foreground hover:text-foreground transition"
                    aria-label={showConfirmPassword ? "Hide confirm password" : "Show confirm password"}
                  >
                    {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
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
                  Creating workspace...
                </>
              ) : (
                "Create organization"
              )}
            </button>

            <div className="text-sm text-center text-muted-foreground">
              Already have an account?{" "}
              <Link to="/login" className="font-medium text-primary hover:underline">
                Sign in
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
