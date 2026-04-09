// src/pages/Welcome.jsx
import { Link } from "react-router-dom"
import { motion } from "framer-motion"
import ThemeToggle from "../components/ThemeToggle"
import Footer from "../components/layout/Footer"


const steps = [
  {
    title: "Connect Your Cloud",
    description:
      "Securely connect AWS, Azure, or GCP using read-only roles. No risk, full visibility.",
    image: "/images/connect-cloud.png",
  },
  {
    title: "Discover Opportunities",
    description:
      "Autopilot scans your infrastructure and detects waste, idle resources, and optimization opportunities instantly.",
    image: "/images/discover.png",
  },
  {
    title: "Review & Control",
    description:
      "Set policies, risk limits, and approvals. You stay in full control while AI handles the heavy lifting.",
    image: "/images/control.png",
  },
  {
    title: "Automate Savings",
    description:
      "Enable Autopilot to safely execute optimizations and continuously reduce your cloud costs.",
    image: "/images/automate.png",
  },
]

export default function Welcome() {
  return (
    <div className="min-h-screen flex flex-col">
      
      {/* NAVBAR */}
      <nav className="flex justify-between items-center px-8 py-5 border-b border-border">
        <Link to="/" className="flex items-center group relative">
          <div className="absolute inset-0 bg-primary/10 blur-xl opacity-0 group-hover:opacity-100 transition duration-500 rounded-full"></div>

          <img
            src="/logo.png"
            alt="Autopilot AI"
            className="relative h-12 w-auto object-contain transition duration-300 group-hover:scale-105"
          />
        </Link>

        <div className="flex items-center gap-4">
          <ThemeToggle />

          <Link to="/login" className="text-muted hover:text-white">
            Login
          </Link>

          <Link
            to="/register"
            className="bg-primary text-black px-4 py-2 rounded-lg font-medium"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* HERO */}
      <main className="flex items-center justify-center text-center px-6 min-h-[calc(100vh-80px)]">
        <div className="max-w-2xl">
          <h2 className="text-4xl font-bold leading-tight">
            Autonomous Cloud Optimization.
            <br /> Real Savings. Zero Guesswork.
          </h2>
          <p className="mt-6 text-muted text-lg">
            AI-driven cloud cost reduction with full auditability,
            safety controls, and executive-ready reporting.
          </p>

          <div className="mt-8 flex justify-center gap-4">
            <Link
              to="/register"
              className="bg-primary text-black px-6 py-3 rounded-lg font-semibold"
            >
              Start Free
            </Link>
            <Link
              to="/login"
              className="border border-border px-6 py-3 rounded-lg"
            >
              Sign In
            </Link>
          </div>
        </div>
      </main>

    {/* 🔥 NEW SECTION: HOW IT WORKS */}
    <section className="py-28 px-6 bg-gradient-to-b from-transparent to-white/5 relative overflow-hidden">
      <div className="max-w-6xl mx-auto">

        {/* TITLE */}
        <motion.h3
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-3xl font-bold text-center mb-20"
        >
          How It Works
        </motion.h3>

        <div className="space-y-28">
          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 100 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: index * 0.1 }}
              viewport={{ once: true }}
              className={`group flex flex-col md:flex-row items-center gap-12 ${
                index % 2 !== 0 ? "md:flex-row-reverse" : ""
              }`}
            >
              
              {/* 🖼 IMAGE */}
              <motion.div
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 120 }}
                className="flex-1 relative"
              >
                <div className="absolute inset-0 rounded-2xl bg-primary/10 blur-2xl opacity-0 group-hover:opacity-100 transition duration-500"></div>

                <img
                  src={step.image}
                  alt={step.title}
                  className="relative rounded-2xl shadow-2xl border border-white/10 transition duration-500 group-hover:shadow-primary/20"
                />
              </motion.div>

              {/* 🧊 TEXT CARD */}
              <motion.div
                whileHover={{ y: -5 }}
                transition={{ type: "spring", stiffness: 100 }}
                className="flex-1"
              >
                <div className="relative backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8 shadow-xl overflow-hidden">

                  {/* Glow hover effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-primary/20 via-transparent to-primary/20 opacity-0 group-hover:opacity-100 transition duration-700"></div>

                  {/* CONTENT */}
                  <div className="relative z-10">
                    <motion.h4
                      initial={{ opacity: 0, x: -20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.5 }}
                      className="text-xl font-semibold mb-4"
                    >
                      {index + 1}. {step.title}
                    </motion.h4>

                    <motion.p
                      initial={{ opacity: 0 }}
                      whileInView={{ opacity: 1 }}
                      transition={{ delay: 0.2 }}
                      className="text-muted leading-relaxed"
                    >
                      {step.description}
                    </motion.p>

                    {/* CTA ONLY LAST */}
                    {index === steps.length - 1 && (
                      <motion.div
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <Link
                          to="/register"
                          className="inline-flex items-center gap-2 mt-6 bg-primary text-black px-6 py-3 rounded-lg font-semibold transition-all duration-300 hover:shadow-lg hover:shadow-primary/40"
                        >
                          Get Started
                          <motion.span
                            animate={{ x: [0, 5, 0] }}
                            transition={{ repeat: Infinity, duration: 1.2 }}
                          >
                            →
                          </motion.span>
                        </Link>
                      </motion.div>
                    )}
                  </div>
                </div>
              </motion.div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
          <Footer />
    </div>
  )
}

