// tailwind.config.js

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        surface: "var(--surface)",
        border: "var(--border)",

        foreground: "var(--foreground)",
        muted: "var(--muted)",

        primary: "var(--primary)",
        primarySoft: "var(--primarySoft)",

        success: "var(--success)",
        warning: "var(--warning)",
        danger: "var(--danger)",
      },

      boxShadow: {
        card: "0 1px 2px rgba(0,0,0,0.05)",
        cardHover: "0 4px 12px rgba(0,0,0,0.08)",
      },

      borderRadius: {
        xl: "0.75rem",
        "2xl": "1rem",
      },
    },
  },
  plugins: [],
};