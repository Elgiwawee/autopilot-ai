// src/pages/Policies.jsx

import { useEffect, useState } from "react";
import { getPolicy, updatePolicy } from "../api/policies.api";
import Card from "../components/ui/Card";
import Spinner from "../components/ui/Spinner";
import toast from "react-hot-toast";

export default function Policies() {
  const [policy, setPolicy] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getPolicy()
      .then(setPolicy)
      .finally(() => setLoading(false));
  }, []);

  const handleChange = async (field, value) => {
    const updated = { ...policy, [field]: value };
    setPolicy(updated);

    try {
      await updatePolicy({ [field]: value });
      toast.success("Policy updated successfully");
    } catch (err) {
      console.error(err);
      toast.error("Failed to update policy");
    }
  };

  if (loading) return <Spinner />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Autopilot Policy</h1>

      {/* Optimization Limits */}
      <Card title="Optimization Limits">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium">
              Max Monthly Savings (%)
            </label>
            <input
              type="number"
              value={policy.max_monthly_savings_pct}
              onChange={(e) =>
                handleChange("max_monthly_savings_pct", Number(e.target.value))
              }
              className="border p-2 rounded w-full"
            />
          </div>
        </div>
      </Card>

      {/* Allowed Actions */}
      <Card title="Allowed Actions">
        <div className="space-y-3">
          {[
            ["allow_stop", "Allow Stop Instances"],
            ["allow_resize", "Allow Resize Resources"],
            ["allow_delete", "Allow Delete Resources"],
          ].map(([field, label]) => (
            <div key={field} className="flex items-center justify-between">
              <span>{label}</span>
              <input
                type="checkbox"
                checked={policy[field]}
                onChange={(e) => handleChange(field, e.target.checked)}
              />
            </div>
          ))}
        </div>
      </Card>

      {/* Safety Controls */}
      <Card title="Safety Controls">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium">
              Max Resources Per Day
            </label>
            <input
              type="number"
              value={policy.max_resources_per_day}
              onChange={(e) =>
                handleChange("max_resources_per_day", Number(e.target.value))
              }
              className="border p-2 rounded w-full"
            />
          </div>

          <div className="flex items-center justify-between">
            <span>Require Approval</span>
            <input
              type="checkbox"
              checked={policy.require_approval}
              onChange={(e) =>
                handleChange("require_approval", e.target.checked)
              }
            />
          </div>

          <div className="flex items-center justify-between">
            <span>Enable Kill Switch</span>
            <input
              type="checkbox"
              checked={policy.enable_kill_switch}
              onChange={(e) =>
                handleChange("enable_kill_switch", e.target.checked)
              }
            />
          </div>
        </div>
      </Card>
    </div>
  );
}