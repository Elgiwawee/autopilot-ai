// src/sefety/AutopilotModeLock.jsx

import { Lock } from "lucide-react";

export default function AutopilotModeLock({ disabled, reason }) {
  if (!disabled) return null;

  return (
    <div className="flex items-center gap-2 text-xs text-danger mt-2">
      <Lock size={14} />
      {reason}
    </div>
  );
}
