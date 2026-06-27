export default function PolicyNumberInput({
  label,
  description,
  value,
  onChange,
  suffix,
  min = 0,
  max,
}) {
  return (
    <div className="space-y-2">
      <div>
        <h4 className="font-medium">
          {label}
        </h4>

        {description && (
          <p className="text-sm text-muted-foreground">
            {description}
          </p>
        )}
      </div>

      <div className="flex items-center rounded-xl border border-border overflow-hidden w-56">
        <button
          type="button"
          className="px-4 py-3 hover:bg-muted transition"
          onClick={() => onChange(Math.max(min, value - 1))}
        >
          −
        </button>

        <input
          type="number"
          value={value}
          min={min}
          max={max}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full text-center bg-transparent outline-none"
        />

        <button
          type="button"
          className="px-4 py-3 hover:bg-muted transition"
          onClick={() =>
            onChange(max ? Math.min(max, value + 1) : value + 1)
          }
        >
          +
        </button>

        {suffix && (
          <div className="px-3 text-muted-foreground border-l border-border">
            {suffix}
          </div>
        )}
      </div>
    </div>
  );
}