// src/components/ui/RecentActions.jsx

export default function RecentActions({ actions }) {
  return (
    <div className="bg-surface p-6 rounded-lg border border-border">
      <h3 className="font-medium mb-4">Recent Actions</h3>

      {!actions.length && (
        <div className="text-sm text-muted">
          No recent actions
        </div>
      )}

      <ul className="space-y-3">
        {actions.map((a, i) => (
          <li
            key={i}
            className="text-sm flex items-center gap-2"
          >
            <span className="text-success">✔</span>
            <span>
              {a.action} → {a.resource_id}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
