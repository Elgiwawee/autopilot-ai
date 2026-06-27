import { useEffect, useState } from "react";
import toast from "react-hot-toast";

import { getPolicy, updatePolicy } from "../api/policies.api";

import Spinner from "../components/ui/Spinner";

import PolicySection from "../components/policies/PolicySection";
import PolicySwitch from "../components/policies/PolicySwitch";
import PolicySlider from "../components/policies/PolicySlider";
import PolicyNumberInput from "../components/policies/PolicyNumberInput";

export default function Policies() {
  const [policy, setPolicy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadPolicy();
  }, []);

  async function loadPolicy() {
    try {
      const data = await getPolicy();
      setPolicy(data);
    } catch {
      toast.error("Unable to load policy");
    } finally {
      setLoading(false);
    }
  }

  async function save(changes) {
    setSaving(true);

    try {
      const updated = await updatePolicy(changes);

      setPolicy(updated);

      toast.success("Policy updated");
    } catch (err) {
      console.error(err);
      toast.error("Failed to update policy");
    } finally {
      setSaving(false);
    }
  }

  async function handleChange(field, value) {
    setPolicy((prev) => ({
      ...prev,
      [field]: value,
    }));

    await save({
      [field]: value,
    });
  }

  if (loading) return <Spinner />;

  return (
    <div className="max-w-6xl mx-auto space-y-8">

      <div className="flex items-center justify-between">

        <div>
          <h1 className="text-3xl font-semibold">
            Autopilot Policies
          </h1>

          <p className="text-muted-foreground mt-2">
            Configure how Autopilot is allowed to optimize your cloud
            infrastructure.
          </p>
        </div>

        <div className="text-sm text-muted-foreground">
          {saving ? "Saving..." : "All changes saved"}
        </div>

      </div>

      {/* ------------------------------------------------ */}

      <PolicySection
        title="Execution Mode"
        description="Choose how Autopilot behaves when recommendations are generated."
      >

        <PolicySwitch
          label="Require Approval"
          description="Every optimization must be approved before execution."
          checked={policy.require_approval}
          onChange={(v) => handleChange("require_approval", v)}
        />

        <PolicySwitch
          label="Kill Switch"
          description="Immediately stop all automated actions."
          checked={policy.enable_kill_switch}
          onChange={(v) => handleChange("enable_kill_switch", v)}
        />

      </PolicySection>

      {/* ------------------------------------------------ */}

      <PolicySection
        title="Financial Guardrails"
        description="Prevent Autopilot from making excessive cost changes."
      >

        <PolicySlider
          label="Maximum Monthly Savings"
          description="Maximum percentage of cloud spend Autopilot may optimize."
          value={policy.max_monthly_savings_pct}
          min={1}
          max={100}
          suffix="%"
          onChange={(v) =>
            handleChange("max_monthly_savings_pct", v)
          }
        />

      </PolicySection>

      {/* ------------------------------------------------ */}

      <PolicySection
        title="Execution Limits"
        description="Limit the number of resources Autopilot may modify."
      >

        <PolicyNumberInput
          label="Maximum Resources Per Day"
          description="Limits execution blast radius."
          value={policy.max_resources_per_day}
          min={1}
          onChange={(v) =>
            handleChange("max_resources_per_day", v)
          }
        />

      </PolicySection>

      {/* ------------------------------------------------ */}

      <PolicySection
        title="Allowed Actions"
        description="Choose which infrastructure actions Autopilot is allowed to perform."
      >

        <PolicySwitch
          label="Stop Compute Resources"
          description="Allow stopping EC2 instances or Virtual Machines."
          checked={policy.allow_stop}
          onChange={(v) => handleChange("allow_stop", v)}
        />

        <PolicySwitch
          label="Resize Resources"
          description="Allow CPU, memory or instance resizing."
          checked={policy.allow_resize}
          onChange={(v) => handleChange("allow_resize", v)}
        />

        <PolicySwitch
          label="Delete Resources"
          description="Allow deletion of idle resources."
          checked={policy.allow_delete}
          onChange={(v) => handleChange("allow_delete", v)}
        />

      </PolicySection>

      {/* ------------------------------------------------ */}

      <PolicySection
        title="Advanced Safety"
        description="Additional organization-wide execution controls."
      >

        <PolicyNumberInput
          label="Maximum Concurrent Executions"
          description="Maximum optimization tasks running simultaneously."
          value={policy.max_concurrent_actions}
          min={1}
          onChange={(v) =>
            handleChange("max_concurrent_actions", v)
          }
        />

        <PolicyNumberInput
          label="Approval Timeout"
          description="Pending approvals expire automatically."
          value={policy.approval_timeout_minutes}
          suffix="min"
          min={1}
          onChange={(v) =>
            handleChange("approval_timeout_minutes", v)
          }
        />

      </PolicySection>

    </div>
  );
}