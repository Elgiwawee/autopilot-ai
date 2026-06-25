import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowRight,
  CheckCircle2,
  Cloud,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  Gauge,
  Bot,
  PieChart,
  Menu,
  X,
  Lock,
  Activity,
  BarChart3,
} from "lucide-react";
import {
  AreaChart,
  Area,
  ResponsiveContainer,
  Tooltip,
  CartesianGrid,
  XAxis,
  YAxis,
} from "recharts";

import { useMemo, useState } from "react";
import ThemeToggle from "../components/ThemeToggle";
import Footer from "../components/layout/Footer";

const steps = [
  {
    number: "01",
    title: "Connect your cloud",
    description:
      "Securely connect AWS, Azure, or GCP with the exact permissions you choose.",
    badge: "Read-only first",
  },
  {
    number: "02",
    title: "Discover opportunities",
    description:
      "Autopilot scans resources, detects idle waste, and ranks savings opportunities automatically.",
    badge: "AI detection",
  },
  {
    number: "03",
    title: "Review and control",
    description:
      "Set policy limits, approvals, and risk thresholds. You stay in control while AI handles the analysis.",
    badge: "Policy-driven",
  },
  {
    number: "04",
    title: "Automate savings",
    description:
      "Move from observe to recommend to autopilot when your team is ready to act safely.",
    badge: "Safe execution",
  },
];

const chartData = [
  { month: "Jan", savings: 12, risks: 5 },
  { month: "Feb", savings: 18, risks: 6 },
  { month: "Mar", savings: 26, risks: 7 },
  { month: "Apr", savings: 34, risks: 5 },
  { month: "May", savings: 48, risks: 4 },
  { month: "Jun", savings: 62, risks: 3 },
];

const stats = [
  { label: "Accounts scanned", value: "3+ clouds" },
  { label: "Actions gated", value: "Policy-based" },
  { label: "Savings visibility", value: "Real time" },
];

const trust = [
  "Least-privilege permissions",
  "Audit logs for every action",
  "Observe before automation",
  "Built for cloud teams",
];

