// src/pages/Savings.jsx

import { useEffect, useState } from "react";
import {
  getSavingsOverview,
  getSavingsTrend,
  getRecommendations,
  exportSavingsCSV,
} from "../api/savings.api";
import Card from "../components/ui/Card";
import Spinner from "../components/ui/Spinner";
import LineChart from "../components/ui/LineChart";

export default function Savings() {
  const [overview, setOverview] = useState(null);
  const [trend, setTrend] = useState([]);
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const o = await getSavingsOverview();
        const t = await getSavingsTrend();
        const r = await getRecommendations();

        setOverview(o);
        setTrend(t);
        setRecs(r.recommendations || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const download = (fn, filename) => {
    fn().then(res => {
      const url = window.URL.createObjectURL(res.data);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
    });
  };

  if (loading) return <Spinner />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Savings</h1>

      {/* KPI */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card title="Total Saved">${overview?.total_saved ?? 0}</Card>
        <Card title="Monthly Savings">${overview?.monthly_savings ?? 0}</Card>
        <Card title="Potential Savings">
          ${overview?.potential_monthly_savings ?? 0}
        </Card>
        <Card title="Optimization Rate">{overview?.optimization_rate ?? 0}%</Card>
        <Card title="Actions Taken">{overview?.actions ?? 0}</Card>
      </div>

      {/* Trend */}
      <Card title="Savings Trend">
        <LineChart data={trend} xKey="month" yKey="amount" />
      </Card>

      {/* Recommendations */}
      <Card title="Recommendations">
        <ul className="space-y-2">
          {recs.map(r => (
            <li key={r.id} className="border-b pb-2">
              <p className="font-medium">
                {r.action} {r.resource_type}
              </p>

              <p className="text-sm text-gray-500">
                Cloud: {r.cloud} | Resource ID: {r.resource_id}
              </p>

              <p className="text-sm">
                Estimated saving: <strong>${r.estimated_monthly_savings}</strong>
              </p>

              <p className="text-xs text-gray-400">
                Confidence: {r.confidence} | Status: {r.status}
              </p>
            </li>
          ))}
        </ul>
      </Card>

      {/* Export */}
      <div className="flex gap-3">
        <button
          onClick={() => download(exportSavingsCSV, "savings.csv")}
          className="btn"
        >
          Export CSV
        </button>
      </div>
    </div>
  );
}
