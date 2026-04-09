// src/components/sefety/RiskGate.jsx

import { ShieldAlert, ShieldCheck } from "lucide-react";

export default function RiskGate({ currentRisk, maxRisk }) {
  const blocked = currentRisk > maxRisk;

  return (
    <div
      className={`flex items-center gap-2 text-sm ${
        blocked ? "text-danger" : "text-success"
      }`}
    >
      {blocked ? <ShieldAlert size={16} /> : <ShieldCheck size={16} />}
      Risk {currentRisk}% / Allowed {maxRisk}%
      {blocked && " — BLOCKED"}
    </div>
  );
}
