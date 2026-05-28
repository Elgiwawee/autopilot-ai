// src/pages/Overview.jsx

import { useEffect, useState } from "react";
import { fetchOverview } from "../api/overview.api";

import KPI from "../components/ui/KPI";
import AutopilotBadge from "../components/ui/AutopilotBadge";
import CostTrendChart from "../components/ui/CostTrendChart";
import RecentActions from "../components/ui/RecentActions";

export default function OverviewPage() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchOverview()
      .then(setData)
      .catch(() => setError("Failed to load overview data"));
  }, []);

  if (error) {
    return (
      <div className="text-danger">
        {error}
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-muted">
        Loading overview…
      </div>
    );
  }

  return (
    <>
      {/* HEADER */}
      <div className="flex justify-between items-start mb-10">
        <div>
          <h1 className="text-3xl font-semibold">
            Overview
          </h1>
          <p className="text-sm text-muted mt-2">
            Real-time infrastructure optimization insights
          </p>
        </div>

        <AutopilotBadge autopilot={data.autopilot} />
      </div>

      {/* KPI CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">

        <div className="bg-panel border border-border rounded-xl p-6">
          <KPI
            title="Monthly Savings"
            value={`$${data.kpis.monthly_savings}`}
          />
        </div>

        <div className="bg-panel border border-border rounded-xl p-6">
          <KPI
            title="Lifetime Savings"
            value={`$${data.kpis.lifetime_savings}`}
          />
        </div>

        <div className="bg-panel border border-border rounded-xl p-6">
          <KPI
            title="GPUs Managed"
            value={data.kpis.gpu_count}
          />
        </div>

        <div className="bg-panel border border-border rounded-xl p-6">
          <KPI
            title="Active Optimizations"
            value={data.kpis.active_optimizations}
          />
        </div>

      </div>

      {/* CHART + ACTIONS */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">

        <div className="bg-panel border border-border rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4">
            Cost Trend
          </h2>
          <CostTrendChart data={data.cost_trend} />
        </div>

        <div className="bg-panel border border-border rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4">
            Recent Actions
          </h2>
          <RecentActions actions={data.recent_actions} />
        </div>

      </div>
    </>
  );
}