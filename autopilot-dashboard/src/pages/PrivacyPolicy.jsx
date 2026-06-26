// src/pages/PrivacyPolocy.jsx

const sections = [
  {
    number: "01",
    title: "Information We Collect",
    body: "We may collect information you provide directly, such as account details, contact information, organization details, support messages, and feedback. We may also collect cloud connection metadata, resource inventory data, configuration details, logs, usage data, and other information needed to operate the platform.",
  },
  {
    number: "02",
    title: "How We Use Information",
    body: "We use information to provide and improve the service, connect cloud accounts, identify optimization opportunities, generate recommendations, support security and auditability, respond to requests, and maintain the overall reliability of the platform.",
  },
  {
    number: "03",
    title: "Cloud Credentials and Access",
    body: "Any cloud credentials, tokens, or service account data used to connect your environment are handled only for the purpose of operating the platform according to the permissions you grant. We recommend least-privilege access for every integration.",
  },
  {
    number: "04",
    title: "Sharing of Information",
    body: "We do not sell your personal information. We may share limited information with trusted service providers that help us host, support, secure, or improve the platform, as well as when required by law or necessary to protect our users and services.",
  },
  {
    number: "05",
    title: "Data Retention",
    body: "We retain information for as long as needed to provide the service, meet legal and compliance obligations, resolve disputes, maintain security records, and support legitimate business operations.",
  },
  {
    number: "06",
    title: "Security",
    body: "We use administrative, technical, and organizational safeguards designed to protect information and reduce risk. No system is completely secure, so we encourage strong account security, limited access, and careful review of permissions.",
  },
  {
    number: "07",
    title: "Your Choices and Rights",
    body: "Depending on your account settings and applicable law, you may request access, correction, deletion, or export of your data. You may also manage certain preferences through your account or by contacting us directly.",
  },
  {
    number: "08",
    title: "Changes to This Policy",
    body: "We may update this Privacy Policy from time to time. If we make material changes, we will post the updated version on this page and revise the effective date where appropriate.",
  },
  {
    number: "09",
    title: "Contact Us",
    body: "If you have questions about this Privacy Policy or how your data is handled, contact us at privacy@autopilotops.cloud.",
  },
];

function NumberBadge({ number }) {
  return (
    <div className="h-11 w-11 shrink-0 rounded-full border border-border bg-background flex items-center justify-center shadow-sm">
      <span className="text-xs font-semibold tracking-[0.2em] text-primary">{number}</span>
    </div>
  );
}

function PolicyCard({ number, title, body }) {
  return (
    <section className="rounded-[1.75rem] border border-border bg-card p-6 sm:p-7 shadow-sm transition hover:shadow-md">
      <div className="flex items-start gap-4">
        <NumberBadge number={number} />
        <div className="min-w-0 flex-1">
          <h2 className="text-xl sm:text-2xl font-semibold tracking-tight">{title}</h2>
          <p className="mt-3 leading-7 text-muted-foreground">{body}</p>
        </div>
      </div>
    </section>
  );
}

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-12 sm:py-16 lg:py-20">
        <div className="rounded-[2.25rem] border border-border bg-card shadow-2xl shadow-black/5 overflow-hidden">
          <div className="relative px-6 sm:px-10 py-10 sm:py-12 border-b border-border bg-[radial-gradient(circle_at_top_right,rgba(59,130,246,0.12),transparent_38%),linear-gradient(180deg,rgba(255,255,255,0.02),rgba(255,255,255,0))]">
            <div className="max-w-3xl space-y-4">
              <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">
                Legal
              </p>
              <h1 className="text-4xl sm:text-5xl font-semibold tracking-tight">
                Privacy Policy
              </h1>
              <p className="text-base sm:text-lg leading-8 text-muted-foreground max-w-2xl">
                This policy explains how Autopilot collects, uses, shares, and protects information when you use our platform.
              </p>
              <div className="inline-flex items-center rounded-full border border-border bg-background/80 px-4 py-2 text-sm text-muted-foreground shadow-sm">
                Effective date: [Add date]
              </div>
            </div>
          </div>

          <div className="px-6 sm:px-10 py-8 sm:py-10 space-y-5 sm:space-y-6">
            {sections.map((section) => (
              <PolicyCard key={section.number} {...section} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