function MetricCard({ icon, label, value, accent }) {
  return (
    <div className="rounded-3xl border border-border bg-card/80 backdrop-blur p-5 shadow-sm">
      <div className="flex items-center justify-between gap-4">
        <div>
          <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground mb-2">
            {label}
          </div>
          <div className="text-2xl font-semibold">{value}</div>
        </div>
        <div className={`h-12 w-12 rounded-2xl flex items-center justify-center ${accent}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

function FeaturePill({ icon, text }) {
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-border bg-background/80 px-4 py-2 text-sm shadow-sm">
      <span className="text-primary">{icon}</span>
      <span>{text}</span>
    </div>
  );
}

export default function Welcome() {
  const [mobileOpen, setMobileOpen] = useState(false);

  const heroStats = useMemo(
    () => [
      { label: "Savings tracked", value: "$0 → $62K" },
      { label: "Optimization modes", value: "Observe • Recommend • Autopilot" },
      { label: "Policy control", value: "Risk limits + approvals" },
    ],
    []
  );

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground">
      {/* NAVBAR */}
      <header className="sticky top-0 z-50 border-b border-border/70 bg-background/90 backdrop-blur-xl">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="h-16 flex items-center justify-between gap-4">
            <Link to="/" className="flex items-center gap-3 group">
              <div className="relative h-10 w-10 flex items-center justify-center overflow-hidden">
                <span className="absolute inset-0 bg-primary/10 blur-xl opacity-0 group-hover:opacity-100 transition rounded-2xl" />

                <img
                  src="/icon.png"
                  alt="Autopilot"
                  className="relative z-10 h-11 w-11 object-contain transition-transform duration-300 group-hover:scale-105"
                />
              </div>
              <div className="leading-tight">
                <div className="font-semibold text-lg tracking-tight">Autopilot</div>
                <div className="text-[11px] text-muted-foreground hidden sm:block">
                  Autonomous cloud optimization
                </div>
              </div>
            </Link>

            <nav className="hidden md:flex items-center gap-6 text-sm text-muted-foreground">
              <a href="#features" className="hover:text-foreground transition">Features</a>
              <a href="#how-it-works" className="hover:text-foreground transition">How it works</a>
              <a href="#security" className="hover:text-foreground transition">Security</a>
              <a href="#beta" className="hover:text-foreground transition">Beta</a>
            </nav>

            <div className="hidden md:flex items-center gap-3">
              <ThemeToggle />
              <Link to="/login" className="text-sm text-muted-foreground hover:text-foreground transition">
                Sign in
              </Link>
              <Link
                to="/register"
                className="inline-flex items-center gap-2 rounded-full bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground shadow-lg shadow-primary/20 hover:-translate-y-0.5 transition"
              >
                Get started <ArrowRight className="h-4 w-4" />
              </Link>
            </div>

            <button
              className="md:hidden inline-flex h-10 w-10 items-center justify-center rounded-full border border-border"
              onClick={() => setMobileOpen((v) => !v)}
              aria-label="Open menu"
            >
              {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>

          {mobileOpen && (
            <div className="md:hidden pb-4">
              <div className="grid gap-2 rounded-2xl border border-border bg-card p-3 shadow-sm">
                <a href="#features" className="rounded-xl px-3 py-2 text-sm hover:bg-muted/30">Features</a>
                <a href="#how-it-works" className="rounded-xl px-3 py-2 text-sm hover:bg-muted/30">How it works</a>
                <a href="#security" className="rounded-xl px-3 py-2 text-sm hover:bg-muted/30">Security</a>
                <a href="#beta" className="rounded-xl px-3 py-2 text-sm hover:bg-muted/30">Beta</a>
                <div className="flex items-center justify-between px-3 py-2">
                  <ThemeToggle />
                  <Link to="/login" className="text-sm text-muted-foreground hover:text-foreground transition">
                    Sign in
                  </Link>
                </div>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* HERO */}
      <main className="flex-1">
        <section className="relative overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.15),transparent_35%),radial-gradient(circle_at_top_right,rgba(59,130,246,0.08),transparent_30%)]" />
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-16 lg:py-24 relative">
            <div className="grid lg:grid-cols-12 gap-10 items-center">
              <div className="lg:col-span-6 space-y-8">
                <div className="space-y-4">
                  <FeaturePill icon={<Sparkles className="h-4 w-4" />} text="Private beta for cloud teams" />
                  <h1 className="text-5xl sm:text-6xl lg:text-7xl font-semibold tracking-tight leading-[1.02] max-w-3xl">
                    Cloud optimization that feels premium, fast, and safe.
                  </h1>
                  <p className="text-lg sm:text-xl text-muted-foreground leading-8 max-w-2xl">
                    Autopilot discovers waste, ranks savings opportunities, and helps teams move from observe to automation with policy controls, approvals, and audit trails.
                  </p>
                </div>

                <div className="flex flex-col sm:flex-row gap-3">
                  <Link
                    to="/register"
                    className="inline-flex items-center justify-center gap-2 rounded-2xl bg-primary px-6 py-3.5 text-sm font-medium text-primary-foreground shadow-xl shadow-primary/20 hover:-translate-y-0.5 transition"
                  >
                    Start free <ArrowRight className="h-4 w-4" />
                  </Link>
                  <Link
                    to="/login"
                    className="inline-flex items-center justify-center gap-2 rounded-2xl border border-border bg-card px-6 py-3.5 text-sm font-medium hover:bg-muted/30 transition"
                  >
                    Sign in
                  </Link>
                  <a
                    href="#beta"
                    className="inline-flex items-center justify-center gap-2 rounded-2xl border border-border bg-transparent px-6 py-3.5 text-sm font-medium hover:bg-muted/20 transition"
                  >
                    Join beta
                  </a>
                </div>

                <div className="grid sm:grid-cols-3 gap-3">
                  {heroStats.map((item) => (
                    <div key={item.label} className="rounded-2xl border border-border bg-card/70 backdrop-blur px-4 py-4 shadow-sm">
                      <div className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground mb-1">{item.label}</div>
                      <div className="font-medium text-sm sm:text-base">{item.value}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="lg:col-span-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6 }}
                  viewport={{ once: true }}
                  className="relative"
                >
                  <div className="absolute -inset-6 bg-primary/10 blur-3xl rounded-full" />
                  <div className="relative rounded-[2rem] border border-border bg-card/80 backdrop-blur-xl shadow-2xl overflow-hidden">
                    <div className="flex items-center justify-between px-5 py-4 border-b border-border bg-background/70">
                      <div className="flex items-center gap-3">
                        <div className="flex gap-1.5">
                          <span className="h-3 w-3 rounded-full bg-red-400" />
                          <span className="h-3 w-3 rounded-full bg-yellow-400" />
                          <span className="h-3 w-3 rounded-full bg-emerald-400" />
                        </div>
                        <div className="text-sm font-medium">Autopilot command center</div>
                      </div>
                      <div className="text-xs text-muted-foreground inline-flex items-center gap-2">
                        <ShieldCheck className="h-4 w-4" />
                        Safe mode
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4 p-5">
                      <div className="space-y-4">
                        <div className="rounded-2xl border border-border bg-background p-4 shadow-sm">
                          <div className="flex items-center justify-between mb-4">
                            <div>
                              <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground mb-1">Savings potential</div>
                              <div className="text-2xl font-semibold">$62K</div>
                            </div>
                            <TrendingUp className="h-8 w-8 text-primary" />
                          </div>
                          <div className="h-48">
                            <ResponsiveContainer width="100%" height="100%">
                              <AreaChart data={chartData}>
                                <defs>
                                  <linearGradient id="savingsGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="currentColor" stopOpacity={0.35} />
                                    <stop offset="95%" stopColor="currentColor" stopOpacity={0.02} />
                                  </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} opacity={0.25} />
                                <XAxis dataKey="month" tickLine={false} axisLine={false} fontSize={12} />
                                <YAxis tickLine={false} axisLine={false} fontSize={12} width={28} />
                                <Tooltip />
                                <Area type="monotone" dataKey="savings" stroke="currentColor" fill="url(#savingsGradient)" />
                              </AreaChart>
                            </ResponsiveContainer>
                          </div>
                        </div>

                        <div className="grid grid-cols-3 gap-3">
                          <MetricCard icon={<Cloud className="h-5 w-5" />} label="Clouds" value="3" accent="bg-blue-500/10 text-primary" />
                          <MetricCard icon={<Bot className="h-5 w-5" />} label="AI" value="Live" accent="bg-violet-500/10 text-violet-500" />
                          <MetricCard icon={<Lock className="h-5 w-5" />} label="Policy" value="On" accent="bg-emerald-500/10 text-emerald-500" />
                        </div>
                      </div>

                      <div className="space-y-4">
                        <div className="rounded-2xl border border-border bg-background p-4 shadow-sm">
                          <div className="flex items-center justify-between mb-4">
                            <div>
                              <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground mb-1">Live insights</div>
                              <div className="text-base font-semibold">Recommendations ready</div>
                            </div>
                            <PieChart className="h-8 w-8 text-primary" />
                          </div>

                          <div className="space-y-3">
                            {[
                              ["Idle compute detected", "Stop or downsize resources safely"],
                              ["Rightsizing opportunity", "Reduce over-provisioned instances"],
                              ["Audit trail", "Every action is recorded"],
                            ].map(([title, text], idx) => (
                              <div key={title} className="flex items-start gap-3 rounded-2xl border border-border p-3">
                                <div className="mt-0.5 h-7 w-7 rounded-xl bg-primary/10 text-primary flex items-center justify-center text-xs font-semibold">
                                  {idx + 1}
                                </div>
                                <div>
                                  <div className="font-medium text-sm">{title}</div>
                                  <div className="text-xs text-muted-foreground mt-1">{text}</div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        <div className="rounded-2xl border border-border bg-background p-4 shadow-sm">
                          <div className="flex items-center justify-between mb-3">
                            <div className="text-sm font-medium">Modes</div>
                            <Activity className="h-4 w-4 text-primary" />
                          </div>
                          <div className="grid gap-2">
                            {[
                              ["Observe", "Discovery only"],
                              ["Recommend", "Review before action"],
                              ["Autopilot", "Policy-driven execution"],
                            ].map(([a, b]) => (
                              <div key={a} className="flex items-center justify-between rounded-xl border border-border px-3 py-2 text-sm">
                                <span>{a}</span>
                                <span className="text-muted-foreground">{b}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              </div>
            </div>
          </div>
        </section>

        {/* FEATURES */}
        <section id="features" className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-20">
          <div className="grid lg:grid-cols-[1.1fr_0.9fr] gap-10 items-start">
            <div className="space-y-6">
              <div className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-4 py-2 text-sm text-muted-foreground shadow-sm">
                <Sparkles className="h-4 w-4 text-primary" />
                Premium UI. Clear outcomes. Real savings.
              </div>
              <h2 className="text-4xl font-semibold tracking-tight max-w-2xl leading-tight">
                Built to look like a serious cloud product from the first scroll.
              </h2>
              <p className="text-lg leading-8 text-muted-foreground max-w-2xl">
                Replace weak screenshots with a polished product story, a dashboard-style visualization, and a tighter top navigation that feels closer to AWS and Microsoft quality.
              </p>
            </div>

            <div className="grid gap-4">
              {[
                { title: "Compact navigation", text: "Short header, fewer distractions, cleaner first impression.", icon: <Menu className="h-5 w-5" /> },
                { title: "Dashboard visualization", text: "Show savings and policy flow with a premium chart and live metrics.", icon: <BarChart3 className="h-5 w-5" /> },
                { title: "Trust signals", text: "Security, control, and auditability are visible before signup.", icon: <ShieldCheck className="h-5 w-5" /> },
              ].map((item) => (
                <div key={item.title} className="rounded-[1.5rem] border border-border bg-card p-5 shadow-sm flex gap-4">
                  <div className="h-12 w-12 rounded-2xl bg-primary/10 text-primary flex items-center justify-center shrink-0">
                    {item.icon}
                  </div>
                  <div>
                    <div className="font-semibold mb-1">{item.title}</div>
                    <div className="text-sm leading-7 text-muted-foreground">{item.text}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* HOW IT WORKS */}
        <section id="how-it-works" className="border-y border-border bg-muted/20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-20">
            <div className="grid lg:grid-cols-2 gap-10 items-start">
              <div className="space-y-5 lg:pr-8">
                <div className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-4 py-2 text-sm text-muted-foreground shadow-sm">
                  <Gauge className="h-4 w-4 text-primary" />
                  How it works
                </div>
                <h2 className="text-4xl font-semibold tracking-tight leading-tight">
                  Left side: stronger story. Right side: premium visualization.
                </h2>
                <p className="text-lg leading-8 text-muted-foreground max-w-xl">
                  The step-by-step section should feel like a product explainer, not a document. Keep the text bigger and let the graphic carry the visual weight.
                </p>
                <div className="grid gap-3 pt-2">
                  {trust.map((item) => (
                    <div key={item} className="flex items-center gap-3 rounded-2xl border border-border bg-card px-4 py-3 shadow-sm">
                      <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0" />
                      <span className="text-sm">{item}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid gap-4">
                {steps.map((step, index) => (
                  <motion.div
                    key={step.title}
                    initial={{ opacity: 0, y: 16 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.45, delay: index * 0.06 }}
                    viewport={{ once: true }}
                    className="grid md:grid-cols-[140px_1fr] gap-4 rounded-[1.75rem] border border-border bg-card p-5 shadow-sm"
                  >
                    <div className="rounded-2xl bg-primary/10 p-4 flex flex-col justify-between min-h-[140px]">
                      <div className="text-3xl font-semibold text-primary">{step.number}</div>
                      <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground">{step.badge}</div>
                    </div>
                    <div className="flex flex-col justify-center">
                      <h3 className="text-2xl font-semibold tracking-tight mb-3">{step.title}</h3>
                      <p className="text-base leading-8 text-muted-foreground max-w-lg">{step.description}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* SECURITY */}
        <section id="security" className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-20">
          <div className="grid lg:grid-cols-2 gap-10 items-start">
            <div className="space-y-4">
              <div className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-4 py-2 text-sm text-muted-foreground shadow-sm">
                <Lock className="h-4 w-4 text-primary" />
                Security and control
              </div>
              <h2 className="text-4xl font-semibold tracking-tight leading-tight">
                Build trust like AWS, Microsoft, and Google do.
              </h2>
              <p className="text-lg leading-8 text-muted-foreground max-w-xl">
                The landing page should make security obvious: least-privilege permissions, audit logs, and controlled automation modes.
              </p>
            </div>

            <div className="grid gap-4">
              {[
                ["Least-privilege connections", "Use only the permissions needed for discovery and safe execution."],
                ["Audit-first workflow", "Log connection, recommendation, and execution events for review."],
                ["Human-in-the-loop", "Start with observe mode and move to autopilot only when ready."],
                ["Transparent data handling", "Be clear about what is collected and why."],
              ].map(([title, text]) => (
                <div key={title} className="rounded-[1.5rem] border border-border bg-card p-5 shadow-sm">
                  <div className="font-semibold mb-1">{title}</div>
                  <div className="text-sm text-muted-foreground leading-7">{text}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* BETA */}
        <section id="beta" className="border-y border-border bg-primary/5">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-20">
            <div className="grid lg:grid-cols-[1fr_420px] gap-10 items-start">
              <div className="space-y-5">
                <div className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-4 py-2 text-sm text-muted-foreground shadow-sm">
                  <Sparkles className="h-4 w-4 text-primary" />
                  Private beta
                </div>
                <h2 className="text-4xl font-semibold tracking-tight leading-tight max-w-2xl">
                  Invite a small number of teams and guide them from signup to insight.
                </h2>
                <p className="text-lg leading-8 text-muted-foreground max-w-2xl">
                  The beta section should speak to serious cloud teams, not random visitors. Keep the CTA direct and the promise clear.
                </p>
                <div className="flex flex-col sm:flex-row gap-3 pt-2">
                  <Link
                    to="https://forms.gle/QU48zpmeqrzx3PHP6"
                    className="inline-flex items-center justify-center gap-2 rounded-2xl bg-primary px-6 py-3.5 text-sm font-medium text-primary-foreground shadow-xl shadow-primary/20 hover:-translate-y-0.5 transition"
                  >
                    Join beta <ArrowRight className="h-4 w-4" />
                  </Link>
                  <Link
                    to="/register"
                    className="inline-flex items-center justify-center gap-2 rounded-2xl border border-border bg-card px-6 py-3.5 text-sm font-medium hover:bg-muted/30 transition"
                  >
                    Connect cloud account
                  </Link>
                </div>
              </div>

              <div className="rounded-[2rem] border border-border bg-card p-6 shadow-sm">
                <div className="text-sm text-muted-foreground uppercase tracking-[0.2em] mb-3">Ideal beta users</div>
                <div className="text-xl font-semibold mb-4">DevOps, FinOps, Platform, SRE</div>
                <div className="space-y-3 text-sm leading-7 text-muted-foreground">
                  <p>• Teams already managing cloud spend or infrastructure complexity</p>
                  <p>• Teams willing to connect one account and test observe mode first</p>
                  <p>• Teams open to honest feedback during onboarding</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}