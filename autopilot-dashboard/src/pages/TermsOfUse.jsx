export default function TermsOfUse() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="mx-auto max-w-4xl px-4 py-16 space-y-10">
        <div>
          <h1 className="text-4xl font-semibold">Terms of Use</h1>
          <p className="mt-3 text-muted-foreground">
            Effective date: [Add date]
          </p>
        </div>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">1. Acceptance of Terms</h2>
          <p className="leading-7 text-muted-foreground">
            By accessing or using Autopilot AI, you agree to these Terms of Use
            and any related policies. If you do not agree, do not use the service.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">2. Service Description</h2>
          <p className="leading-7 text-muted-foreground">
            Autopilot AI is a cloud optimization platform that helps discover
            resources, identify savings opportunities, and support safe execution
            based on your permissions and selected mode.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">3. Accounts and Access</h2>
          <p className="leading-7 text-muted-foreground">
            You are responsible for the accuracy and security of your account and
            for ensuring you have authority to connect any cloud account you submit.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">4. Acceptable Use</h2>
          <p className="leading-7 text-muted-foreground">
            You agree not to misuse the service, attempt unauthorized access,
            interfere with the platform, or connect resources without proper permission.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">5. Automation and Risk</h2>
          <p className="leading-7 text-muted-foreground">
            Any recommended or automated action should be reviewed according to
            your organization’s policies. You remain responsible for approving the
            level of automation that suits your environment.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">6. Limitation of Liability</h2>
          <p className="leading-7 text-muted-foreground">
            To the fullest extent permitted by law, the service is provided on an
            as-is and as-available basis. We are not liable for indirect, incidental,
            special, or consequential damages arising from your use of the service.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">7. Changes</h2>
          <p className="leading-7 text-muted-foreground">
            We may update these terms from time to time. Continued use after updates
            become effective means you accept the revised terms.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">8. Contact</h2>
          <p className="leading-7 text-muted-foreground">
            For questions, contact: legal@autopilotops.cloud
          </p>
        </section>
      </div>
    </div>
  );
}