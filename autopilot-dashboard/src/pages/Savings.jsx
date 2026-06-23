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
        const [o, t, r] = await Promise.all([
          getSavingsOverview(),
          getSavingsTrend(),
          getRecommendations(),
        ]);

        setOverview(o);
        setTrend(t || []);
        setRecs(r?.recommendations || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const download = (fn, filename) => {
    fn().then((res) => {
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

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card title="Total Saved">
          ${overview?.lifetime?.total_saved ?? 0}
        </Card>

        <Card title="Monthly Savings">
          ${overview?.current_month?.savings ?? 0}
        </Card>

        <Card title="Potential Savings">
          ${overview?.potential_monthly_savings ?? 0}
        </Card>

        <Card title="Actions Taken">
          {overview?.lifetime?.actions_taken ?? 0}
        </Card>
      </div>

      <Card title="Savings Trend">
        <LineChart data={trend} xKey="date" yKey="cost" />
      </Card>

      <Card title="Recommendations">
        <ul className="space-y-2">
          {recs.map((r) => (
            <li key={r.id} className="border-b pb-2">
              <p className="font-medium">{r.title}</p>
              <p className="text-sm text-gray-500">{r.description}</p>
              <p className="text-sm text-gray-500">Cloud: {r.cloud}</p>
              <p className="text-sm text-gray-500">{r.resource}</p>
              <p className="text-sm">
                Estimated saving: <strong>${r.savings}</strong>
              </p>
              <p className="text-xs text-gray-400">
                Confidence: {r.confidence} | Status: {r.status}
              </p>
            </li>
          ))}
        </ul>
      </Card>

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