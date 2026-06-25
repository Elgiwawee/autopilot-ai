export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="mx-auto max-w-4xl px-4 py-16 space-y-10">
        <div>
          <h1 className="text-4xl font-semibold">Privacy Policy</h1>
          <p className="mt-3 text-muted-foreground">
            Effective date: [Add date]
          </p>
        </div>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">1. Information We Collect</h2>
          <p className="leading-7 text-muted-foreground">
            We may collect account information, contact details, cloud account
            metadata, resource inventory data, logs, and feedback you provide.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">2. How We Use Information</h2>
          <p className="leading-7 text-muted-foreground">
            We use information to provide the service, discover cloud resources,
            generate recommendations, improve product quality, deliver support,
            and maintain security and auditability.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">3. Cloud Credentials</h2>
          <p className="leading-7 text-muted-foreground">
            Cloud credentials or service account data are used only to connect to
            supported cloud providers and operate the platform according to your permissions.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">4. Sharing</h2>
          <p className="leading-7 text-muted-foreground">
            We do not sell your personal information. We may share limited data
            with service providers that help us operate the platform, comply with law,
            or protect the service.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">5. Data Retention</h2>
          <p className="leading-7 text-muted-foreground">
            We retain information as long as needed to provide the service, comply
            with legal obligations, resolve disputes, and maintain security logs.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">6. Security</h2>
          <p className="leading-7 text-muted-foreground">
            We use administrative, technical, and organizational safeguards to help
            protect data. No system is perfectly secure, so least-privilege access is recommended.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">7. Your Choices</h2>
          <p className="leading-7 text-muted-foreground">
            You may request access, correction, deletion, or export of your data
            depending on your account setup and applicable law.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">8. Updates</h2>
          <p className="leading-7 text-muted-foreground">
            We may update this policy from time to time. Material changes will be posted on this page.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">9. Contact</h2>
          <p className="leading-7 text-muted-foreground">
            For privacy questions, contact: privacy@autopilotops.cloud
          </p>
        </section>
      </div>
    </div>
  );
}