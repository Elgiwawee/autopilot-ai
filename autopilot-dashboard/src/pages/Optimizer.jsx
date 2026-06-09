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

              <span
              className={
                opt.status === "COMPLETED"
                  ? "text-green-600 font-semibold"
                  : opt.status === "FAILED"
                  ? "text-red-600 font-semibold"
                  : opt.status === "IN_PROGRESS"
                  ? "text-yellow-600 font-semibold"
                  : "text-blue-600 font-semibold"
              }
            >
              Status: {opt.status}
            </span>
            
            </div>
          </div>

          {/* APPLY BUTTON */}
            <div>
            {applying === opt.id ? (
              <button
                disabled
                className="bg-gray-400 text-white px-4 py-2 rounded text-sm"
              >
                Applying...
              </button>
            ) : opt.status === "PLANNED" ? (
              <button
                onClick={() => handleApply(opt.id)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm"
              >
                Apply
              </button>
            ) : opt.status === "IN_PROGRESS" ? (
              <button
                disabled
                className="bg-yellow-500 text-white px-4 py-2 rounded text-sm cursor-not-allowed"
              >
                ⏳ Executing...
              </button>
            ) : opt.status === "COMPLETED" ? (
              <button
                disabled
                className="bg-green-600 text-white px-4 py-2 rounded text-sm cursor-not-allowed"
              >
                ✅ Applied
              </button>
            ) : opt.status === "FAILED" ? (
              <button
                onClick={() => handleApply(opt.id)}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm"
              >
                Retry
              </button>
            ) : (
              <button
                disabled
                className="bg-gray-500 text-white px-4 py-2 rounded text-sm"
              >
                {opt.status}
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}