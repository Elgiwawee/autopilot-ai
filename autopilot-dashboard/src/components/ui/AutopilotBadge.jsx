// src/components/ui/AutopilotBadge.jsx

export default function AutopilotBadge({ autopilot }) {
  if (!autopilot) return null;

  const isGloballyEnabled = autopilot.autopilot_enabled;
  const activeAccounts = autopilot.active_accounts || 0;

  let label = "Paused";
  let styles = "bg-warning/10 text-warning";

  if (!isGloballyEnabled) {
    label = "Disabled";
    styles = "bg-danger/10 text-danger";
  } else if (activeAccounts > 0) {
    label = "Active";
    styles = "bg-success/10 text-success";
  }

  return (
    <span
      className={`px-3 py-1 rounded-full text-sm font-medium ${styles}`}
    >
      Autopilot {label}
    </span>
  );
}