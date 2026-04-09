// src/components/ui/Badge.jsx

const variants = {
  success: "bg-success/10 text-success",
  muted: "bg-border text-muted",
};
export default function Badge({ children, variant = "gray" }) {
  return (
    <span className={`px-2 py-1 rounded text-xs ${variants[variant]}`}>
      {children}
    </span>
  );
}
