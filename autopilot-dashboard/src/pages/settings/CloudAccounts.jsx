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
  X,
  ChevronRight,
  ExternalLink,
  Info,
  CircleCheckBig,
  CircleDashed,
} from "lucide-react";

const PROVIDER_GUIDES = {
  aws: {
    title: "Connect AWS to Autopilot",
    subtitle:
      "Autopilot needs an IAM role to discover AWS resources and prepare optimizations.",
    steps: [
      "Go to AWS IAM and create or choose a role for Autopilot.",
      "Attach read permissions for discovery. Add execution permissions later if you want Autopilot to apply changes.",
      "Set the trust policy so your Autopilot AWS principal can assume the role.",
      "Copy the Role ARN and External ID into the form.",
      "Submit the account, then wait for discovery to sync resources into Autopilot.",
    ],
    required: [
      { key: "account_identifier", label: "Account Identifier", sample: "123456789012" },
      { key: "role_arn", label: "Role ARN", sample: "arn:aws:iam::123456789012:role/AutopilotAccessRole" },
      { key: "external_id", label: "External ID", sample: "autopilot-external-9f2a" },
    ],
    tip: "Without the role permissions, Autopilot can connect but cannot discover or optimize resources.",
  },
  azure: {
    title: "Connect Azure to Autopilot",
    subtitle:
      "Autopilot needs an Azure app registration and subscription permissions before it can discover or optimize resources.",
    steps: [
      "Go to Microsoft Entra ID and create a new App Registration for Autopilot.",
      "Create a client secret and copy it immediately.",
      "Assign the app at least the Reader role on the subscription for discovery.",
      "Add Virtual Machine Contributor later if you want Autopilot to execute VM actions.",
      "Copy Tenant ID, Client ID, Client Secret, and Subscription ID into the form.",
      "Submit the account and let Autopilot run discovery.",
    ],
    required: [
      { key: "account_identifier", label: "Account Identifier", sample: "autopilot-azure-prod" },
      { key: "tenant_id", label: "Tenant ID", sample: "2f8f1b7d-1234-4b7a-9f8a-111111111111" },
      { key: "client_id", label: "Client ID", sample: "7c9f2d4a-2222-4f1a-9b2d-222222222222" },
      { key: "client_secret", label: "Client Secret", sample: "xYz12345-super-secret-value" },
      { key: "subscription_id", label: "Subscription ID", sample: "9b3d7f21-3333-4444-aaaa-333333333333" },
    ],
    tip: "Azure needs both credentials and RBAC permissions before discovery and optimization can work.",
  },
  gcp: {
    title: "Connect GCP to Autopilot",
    subtitle:
      "Autopilot uses a service account JSON key and required APIs to discover resources and calculate savings.",
    steps: [
      "Open Google Cloud Console and select the project you want Autopilot to manage.",
      "Enable Compute Engine API, Cloud Billing API, and Cloud Monitoring API.",
      "Create a service account for Autopilot.",
      "Grant it Compute Viewer for discovery. Add more permissions later if you want execution.",
      "Generate a JSON key and paste it into the form.",
      "Enter the Project ID and connect the account.",
    ],
    required: [
      { key: "account_identifier", label: "Account Identifier", sample: "autopilot-gcp-prod" },
      { key: "project_id", label: "Project ID", sample: "autopilotops-prod-123456" },
      {
        key: "service_account_json",
        label: "Service Account JSON",
        sample:
          '{\n  "type": "service_account",\n  "project_id": "autopilotops-prod-123456",\n  "client_email": "autopilot@autopilotops-prod-123456.iam.gserviceaccount.com"\n}',
      },
    ],
    tip: "If the required GCP APIs are not enabled, Autopilot will not be able to list resources or calculate pricing correctly.",
  },
};

const INITIAL_FORM = {
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
};

