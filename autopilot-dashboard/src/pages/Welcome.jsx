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
      "Securely connect AWS, Azure, or GCP with permissions that fit your team’s security standards.",
    badge: "Least-privilege setup",
  },
  {
    number: "02",
    title: "Analyze spend automatically",
    description:
      "Autopilot scans usage patterns, identifies waste, and prioritizes cost-saving opportunities with AI.",
    badge: "AI-powered insights",
  },
  {
    number: "03",
    title: "Review with confidence",
    description:
      "Set approval rules, policy thresholds, and risk controls so every recommendation stays aligned with your governance.",
    badge: "Policy control",
  },
  {
    number: "04",
    title: "Act on savings safely",
    description:
      "Move from visibility to action when your team is ready, with automation that stays within your guardrails.",
    badge: "Safe automation",
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
        <div
          className={`h-12 w-12 rounded-2xl flex items-center justify-center ${accent}`}
        >
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

function SectionHeading({ eyebrow, title, description }) {
  return (
    <div className="mx-auto max-w-3xl text-center space-y-4">
      <div className="text-xs uppercase tracking-[0.24em] text-muted-foreground">
        {eyebrow}
      </div>
      <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight">
        {title}
      </h2>
      <p className="text-base sm:text-lg text-muted-foreground leading-7">
        {description}
      </p>
    </div>
  );
}

export default function Welcome() {
  const [mobileOpen, setMobileOpen] = useState(false);

  const heroStats = useMemo(
    () => [
      { label: "Savings tracked", value: "$0 → $62K" },
      { label: "Optimization modes", value: "Observe • Recommend • Automate" },
      { label: "Governance control", value: "Approvals + thresholds" },
    ],
    []
  );

  const trust = [
    "Least-privilege access by default",
    "Complete audit trail for every action",
    "Human review before automation",
    "Built for modern cloud teams",
  ];

  const benefits = [
    {
      icon: <Gauge className="h-5 w-5" />,
      title: "Prioritize what matters",
      description:
        "See the highest-value opportunities first, so your team can focus on savings that actually move the needle.",
    },
    {
      icon: <ShieldCheck className="h-5 w-5" />,
      title: "Stay in control",
      description:
        "Policies, approvals, and thresholds keep every recommendation aligned with your internal standards.",
    },
    {
      icon: <BarChart3 className="h-5 w-5" />,
      title: "Measure impact clearly",
      description:
        "Track estimated savings, risk trends, and action status in a single view your team can trust.",
    },
  ];

  const featureCards = [
    {
      icon: <Cloud className="h-5 w-5" />,
      title: "Multi-cloud visibility",
      text: "Connect AWS, Azure, and GCP in one place and see spend patterns across your environment.",
    },
    {
      icon: <Bot className="h-5 w-5" />,
      title: "AI-powered recommendations",
      text: "Surface idle resources, overprovisioned workloads, and optimization opportunities automatically.",
    },
    {
      icon: <Lock className="h-5 w-5" />,
      title: "Policy-driven automation",
      text: "Decide what can be reviewed, approved, or executed so automation always respects your controls.",
    },
    {
      icon: <Activity className="h-5 w-5" />,
      title: "Operational oversight",
      text: "Monitor activity, review changes, and keep a clear record of every recommendation and action.",
    },
  ];

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
              <a href="#features" className="hover:text-foreground transition">
                Features
              </a>
              <a href="#how-it-works" className="hover:text-foreground transition">
                How it works
              </a>
              <a href="#security" className="hover:text-foreground transition">
                Security
              </a>
              <a href="#beta" className="hover:text-foreground transition">
                Beta
              </a>
            </nav>

            <div className="hidden md:flex items-center gap-3">
              <ThemeToggle />
              <Link
                to="/login"
                className="text-sm text-muted-foreground hover:text-foreground transition"
              >
                Sign in
              </Link>
              <Link
                to="/register"
                className="inline-flex items-center gap-2 rounded-full bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground shadow-lg shadow-primary/20 hover:-translate-y-0.5 transition"
              >
                Request access <ArrowRight className="h-4 w-4" />
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
                <a href="#features" className="rounded-xl px-3 py-2 text-sm hover:bg-muted/30">
                  Features
                </a>
                <a href="#how-it-works" className="rounded-xl px-3 py-2 text-sm hover:bg-muted/30">
                  How it works
                </a>
                <a href="#security" className="rounded-xl px-3 py-2 text-sm hover:bg-muted/30">
                  Security
                </a>
                <a href="#beta" className="rounded-xl px-3 py-2 text-sm hover:bg-muted/30">
                  Beta
                </a>
                <div className="flex items-center justify-between px-3 py-2">
                  <ThemeToggle />
                  <Link
                    to="/login"
                    className="text-sm text-muted-foreground hover:text-foreground transition"
                  >
                    Sign in
                  </Link>
                </div>
              </div>
            </div>
          )}
        </div>
      </header>

      <main className="flex-1">
        {/* HERO */}
        <section className="relative overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.15),transparent_35%),radial-gradient(circle_at_top_right,rgba(59,130,246,0.08),transparent_30%)]" />
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-16 lg:py-24 relative">
            <div className="grid lg:grid-cols-12 gap-10 items-center">
              <div className="lg:col-span-6 space-y-8">
                <div className="space-y-4">
                  <FeaturePill
                    icon={<Sparkles className="h-4 w-4" />}
                    text="Private beta for cloud teams"
                  />
                  <h1 className="text-5xl sm:text-6xl lg:text-7xl font-semibold tracking-tight leading-[1.02] max-w-3xl">
                    An autonomous cloud cost optimization platform. Real savings.
                    Zero guesswork.
                  </h1>
                  <p className="text-lg sm:text-xl text-muted-foreground leading-8 max-w-2xl">
                    Autopilot helps teams uncover waste, prioritize meaningful savings,
                    and move from insight to action with confidence, policy controls,
                    and full audit visibility.
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
                    Request access
                  </a>
                </div>

                <div className="grid sm:grid-cols-3 gap-3">
                  {heroStats.map((item) => (
                    <div
                      key={item.label}
                      className="rounded-2xl border border-border bg-card/70 backdrop-blur px-4 py-4 shadow-sm"
                    >
                      <div className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground mb-1">
                        {item.label}
                      </div>
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
                        <div className="text-sm font-medium">Autopilot savings console</div>
                      </div>
                      <div className="text-xs text-muted-foreground inline-flex items-center gap-2">
                        <ShieldCheck className="h-4 w-4" />
                        Guarded automation
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4 p-5">
                      <div className="space-y-4">
                        <div className="rounded-2xl border border-border bg-background p-4 shadow-sm">
                          <div className="flex items-center justify-between mb-4">
                            <div>
                              <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground mb-1">
                                Estimated monthly savings
                              </div>
                              <div className="text-2xl font-semibold">$62K</div>
                            </div>
                            <TrendingUp className="h-8 w-8 text-primary" />
                          </div>
                          <div className="h-48">
                            <ResponsiveContainer width="100%" height="100%">
                              <AreaChart data={chartData}>
                                <defs>
                                  <linearGradient
                                    id="savingsGradient"
                                    x1="0"
                                    y1="0"
                                    x2="0"
                                    y2="1"
                                  >
                                    <stop offset="5%" stopColor="currentColor" stopOpacity={0.35} />
                                    <stop offset="95%" stopColor="currentColor" stopOpacity={0.02} />
                                  </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} opacity={0.25} />
                                <XAxis dataKey="month" tickLine={false} axisLine={false} fontSize={12} />
                                <YAxis tickLine={false} axisLine={false} fontSize={12} width={28} />
                                <Tooltip />
                                <Area
                                  type="monotone"
                                  dataKey="savings"
                                  stroke="currentColor"
                                  fill="url(#savingsGradient)"
                                />
                              </AreaChart>
                            </ResponsiveContainer>
                          </div>
                        </div>

                        <div className="grid grid-cols-3 gap-3">
                          <MetricCard
                            icon={<Cloud className="h-5 w-5" />}
                            label="Connected clouds"
                            value="3"
                            accent="bg-blue-500/10 text-primary"
                          />
                          <MetricCard
                            icon={<Bot className="h-5 w-5" />}
                            label="AI analysis"
                            value="Live"
                            accent="bg-violet-500/10 text-violet-500"
                          />
                          <MetricCard
                            icon={<Lock className="h-5 w-5" />}
                            label="Policy engine"
                            value="Enabled"
                            accent="bg-emerald-500/10 text-emerald-500"
                          />
                        </div>
                      </div>

                      <div className="space-y-4">
                        <div className="rounded-2xl border border-border bg-background p-4 shadow-sm">
                          <div className="flex items-center justify-between mb-4">
                            <div>
                              <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground mb-1">
                                Active insights
                              </div>
                              <div className="text-base font-semibold">
                                Recommendations ready for review
                              </div>
                            </div>
                            <PieChart className="h-8 w-8 text-primary" />
                          </div>
                          <div className="space-y-3">
                            {[
                              {
                                label: "Idle resources",
                                value: "12 instances",
                                note: "Estimated 21% monthly savings",
                              },
                              {
                                label: "Oversized workloads",
                                value: "8 services",
                                note: "Estimated 15% monthly savings",
                              },
                              {
                                label: "Storage cleanup",
                                value: "4 buckets",
                                note: "Estimated 9% monthly savings",
                              },
                            ].map((item) => (
                              <div
                                key={item.label}
                                className="rounded-2xl border border-border bg-muted/20 p-3"
                              >
                                <div className="flex items-start justify-between gap-3">
                                  <div>
                                    <div className="font-medium text-sm">{item.label}</div>
                                    <div className="text-xs text-muted-foreground mt-1">
                                      {item.note}
                                    </div>
                                  </div>
                                  <div className="text-xs rounded-full bg-primary/10 text-primary px-3 py-1">
                                    {item.value}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        <div className="rounded-2xl border border-border bg-background p-4 shadow-sm space-y-3">
                          <div className="flex items-center gap-2 text-sm font-medium">
                            <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                            Review status
                          </div>
                          <div className="text-sm text-muted-foreground leading-6">
                            All current recommendations are within approved policy limits and
                            ready for team review.
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

        {/* TRUST */}
        <section className="border-y border-border/60 bg-muted/20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              {trust.map((item) => (
                <div
                  key={item}
                  className="flex items-center gap-3 rounded-2xl border border-border bg-background px-4 py-4 shadow-sm"
                >
                  <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0" />
                  <span className="text-sm font-medium">{item}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* FEATURES */}
        <section id="features" className="py-20 lg:py-24">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <SectionHeading
              eyebrow="Why teams choose Autopilot"
              title="Built for clarity, control, and measurable savings"
              description="A modern cloud optimization experience should feel trustworthy, structured, and easy to adopt. Autopilot gives teams the visibility they need and the controls they expect."
            />

            <div className="mt-14 grid md:grid-cols-2 xl:grid-cols-4 gap-5">
              {featureCards.map((item) => (
                <div
                  key={item.title}
                  className="rounded-[1.75rem] border border-border bg-card p-6 shadow-sm"
                >
                  <div className="h-11 w-11 rounded-2xl bg-primary/10 text-primary flex items-center justify-center mb-5">
                    {item.icon}
                  </div>
                  <h3 className="text-lg font-semibold mb-3">{item.title}</h3>
                  <p className="text-sm leading-6 text-muted-foreground">{item.text}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* HOW IT WORKS */}
        <section id="how-it-works" className="py-20 lg:py-24 bg-muted/15 border-y border-border/60">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <SectionHeading
              eyebrow="How it works"
              title="A simple flow from visibility to action"
              description="The product experience is intentionally straightforward: connect, analyze, review, and automate when you're ready."
            />

            <div className="mt-14 grid lg:grid-cols-4 gap-5">
              {steps.map((step) => (
                <motion.div
                  key={step.number}
                  initial={{ opacity: 0, y: 14 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5 }}
                  className="rounded-[1.75rem] border border-border bg-card p-6 shadow-sm"
                >
                  <div className="text-xs uppercase tracking-[0.22em] text-muted-foreground mb-4">
                    {step.number}
                  </div>
                  <div className="inline-flex items-center rounded-full border border-border bg-background px-3 py-1 text-xs font-medium mb-4">
                    {step.badge}
                  </div>
                  <h3 className="text-lg font-semibold mb-3">{step.title}</h3>
                  <p className="text-sm leading-6 text-muted-foreground">{step.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* BENEFITS */}
        <section className="py-20 lg:py-24">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <SectionHeading
              eyebrow="Designed for decision-makers"
              title="Confidence for finance, engineering, and platform teams"
              description="The interface is polished, but the real value is operational: helping teams make better decisions faster, with less risk and more transparency."
            />

            <div className="mt-14 grid lg:grid-cols-3 gap-5">
              {benefits.map((item) => (
                <div
                  key={item.title}
                  className="rounded-[1.75rem] border border-border bg-card p-6 shadow-sm"
                >
                  <div className="h-11 w-11 rounded-2xl bg-primary/10 text-primary flex items-center justify-center mb-5">
                    {item.icon}
                  </div>
                  <h3 className="text-lg font-semibold mb-3">{item.title}</h3>
                  <p className="text-sm leading-6 text-muted-foreground">{item.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* SECURITY */}
        <section id="security" className="py-20 lg:py-24 bg-muted/15 border-y border-border/60">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="grid lg:grid-cols-12 gap-8 items-start">
              <div className="lg:col-span-5 space-y-6">
                <div className="text-xs uppercase tracking-[0.24em] text-muted-foreground">
                  Security and governance
                </div>
                <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight">
                  Built to earn trust before it earns savings
                </h2>
                <p className="text-base sm:text-lg text-muted-foreground leading-7">
                  Every part of the experience is designed to reassure users that cloud
                  actions are visible, governed, and reversible where possible.
                </p>
                <div className="grid gap-3">
                  {[
                    "Least-privilege permissions from the start",
                    "Audit logs for every recommendation and action",
                    "Approval workflows for sensitive changes",
                    "Clear policy boundaries before automation",
                  ].map((item) => (
                    <div
                      key={item}
                      className="flex items-center gap-3 rounded-2xl border border-border bg-card px-4 py-3 shadow-sm"
                    >
                      <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0" />
                      <span className="text-sm font-medium">{item}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="lg:col-span-7">
                <div className="rounded-[2rem] border border-border bg-card p-6 shadow-sm">
                  <div className="flex items-center justify-between gap-4 mb-6">
                    <div>
                      <div className="text-xs uppercase tracking-[0.22em] text-muted-foreground mb-2">
                        Risk overview
                      </div>
                      <div className="text-xl font-semibold">Governance snapshot</div>
                    </div>
                    <div className="inline-flex items-center gap-2 rounded-full border border-border bg-background px-3 py-2 text-sm">
                      <ShieldCheck className="h-4 w-4 text-primary" />
                      Protected mode
                    </div>
                  </div>

                  <div className="grid md:grid-cols-3 gap-4">
                    <div className="rounded-2xl border border-border bg-background p-4">
                      <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground mb-2">
                        Access
                      </div>
                      <div className="text-lg font-semibold mb-1">Restricted</div>
                      <div className="text-sm text-muted-foreground">
                        Only approved roles can configure connected accounts.
                      </div>
                    </div>
                    <div className="rounded-2xl border border-border bg-background p-4">
                      <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground mb-2">
                        Actions
                      </div>
                      <div className="text-lg font-semibold mb-1">Reviewed</div>
                      <div className="text-sm text-muted-foreground">
                        Recommendations remain in review until policy conditions are met.
                      </div>
                    </div>
                    <div className="rounded-2xl border border-border bg-background p-4">
                      <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground mb-2">
                        Logging
                      </div>
                      <div className="text-lg font-semibold mb-1">Enabled</div>
                      <div className="text-sm text-muted-foreground">
                        Actions are captured for audit, reporting, and operational review.
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* BETA CTA */}
        <section id="beta" className="py-20 lg:py-24">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="relative overflow-hidden rounded-[2.25rem] border border-border bg-card shadow-sm">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(59,130,246,0.12),transparent_40%)]" />
              <div className="relative px-6 py-10 sm:px-10 sm:py-12 lg:px-14 lg:py-14">
                <div className="grid lg:grid-cols-12 gap-8 items-center">
                  <div className="lg:col-span-8 space-y-4">
                    <div className="text-xs uppercase tracking-[0.24em] text-muted-foreground">
                      Private beta
                    </div>
                    <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight max-w-2xl">
                      Join the cloud teams using Autopilot to identify savings faster.
                    </h2>
                    <p className="text-base sm:text-lg text-muted-foreground leading-7 max-w-2xl">
                      Get early access to a polished optimization workflow built for real
                      teams that need visibility, control, and measurable impact.
                    </p>
                  </div>
                  <div className="lg:col-span-4 flex lg:justify-end gap-3 flex-col sm:flex-row lg:flex-col">
                    <Link
                      to="https://forms.gle/4HbeoPkHpREB7J1u9"
                      className="inline-flex items-center justify-center gap-2 rounded-2xl bg-primary px-6 py-3.5 text-sm font-medium text-primary-foreground shadow-xl shadow-primary/20 hover:-translate-y-0.5 transition"
                    >
                      Apply for beta access <ArrowRight className="h-4 w-4" />
                    </Link>
                    <a
                      href="#features"
                      className="inline-flex items-center justify-center gap-2 rounded-2xl border border-border bg-background px-6 py-3.5 text-sm font-medium hover:bg-muted/30 transition"
                    >
                      Explore features
                    </a>
                  </div>
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
