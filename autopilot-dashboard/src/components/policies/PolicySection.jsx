export default function PolicySection({
  title,
  description,
  children,
}) {
  return (
    <div className="rounded-3xl border border-border bg-card shadow-sm">
      <div className="border-b border-border px-8 py-6">
        <h2 className="text-xl font-semibold">
          {title}
        </h2>

        {description && (
          <p className="mt-2 text-sm text-muted-foreground">
            {description}
          </p>
        )}
      </div>

      <div className="p-8">
        {children}
      </div>
    </div>
  );
}