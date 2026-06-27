import { Switch } from "@headlessui/react";

export default function PolicySwitch({
  label,
  description,
  checked,
  onChange,
}) {
  return (
    <div className="flex items-center justify-between py-4">
      <div>
        <h4 className="font-medium">
          {label}
        </h4>

        {description && (
          <p className="text-sm text-muted-foreground mt-1">
            {description}
          </p>
        )}
      </div>

      <Switch
        checked={checked}
        onChange={onChange}
        className={`${
          checked ? "bg-primary" : "bg-muted"
        } relative inline-flex h-7 w-12 items-center rounded-full transition`}
      >
        <span
          className={`${
            checked ? "translate-x-6" : "translate-x-1"
          } inline-block h-5 w-5 transform rounded-full bg-white transition`}
        />
      </Switch>
    </div>
  );
}