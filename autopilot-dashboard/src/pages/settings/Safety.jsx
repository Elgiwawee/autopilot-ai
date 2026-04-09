import { useEffect, useState } from "react";
import {
  getGlobalSafety,
  toggleAutopilot,
} from "../../api/safety.api";

import SafetyBanner from "../../components/safety/SafetyBanner";
import toast  from "react-hot-toast";

export default function Safety() {
  const [safety, setSafety] = useState(null);
  const [loading, setLoading] = useState(false);

  // ✅ Initial load
  useEffect(() => {
    loadSafety();
  }, []);

  // ✅ Real-time polling (every 5s)
  useEffect(() => {
    const interval = setInterval(() => {
      loadSafety();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  async function loadSafety() {
    const data = await getGlobalSafety();
    setSafety(data);
  }

  // ✅ Toggle handler
  async function handleToggle() {
    setLoading(true);

    try {
      const updated = await toggleAutopilot();

      // ✅ instant UI update (no waiting for polling)
      toast.success(`Autopilot ${updated.autopilot_enabled ? "enabled" : "locked"}`);
      setSafety(prev => ({
        ...prev,
        autopilot_enabled: updated.autopilot_enabled,
      }));
    } catch (err) {
      console.error("Toggle failed", err);
      toast.error("Failed to toggle autopilot");
    } finally {
      setLoading(false);
    }
  }

  if (!safety) return null;

  return (
    <div className="space-y-6">
      <SafetyBanner safety={safety} />

      <div className="bg-panel border border-border rounded-lg p-6">
        <h2 className="font-semibold mb-2">
          Global Autopilot Safety
        </h2>

        <p className="text-sm text-muted">
          This lock disables all automated actions across all cloud accounts.
        </p>

        {/* STATUS */}
        <div className="mt-4 text-sm">
          Status:{" "}
          <span
            className={
              safety.autopilot_enabled
                ? "text-success"
                : "text-danger"
            }
          >
            {safety.autopilot_enabled ? "ENABLED" : "LOCKED"}
          </span>
        </div>

        {/* 🔥 TOGGLE BUTTON */}
        <div className="mt-6">
          <button
            onClick={handleToggle}
            disabled={loading}
            className={`px-4 py-2 rounded transition ${
              safety.autopilot_enabled
                ? "bg-red-500 text-white"
                : "bg-green-500 text-white"
            }`}
          >
            {loading
              ? "Updating..."
              : safety.autopilot_enabled
              ? "Disable Autopilot"
              : "Enable Autopilot"}
          </button>
        </div>
      </div>
    </div>
  );
}