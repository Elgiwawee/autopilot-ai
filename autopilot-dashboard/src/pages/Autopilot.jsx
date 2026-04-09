import { useEffect, useState } from "react";
import {
  getAutopilotStatus,
  updateAutopilotMode,
  runAutopilotNow
} from "../api/autopilot.api";

import Card from "../components/ui/Card";
import Spinner from "../components/ui/Spinner";

const MODES = [
  "OFF",
  "RECOMMEND",
  "AUTO_SAFE",
  "AUTO_AGGRESSIVE"
];

export default function Autopilot() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAutopilotStatus()
      .then(setStatus)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spinner />;

  const autoDisabled = !status.autopilot_enabled;

  const changeMode = (accountId, mode) => {
    if (autoDisabled) return;

    updateAutopilotMode(accountId, mode)
      .then(() => getAutopilotStatus().then(setStatus));
  };

  return (
    <div className="space-y-6">

      {/* GLOBAL STATUS */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Autopilot Control</h1>

        <span
          className={`px-3 py-1 text-xs rounded-full font-medium ${
            status.autopilot_enabled
              ? "bg-green-500/20 text-green-400"
              : "bg-red-500/20 text-red-400"
          }`}
        >
          {status.autopilot_enabled ? "Autopilot Enabled" : "Autopilot Disabled"}
        </span>
      </div>

      {/* WARNING */}
      {!status.autopilot_enabled && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-lg">
          Autopilot is globally disabled. Enable it from Safety Settings.
        </div>
      )}

      {/* ACCOUNTS */}
      {status.accounts.map(account => (
        <div
          key={account.cloud_account_id}
          className="bg-panel border border-border rounded-xl p-6 shadow-sm"
        >
          {/* HEADER */}
          <div className="flex justify-between items-center mb-4">
            <div>
              <h2 className="font-semibold text-base">
                Cloud Account
              </h2>
              <p className="text-xs text-muted">
                {account.cloud_account_id}
              </p>
            </div>

            <span className="text-xs text-muted">
              Mode: <span className="font-medium text-white">{account.mode}</span>
            </span>
          </div>

          {/* MODE SELECTOR */}
          <div className="flex flex-wrap gap-2">
            {MODES.map(m => (
              <button
                key={m}
                disabled={autoDisabled}
                onClick={() =>
                  changeMode(account.cloud_account_id, m)
                }
                className={`px-3 py-1.5 rounded-full text-xs font-medium transition ${
                  account.mode === m
                    ? "bg-primary text-white"
                    : "bg-border text-muted hover:bg-border/70"
                } ${
                  autoDisabled ? "opacity-50 cursor-not-allowed" : ""
                }`}
              >
                {m.replace("_", " ")}
              </button>
            ))}
          </div>
        </div>
      ))}

      {/* MANUAL EXECUTION */}
      <div className="bg-panel border border-border rounded-xl p-6 flex items-center justify-between">
        <div>
          <h2 className="font-semibold">Manual Execution</h2>
          <p className="text-sm text-muted">
            Trigger autopilot optimization immediately
          </p>
        </div>

        <button
          disabled={autoDisabled}
          onClick={runAutopilotNow}
          className={`px-5 py-2 rounded-lg text-sm font-medium transition ${
            autoDisabled
              ? "bg-gray-600 text-gray-300 cursor-not-allowed"
              : "bg-red-500 hover:bg-red-600 text-white"
          }`}
        >
          Run Now
        </button>
      </div>
    </div>
  );
}