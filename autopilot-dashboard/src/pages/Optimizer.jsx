import { useEffect, useState } from "react";
import { getOptimizer, applyOptimization } from "../api/optimizer.api";
import Spinner from "../components/ui/Spinner";

export default function Optimizer() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [applying, setApplying] = useState(null);

  async function load() {
    try {
      const res = await getOptimizer();
      setData(res);
    } catch {
      alert("Failed to load optimizer");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleApply(id) {
    setApplying(id);

    try {
      await applyOptimization(id);
      alert("✅ Optimization applied");

      await load(); // refresh
    } catch {
      alert("❌ Failed to apply");
    }

    setApplying(null);
  }

  if (loading) return <Spinner />;

  const optimizations = data?.optimizations || [];

  return (
    <div className="space-y-6">

      {/* HEADER */}
      <div>
        <h1 className="text-xl font-semibold">Optimizer</h1>
        <p className="text-sm text-muted">
          AI-powered cost optimization recommendations
        </p>
      </div>

      {/* EMPTY STATE */}
      {optimizations.length === 0 && (
        <div className="bg-panel border border-border rounded-lg p-6 text-center">
          <div className="text-lg font-medium mb-2">
            No optimizations yet
          </div>
          <p className="text-sm text-muted">
            Connect active cloud resources to start seeing recommendations.
          </p>
        </div>
      )}

      {/* LIST */}
      {optimizations.map(opt => (
        <div
          key={opt.id}
          className="bg-panel border border-border rounded-lg p-5 flex justify-between items-center"
        >
          <div>
            <div className="font-medium">{opt.title}</div>

            <div className="text-sm text-muted mt-1">
              {opt.description}
            </div>

            <div className="text-xs text-muted mt-2 flex gap-3">
              <span>Resource: {opt.resource}</span>

              <span className="text-green-500 font-medium">
                💰 Save: ${opt.savings}
              </span>

              <span className="text-blue-400">
                Confidence: {Math.round(opt.confidence * 100)}%
              </span>
            </div>
          </div>

          {/* APPLY BUTTON */}
          <button
            onClick={() => handleApply(opt.id)}
            disabled={applying === opt.id}
            className="bg-primary text-white px-4 py-2 rounded text-sm"
          >
            {applying === opt.id ? "Applying..." : "Apply"}
          </button>
        </div>
      ))}
    </div>
  );
}