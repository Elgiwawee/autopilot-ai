// src/pages/settings/CloudAccounts.jsx

import { useEffect, useMemo, useState } from "react";

import {
  fetchCloudAccounts,
  createCloudAccount,
  disableCloudAccount,
} from "../../api/cloudAccounts";

import {
  Cloud,
  Shield,
  ShieldAlert,
  Bot,
  Plus,
  Trash2,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  PauseCircle,
} from "lucide-react";

export default function CloudAccountsPage() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);

  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [form, setForm] = useState({
    provider_code: "aws",
    account_identifier: "",
    role_arn: "",
    external_id: "",
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
      const data = await fetchCloudAccounts();
      setAccounts(data || []);
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
      const payload = {
        ...form,
      };

      if (
        form.provider_code === "gcp" &&
        form.service_account_json
      ) {
        payload.service_account_json = JSON.parse(
          form.service_account_json
        );
      }

      const created = await createCloudAccount(payload);

      setAccounts(prev => [created, ...prev]);

      setShowModal(false);

      setForm({
        provider_code: "aws",
        account_identifier: "",
        role_arn: "",
        external_id: "",
        tenant_id: "",
        client_id: "",
        client_secret: "",
        subscription_id: "",
        project_id: "",
        service_account_json: "",
        mode: "observe",
      });

    } catch (err) {
      console.error(err);

      alert(
        err?.response?.data?.detail ||
          "Failed to connect cloud account"
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDisable(id) {
    const confirmed = window.confirm(
      "Disable this cloud account?"
    );

    if (!confirmed) return;

    try {
      await disableCloudAccount(id);

      setAccounts(prev =>
        prev.filter(acc => acc.id !== id)
      );
    } catch (err) {
      console.error(err);
    }
  }

  const stats = useMemo(() => {
    return {
      total: accounts.length,
      autopilot: accounts.filter(
        a => a.mode === "autopilot"
      ).length,
      recommend: accounts.filter(
        a => a.mode === "recommend"
      ).length,
      observe: accounts.filter(
        a => a.mode === "observe"
      ).length,
    };
  }, [accounts]);

  function providerIcon(code) {
    switch (code?.toLowerCase()) {
      case "aws":
        return "🟠";

      case "azure":
        return "🔵";

      case "gcp":
        return "🟢";

      default:
        return "☁️";
    }
  }

  function statusBadge(status) {
    switch (status) {
      case "connected":
      case "active":
        return (
          <span className="flex items-center gap-1 text-emerald-400 text-xs">
            <CheckCircle2 size={14} />
            Connected
          </span>
        );

      case "pending":
        return (
          <span className="flex items-center gap-1 text-yellow-400 text-xs">
            <Loader2 size={14} className="animate-spin" />
            Pending
          </span>
        );

      case "failed":
        return (
          <span className="flex items-center gap-1 text-red-400 text-xs">
            <AlertTriangle size={14} />
            Failed
          </span>
        );

      default:
        return (
          <span className="flex items-center gap-1 text-gray-400 text-xs">
            <PauseCircle size={14} />
            Disabled
          </span>
        );
    }
  }

  function modeBadge(mode) {
    switch (mode) {
      case "autopilot":
        return (
          <div className="flex items-center gap-1 bg-primary/20 text-primary px-2 py-1 rounded-full text-xs">
            <Bot size={14} />
            Autopilot
          </div>
        );

      case "recommend":
        return (
          <div className="flex items-center gap-1 bg-yellow-500/10 text-yellow-400 px-2 py-1 rounded-full text-xs">
            <ShieldAlert size={14} />
            Recommend
          </div>
        );

      default:
        return (
          <div className="flex items-center gap-1 bg-muted/20 text-muted px-2 py-1 rounded-full text-xs">
            <Shield size={14} />
            Observe
          </div>
        );
    }
  }

  function ProviderFields() {
    switch (form.provider_code) {
      case "aws":
        return (
          <div className="space-y-3">

            <input
              className="input"
              placeholder="Role ARN"
              value={form.role_arn}
              onChange={e =>
                setForm({
                  ...form,
                  role_arn: e.target.value,
                })
              }
            />

            <input
              className="input"
              placeholder="External ID"
              value={form.external_id}
              onChange={e =>
                setForm({
                  ...form,
                  external_id: e.target.value,
                })
              }
            />
          </div>
        );

      case "azure":
        return (
          <div className="space-y-3">

            <input
              className="input"
              placeholder="Tenant ID"
              onChange={e =>
                setForm({
                  ...form,
                  tenant_id: e.target.value,
                })
              }
            />

            <input
              className="input"
              placeholder="Client ID"
              onChange={e =>
                setForm({
                  ...form,
                  client_id: e.target.value,
                })
              }
            />

            <input
              className="input"
              placeholder="Client Secret"
              onChange={e =>
                setForm({
                  ...form,
                  client_secret: e.target.value,
                })
              }
            />

            <input
              className="input"
              placeholder="Subscription ID"
              onChange={e =>
                setForm({
                  ...form,
                  subscription_id: e.target.value,
                })
              }
            />
          </div>
        );

      case "gcp":
        return (
          <div className="space-y-3">

            <input
              className="input"
              placeholder="Project ID"
              onChange={e =>
                setForm({
                  ...form,
                  project_id: e.target.value,
                })
              }
            />

            <textarea
              className="input min-h-[140px]"
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
    <div className="space-y-8">

      {/* HEADER */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">

        <div>
          <h1 className="text-2xl font-semibold">
            Cloud Accounts
          </h1>

          <p className="text-sm text-muted mt-1">
            Connect and manage multi-cloud infrastructure
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={16} />
          Connect Account
        </button>
      </div>

      {/* STATS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">

        <div className="bg-panel border border-border rounded-xl p-5">
          <div className="text-sm text-muted mb-1">
            Total Accounts
          </div>

          <div className="text-2xl font-semibold">
            {stats.total}
          </div>
        </div>

        <div className="bg-panel border border-border rounded-xl p-5">
          <div className="text-sm text-muted mb-1">
            Autopilot
          </div>

          <div className="text-2xl font-semibold text-primary">
            {stats.autopilot}
          </div>
        </div>

        <div className="bg-panel border border-border rounded-xl p-5">
          <div className="text-sm text-muted mb-1">
            Recommend
          </div>

          <div className="text-2xl font-semibold text-yellow-400">
            {stats.recommend}
          </div>
        </div>

        <div className="bg-panel border border-border rounded-xl p-5">
          <div className="text-sm text-muted mb-1">
            Observe
          </div>

          <div className="text-2xl font-semibold">
            {stats.observe}
          </div>
        </div>

      </div>

      {/* EMPTY */}
      {!loading && accounts.length === 0 && (
        <div className="bg-panel border border-border rounded-2xl py-24 text-center">

          <Cloud
            size={52}
            className="mx-auto mb-5 text-muted"
          />

          <h2 className="text-xl font-semibold mb-2">
            No Cloud Accounts Connected
          </h2>

          <p className="text-muted mb-6">
            Connect your first cloud environment
          </p>

          <button
            onClick={() => setShowModal(true)}
            className="btn-primary"
          >
            Connect Cloud Account
          </button>
        </div>
      )}

      {/* LOADING */}
      {loading && (
        <div className="flex justify-center py-20">
          <Loader2 className="animate-spin" />
        </div>
      )}

      {/* CARDS */}
      {!loading && accounts.length > 0 && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

          {accounts.map(account => (
            <div
              key={account.id}
              className="bg-panel border border-border rounded-2xl p-6"
            >

              <div className="flex items-start justify-between">

                <div>
                  <div className="flex items-center gap-2 mb-2">

                    <span className="text-xl">
                      {providerIcon(account.provider_code)}
                    </span>

                    <h2 className="font-semibold text-lg">
                      {account.provider}
                    </h2>

                  </div>

                  <div className="font-mono text-sm text-muted">
                    {account.account_identifier}
                  </div>
                </div>

                {statusBadge(account.status)}

              </div>

              <div className="mt-5 flex items-center gap-3">
                {modeBadge(account.mode)}
              </div>

              <div className="mt-6 flex items-center justify-between">

                <div className="text-xs text-muted">
                  Connected{" "}
                  {new Date(
                    account.created_at
                  ).toLocaleDateString()}
                </div>

                <button
                  onClick={() =>
                    handleDisable(account.id)
                  }
                  className="flex items-center gap-1 text-danger hover:opacity-80 text-sm"
                >
                  <Trash2 size={14} />
                  Disable
                </button>

              </div>

            </div>
          ))}

        </div>
      )}

      {/* MODAL */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">

          <div className="bg-panel border border-border rounded-2xl w-full max-w-lg p-6">

            <div className="flex items-center justify-between mb-6">

              <div>
                <h2 className="text-xl font-semibold">
                  Connect Cloud Account
                </h2>

                <p className="text-sm text-muted mt-1">
                  Add infrastructure securely
                </p>
              </div>

            </div>

            <form
              onSubmit={handleCreate}
              className="space-y-4"
            >

              <select
                className="input"
                value={form.provider_code}
                onChange={e =>
                  setForm({
                    ...form,
                    provider_code: e.target.value,
                  })
                }
              >
                <option value="aws">AWS</option>
                <option value="azure">Azure</option>
                <option value="gcp">Google Cloud</option>
              </select>

              <input
                required
                className="input"
                placeholder="Account Identifier"
                value={form.account_identifier}
                onChange={e =>
                  setForm({
                    ...form,
                    account_identifier:
                      e.target.value,
                  })
                }
              />

              <ProviderFields />

              <select
                className="input"
                value={form.mode}
                onChange={e =>
                  setForm({
                    ...form,
                    mode: e.target.value,
                  })
                }
              >
                <option value="observe">
                  Observe
                </option>

                <option value="recommend">
                  Recommend
                </option>

                <option value="autopilot">
                  Autopilot
                </option>
              </select>

              <div className="flex justify-end gap-3 pt-4">

                <button
                  type="button"
                  onClick={() =>
                    setShowModal(false)
                  }
                  className="btn-secondary"
                >
                  Cancel
                </button>

                <button
                  disabled={submitting}
                  type="submit"
                  className="btn-primary"
                >
                  {submitting
                    ? "Connecting..."
                    : "Connect Account"}
                </button>

              </div>

            </form>

          </div>

        </div>
      )}
    </div>
  );
}