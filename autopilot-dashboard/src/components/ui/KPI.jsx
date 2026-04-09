// src/components/ui/KPI.jsx

export default function KPI({ title, value, subtitle, trend }) {
  return (
    <div className="bg-surface border border-border rounded-xl p-6 shadow-card hover:shadow-cardHover transition-all duration-200">
      
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted">
          {title}
        </div>

        {trend && (
          <span
            className={`text-xs font-medium ${
              trend > 0 ? "text-success" : "text-danger"
            }`}
          >
            {trend > 0 ? `+${trend}%` : `${trend}%`}
          </span>
        )}
      </div>

      <div className="text-3xl font-semibold text-foreground mt-2">
        {value}
      </div>

      {subtitle && (
        <div className="text-xs text-muted mt-1">
          {subtitle}
        </div>
      )}
    </div>
  );
}
