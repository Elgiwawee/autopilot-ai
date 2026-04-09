// src/components/ui/Card.jsx

export default function Card({ title, children }) {
  return (
    <div className="bg-surface border border-border rounded-xl shadow-card p-4">
      {title && <h3 className="font-medium mb-3">{title}</h3>}
      {children}
    </div>
  );
}