export default function CloudAccountsPage() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);

  const [showModal, setShowModal] = useState(false);
  const [showGuide, setShowGuide] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [form, setForm] = useState(INITIAL_FORM);

  useEffect(() => {
    loadAccounts();
  }, []);

  const guide = PROVIDER_GUIDES[form.provider_code] || PROVIDER_GUIDES.aws;

  const requiredFields = useMemo(() => guide.required, [guide]);
  const missingFields = useMemo(() => {
    return requiredFields.filter(({ key }) => !String(form[key] || "").trim());
  }, [form, requiredFields]);

  const readiness = useMemo(() => {
    const total = requiredFields.length;
    const filled = total - missingFields.length;
    return {
      total,
      filled,
      complete: total > 0 && missingFields.length === 0,
      percent: total === 0 ? 0 : Math.round((filled / total) * 100),
    };
  }, [requiredFields, missingFields]);

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

  function resetForm() {
    setForm(INITIAL_FORM);
    setShowGuide(true);
  }

  function openModal() {
    setShowModal(true);
    setShowGuide(true);
  }

  function closeModal() {
    setShowModal(false);
    resetForm();
  }

  async function handleCreate(e) {
    e.preventDefault();
    setSubmitting(true);

    try {
      const payload = { ...form };

      if (form.provider_code === "gcp" && form.service_account_json) {
        payload.service_account_json = JSON.parse(form.service_account_json);
      }

      const created = await createCloudAccount(payload);
      setAccounts((prev) => [created, ...prev]);
      closeModal();
    } catch (err) {
      console.error(err);
      alert(
        err?.response?.data?.detail ||
          err?.response?.data?.error ||
          "Failed to connect cloud account"
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDisable(id) {
    const confirmed = window.confirm("Disable this cloud account?");
    if (!confirmed) return;

    try {
      await disableCloudAccount(id);
      setAccounts((prev) => prev.filter((acc) => acc.id !== id));
    } catch (err) {
      console.error(err);
      alert("Failed to disable cloud account");
    }
  }

  const stats = useMemo(() => {
    return {
      total: accounts.length,
      autopilot: accounts.filter((a) => a.mode === "autopilot").length,
      recommend: accounts.filter((a) => a.mode === "recommend").length,
      observe: accounts.filter((a) => a.mode === "observe").length,
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

  function FieldStatus({ fieldKey, label }) {
    const value = String(form[fieldKey] || "").trim();
    const ok = Boolean(value);

    return (
      <div className="flex items-start gap-2 text-sm">
        {ok ? (
          <CircleCheckBig size={16} className="text-emerald-500 mt-0.5 shrink-0" />
        ) : (
          <CircleDashed size={16} className="text-muted mt-0.5 shrink-0" />
        )}
        <span className={ok ? "text-foreground" : "text-muted"}>{label}</span>
      </div>
    );
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
              onChange={(e) =>
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
              onChange={(e) =>
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
              value={form.tenant_id}
              onChange={(e) =>
                setForm({
                  ...form,
                  tenant_id: e.target.value,
                })
              }
            />

            <input
              className="input"
              placeholder="Client ID"
              value={form.client_id}
              onChange={(e) =>
                setForm({
                  ...form,
                  client_id: e.target.value,
                })
              }
            />

            <input
              className="input"
              placeholder="Client Secret"
              value={form.client_secret}
              onChange={(e) =>
                setForm({
                  ...form,
                  client_secret: e.target.value,
                })
              }
            />

            <input
              className="input"
              placeholder="Subscription ID"
              value={form.subscription_id}
              onChange={(e) =>
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
              value={form.project_id}
              onChange={(e) =>
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
              onChange={(e) =>
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
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Cloud Accounts</h1>
          <p className="text-sm text-muted mt-1">
            Connect and manage multi-cloud infrastructure
          </p>
        </div>

        <button
          onClick={openModal}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={16} />
          Connect Account
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-panel border border-border rounded-xl p-5">
          <div className="text-sm text-muted mb-1">Total Accounts</div>
          <div className="text-2xl font-semibold">{stats.total}</div>
        </div>

        <div className="bg-panel border border-border rounded-xl p-5">
          <div className="text-sm text-muted mb-1">Autopilot</div>
          <div className="text-2xl font-semibold text-primary">
            {stats.autopilot}
          </div>
        </div>

        <div className="bg-panel border border-border rounded-xl p-5">
          <div className="text-sm text-muted mb-1">Recommend</div>
          <div className="text-2xl font-semibold text-yellow-400">
            {stats.recommend}
          </div>
        </div>

        <div className="bg-panel border border-border rounded-xl p-5">
          <div className="text-sm text-muted mb-1">Observe</div>
          <div className="text-2xl font-semibold">{stats.observe}</div>
        </div>
      </div>

      {!loading && accounts.length === 0 && (
        <div className="bg-panel border border-border rounded-2xl py-24 text-center">
          <Cloud size={52} className="mx-auto mb-5 text-muted" />
          <h2 className="text-xl font-semibold mb-2">
            No Cloud Accounts Connected
          </h2>
          <p className="text-muted mb-6">
            Connect your first cloud environment
          </p>
          <button onClick={openModal} className="btn-primary">
            Connect Cloud Account
          </button>
        </div>
      )}

      {loading && (
        <div className="flex justify-center py-20">
          <Loader2 className="animate-spin" />
        </div>
      )}

      {!loading && accounts.length > 0 && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {accounts.map((account) => (
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
                  Connected {new Date(account.created_at).toLocaleDateString()}
                </div>

                <button
                  onClick={() => handleDisable(account.id)}
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

      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/50">
          <div className="absolute inset-y-0 right-0 w-full max-w-6xl bg-background border-l border-border shadow-2xl flex">
            <div className="flex-1 overflow-y-auto p-6 md:p-8">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-semibold">Connect Cloud Account</h2>
                  <p className="text-sm text-muted mt-1">
                    Add infrastructure securely
                  </p>
                </div>

                <button
                  onClick={closeModal}
                  className="p-2 rounded-full hover:bg-muted/20 transition"
                  aria-label="Close"
                >
                  <X size={18} />
                </button>
              </div>

              <form onSubmit={handleCreate} className="space-y-4">
                <div className="flex items-center gap-3">
                  <select
                    className="input flex-1"
                    value={form.provider_code}
                    onChange={(e) =>
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

                  <button
                    type="button"
                    onClick={() => setShowGuide((prev) => !prev)}
                    className="text-blue-600 hover:text-blue-500 text-sm font-medium flex items-center gap-1 whitespace-nowrap"
                  >
                    Learn more
                    <ChevronRight size={16} />
                  </button>
                </div>

                <input
                  required
                  className="input"
                  placeholder={
                    guide.required.find((f) => f.key === "account_identifier")?.sample ||
                    "Account Identifier"
                  }
                  value={form.account_identifier}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      account_identifier: e.target.value,
                    })
                  }
                />

                <ProviderFields />

                <select
                  className="input"
                  value={form.mode}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      mode: e.target.value,
                    })
                  }
                >
                  <option value="observe">Observe</option>
                  <option value="recommend">Recommend</option>
                  <option value="autopilot">Autopilot</option>
                </select>

                <div className="rounded-xl border border-border p-4 bg-muted/10">
                  <div className="text-sm font-medium mb-3">
                    Connection readiness
                  </div>

                  <div className="space-y-2 mb-4">
                    {requiredFields.map((field) => (
                      <FieldStatus
                        key={field.key}
                        fieldKey={field.key}
                        label={field.label}
                      />
                    ))}
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted">
                      {readiness.filled}/{readiness.total} required fields filled
                    </span>
                    <span className="font-medium">{readiness.percent}%</span>
                  </div>

                  <div className="mt-2 h-2 w-full rounded-full bg-muted overflow-hidden">
                    <div
                      className="h-full rounded-full bg-primary transition-all"
                      style={{ width: `${readiness.percent}%` }}
                    />
                  </div>
                </div>

                <div className="flex justify-end gap-3 pt-4">
                  <button
                    type="button"
                    onClick={closeModal}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>

                  <button
                    disabled={submitting || !readiness.complete}
                    type="submit"
                    className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {submitting ? "Connecting..." : "Connect Account"}
                  </button>
                </div>
              </form>
            </div>

            {showGuide && (
              <aside className="w-full max-w-xl border-l border-border bg-card overflow-y-auto p-6 md:p-8">
                <div className="flex items-start justify-between gap-4 mb-6">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Info size={18} className="text-blue-600" />
                      <h3 className="text-xl font-semibold">{guide.title}</h3>
                    </div>
                    <p className="text-sm text-muted">{guide.subtitle}</p>
                  </div>

                  <button
                    type="button"
                    onClick={() => setShowGuide(false)}
                    className="p-2 rounded-full hover:bg-muted/20 transition"
                    aria-label="Close guide"
                  >
                    <X size={18} />
                  </button>
                </div>

                <div className="space-y-6">
                  <div className="rounded-xl border border-border p-4 bg-background">
                    <div className="text-sm font-medium mb-2">
                      What you need to provide
                    </div>
                    <ul className="space-y-3 text-sm">
                      {guide.required.map((item) => {
                        const value = String(form[item.key] || "").trim();
                        const done = Boolean(value);

                        return (
                          <li key={item.key} className="space-y-1">
                            <div className="flex items-center gap-2">
                              {done ? (
                                <CircleCheckBig
                                  size={16}
                                  className="text-emerald-500 shrink-0"
                                />
                              ) : (
                                <CircleDashed
                                  size={16}
                                  className="text-muted shrink-0"
                                />
                              )}
                              <span className={done ? "text-foreground" : "text-muted"}>
                                {item.label}
                              </span>
                            </div>

                            <div className="ml-6 rounded-md border border-dashed border-border bg-muted/20 px-3 py-2 text-xs text-muted font-mono whitespace-pre-wrap">
                              Example: {item.sample}
                            </div>
                          </li>
                        );
                      })}
                    </ul>
                  </div>

                  <div className="rounded-xl border border-border p-4 bg-background">
                    <div className="text-sm font-medium mb-3">
                      Step-by-step setup
                    </div>

                    <ol className="space-y-3 text-sm text-muted">
                      {guide.steps.map((step, index) => (
                        <li key={step} className="flex gap-3">
                          <span className="mt-0.5 inline-flex h-6 w-6 items-center justify-center rounded-full bg-blue-600/10 text-blue-600 text-xs font-semibold shrink-0">
                            {index + 1}
                          </span>
                          <span>{step}</span>
                        </li>
                      ))}
                    </ol>
                  </div>

                  <div className="rounded-xl border border-border p-4 bg-blue-50/40">
                    <div className="text-sm font-medium mb-2 text-blue-700">
                      Important
                    </div>
                    <p className="text-sm text-muted">{guide.tip}</p>
                  </div>

                  <div className="rounded-xl border border-border p-4 bg-background">
                    <div className="text-sm font-medium mb-3">
                      What happens after you connect
                    </div>
                    <div className="space-y-2 text-sm text-muted">
                      <p>1. Autopilot validates the credentials.</p>
                      <p>2. Inventory sync discovers resources.</p>
                      <p>3. Pricing and metrics are collected.</p>
                      <p>4. Recommendations appear in Optimizer.</p>
                      <p>5. Savings start showing on the Savings page.</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 pt-2">
                    <a
                      href="#"
                      onClick={(e) => e.preventDefault()}
                      className="text-blue-600 hover:text-blue-500 text-sm font-medium flex items-center gap-1"
                    >
                      Documentation
                      <ExternalLink size={14} />
                    </a>
                  </div>
                </div>
              </aside>
            )}
          </div>
        </div>
      )}
    </div>
  );
}