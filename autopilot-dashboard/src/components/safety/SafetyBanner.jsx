// src/components/sefety/SefetyBanner.jsx

import { AlertTriangle, Lock } from "lucide-react";

export default function SafetyBanner({ safety }) {
  if (safety.autopilot_enabled) return null;

  return (
    <div className="flex items-center gap-3 p-4 mb-4 rounded-lg bg-danger/10 border border-danger">
      <Lock className="text-danger" size={18} />
      <div>
        <p className="font-semibold text-danger">
          Autopilot is globally disabled
        </p>
        <p className="text-sm text-muted">
          No automated actions can run until this lock is removed.
        </p>
      </div>
    </div>
  );
}
