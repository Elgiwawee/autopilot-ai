// src/pages/settings/CloudAccounts.jsx

import { useEffect, useState } from "react";
import {
  fetchCloudAccounts,
  createCloudAccount,
  disableCloudAccount,
} from "../../api/cloudAccounts";

export default function CloudAccountsPage() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [form, setForm] = useState({
    provider_code: "aws",
    account_identifier: "",
    role_arn: "",
    tenant_id: "",
    client_id: "",
    client_secret: "",
    subscription_id: "",
    project_id: "",
    service_account_json: "",
    mode: "observe",
  });

  useEffect(() => {
    loadAccounts();
  }, []);

  async function loadAccounts() {
    try {
      const res = await fetchCloudAccounts();
      setAccounts(res || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate(e) {
    e.preventDefault();
    setSubmitting(true);

    try {
      const payload = { ...form };

      // ✅ Parse JSON safely for GCP
      if (form.provider_code === "gcp" && form.service_account_json) {
        payload.service_account_json = JSON.parse(form.service_account_json);
      }

      const newAccount = await createCloudAccount(payload);

      setAccounts(prev => [...prev, newAccount]);
      setShowModal(false);

      // reset
      setForm({
        provider_code: "aws",
        account_identifier: "",
        role_arn: "",
        tenant_id: "",
        client_id: "",
        client_secret: "",
        subscription_id: "",
        project_id: "",
        service_account_json: "",
        mode: "observe",
      });

      alert("✅ Cloud account connected successfully");
    } catch (err) {
      console.error(err);
      alert("❌ Failed to connect account");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDisable(id) {
    if (!window.confirm("Disable this cloud account?")) return;

    try {
      await disableCloudAccount(id);
      setAccounts(prev => prev.filter(acc => acc.id !== id));
    } catch (err) {
      console.error(err);
    }
  }

  // ---------------------------------------
  // 🎯 PROVIDER ICONS
  // ---------------------------------------
  const providerIcon = code => {
    if (code === "aws") return "🟠";
    if (code === "azure") return "🔵";
    if (code === "gcp") return "🟢";
    return "☁️";
  };

  // ---------------------------------------
  // 🎯 PROVIDER DYNAMIC FIELDS
  // ---------------------------------------
  function ProviderFields() {
    switch (form.provider_code) {
      case "aws":
        return (
          <div>
            <label className="text-sm">Role ARN</label>
            <input
              className="input"
              placeholder="arn:aws:iam::123456789:role/..."
              value={form.role_arn}
              onChange={e =>
                setForm({ ...form, role_arn: e.target.value })
              }
            />
          </div>
        );

      case "azure":
        return (
          <div className="space-y-2">
            <input
              className="input"
              placeholder="Tenant ID"
              onChange={e =>
                setForm({ ...form, tenant_id: e.target.value })
              }
            />
            <input
              className="input"
              placeholder="Client ID"
              onChange={e =>
                setForm({ ...form, client_id: e.target.value })
              }
            />
            <input
              className="input"
              placeholder="Client Secret"
              onChange={e =>
                setForm({ ...form, client_secret: e.target.value })
              }
            />
            <input
              className="input"
              placeholder="Subscription ID"
              onChange={e =>
                setForm({ ...form, subscription_id: e.target.value })
              }
            />
          </div>
        );

      case "gcp":
        return (
          <div className="space-y-2">
            <input
              className="input"
              placeholder="Project ID"
              onChange={e =>
                setForm({ ...form, project_id: e.target.value })
              }
            />

            <textarea
              className="input h-28"
              placeholder="Paste Service Account JSON"
              value={form.service_account_json}
              onChange={e =>
                setForm({
                  ...form,
                  service_account_json: e.target.value,
                })
              }
            />
          </div>
        );

      default:
        return null;
    }
  }

  return (
    <>
      {/* HEADER */}
      <div className="flex justify-between items-center mb-6">
        <div className="text-sm text-muted">
          Manage connected cloud environments
        </div>

        <button onClick={() => setShowModal(true)} className="btn-primary">
          + Connect Cloud Account
        </button>
      </div>

      {/* LOADING */}
      {loading ? (
        <div className="text-muted">Loading...</div>
      ) : accounts.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-5xl mb-4">☁️</div>
          <h2 className="text-lg font-semibold mb-2">
            No Cloud Accounts Connected
          </h2>
          <p className="text-muted mb-4">
            Connect your first account to start optimization
          </p>
          <button
            onClick={() => setShowModal(true)}
            className="btn-primary"
          >
            + Connect Cloud Account
          </button>
        </div>
      ) : (
        <table className="w-full border-collapse">
          <thead className="text-muted text-sm border-b">
            <tr>
              <th className="text-left py-3">Provider</th>
              <th className="text-left py-3">Account ID</th>
              <th className="text-left py-3">Mode</th>
              <th className="text-left py-3">Status</th>
              <th className="text-left py-3">Connected</th>
              <th className="text-right py-3">Actions</th>
            </tr>
          </thead>

          <tbody>
            {accounts.map(acc => (
              <tr key={acc.id} className="border-b">
                <td className="py-3 flex items-center gap-2">
                  {providerIcon(acc.provider_code)}
                  <span className="capitalize">{acc.provider}</span>
                </td>

                <td className="py-3 font-mono text-sm">
                  {acc.account_identifier}
                </td>

                <td className="py-3 text-xs">
                  <span className="px-2 py-1 bg-muted/20 rounded">
                    {acc.mode}
                  </span>
                </td>

                <td className="py-3 text-success text-sm">
                  ● {acc.status}
                </td>

                <td className="py-3 text-sm text-muted">
                  {new Date(acc.created_at).toLocaleDateString()}
                </td>

                <td className="py-3 text-right">
                  <button
                    onClick={() => handleDisable(acc.id)}
                    className="text-danger hover:underline text-sm"
                  >
                    Disable
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* MODAL */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center">
          <div className="bg-surface p-6 rounded-lg w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">
              Connect Cloud Account
            </h3>

            <form onSubmit={handleCreate} className="space-y-4">

              {/* Provider */}
              <select
                className="input"
                value={form.provider_code}
                onChange={e =>
                  setForm({ ...form, provider_code: e.target.value })
                }
              >
                <option value="aws">AWS</option>
                <option value="azure">Azure</option>
                <option value="gcp">GCP</option>
              </select>

              {/* Account ID */}
              <input
                className="input"
                placeholder="Account Identifier"
                required
                value={form.account_identifier}
                onChange={e =>
                  setForm({
                    ...form,
                    account_identifier: e.target.value,
                  })
                }
              />

              {/* Dynamic Fields */}
              <ProviderFields />

              {/* Mode */}
              <select
                className="input"
                value={form.mode}
                onChange={e =>
                  setForm({ ...form, mode: e.target.value })
                }
              >
                <option value="observe">Observe</option>
                <option value="recommend">Recommend</option>
                <option value="autopilot">Autopilot</option>
              </select>

              {/* Actions */}
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={submitting}
                  className="btn-primary"
                >
                  {submitting ? "Connecting..." : "Connect"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}