// src/pages/TermsOfUse.jsx

const sections = [
  {
    number: "01",
    title: "Acceptance of Terms",
    body: "By accessing or using Autopilot, you agree to these Terms of Use and any additional policies referenced here. If you do not agree, you should not use the service.",
  },
  {
    number: "02",
    title: "Service Description",
    body: "Autopilot is a cloud optimization platform that helps users discover cloud resources, identify savings opportunities, and support safe execution based on the permissions and automation mode they choose.",
  },
  {
    number: "03",
    title: "Accounts and Access",
    body: "You are responsible for the accuracy, confidentiality, and security of your account credentials. You also confirm that you have the authority to connect any cloud account or resource you submit to the platform.",
  },
  {
    number: "04",
    title: "Acceptable Use",
    body: "You agree not to misuse the service, attempt unauthorized access, interfere with platform operations, or connect resources without proper authorization. You must use the service in compliance with applicable laws and policies.",
  },
  {
    number: "05",
    title: "Automation and Risk",
    body: "Any recommendation or automated action should be reviewed according to your organization’s policies and risk tolerance. You remain responsible for deciding what level of automation is appropriate for your environment.",
  },
  {
    number: "06",
    title: "Intellectual Property",
    body: "The platform, branding, design, text, graphics, and software are owned by or licensed to us and are protected by applicable intellectual property laws. You may not copy, modify, distribute, or reuse them except as permitted by law or written agreement.",
  },
  {
    number: "07",
    title: "Limitation of Liability",
    body: "To the fullest extent permitted by law, the service is provided on an as-is and as-available basis. We are not liable for indirect, incidental, special, or consequential damages arising from your use of the service.",
  },
  {
    number: "08",
    title: "Changes to These Terms",
    body: "We may update these Terms of Use from time to time. When we do, the revised version will be posted on this page. Continued use of the service after the effective date means you accept the updated terms.",
  },
  {
    number: "09",
    title: "Contact Us",
    body: "If you have questions about these Terms of Use, contact us at legal@autopilotops.cloud.",
  },
];

function NumberBadge({ number }) {
  return (
    <div className="h-11 w-11 shrink-0 rounded-full border border-border bg-background flex items-center justify-center shadow-sm">
      <span className="text-xs font-semibold tracking-[0.2em] text-primary">{number}</span>
    </div>
  );
}

function TermsCard({ number, title, body }) {
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

export default function TermsOfUse() {
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
                Terms of Use
              </h1>
              <p className="text-base sm:text-lg leading-8 text-muted-foreground max-w-2xl">
                These terms govern your access to and use of Autopilot, including related services, features, and policies.
              </p>
              <div className="inline-flex items-center rounded-full border border-border bg-background/80 px-4 py-2 text-sm text-muted-foreground shadow-sm">
                Effective date: [Add date]
              </div>
            </div>
          </div>

          <div className="px-6 sm:px-10 py-8 sm:py-10 space-y-5 sm:space-y-6">
            {sections.map((section) => (
              <TermsCard key={section.number} {...section} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}