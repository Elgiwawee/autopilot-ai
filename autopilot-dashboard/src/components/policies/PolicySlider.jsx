export default function PolicySlider({
  label,
  description,
  value,
  min,
  max,
  step = 1,
  suffix = "",
  onChange,
}) {
  return (
    <div className="space-y-3">
      <div className="flex justify-between">
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

        <span className="font-semibold">
          {value}
          {suffix}
        </span>
      </div>

      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-primary"
      />
    </div>
  );
}