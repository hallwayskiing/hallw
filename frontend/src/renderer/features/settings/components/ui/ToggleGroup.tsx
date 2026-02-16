import { cn } from "@lib/utils";

export function ToggleGroup({
  id,
  label,
  desc,
  checked,
  onChange,
  color,
}: {
  id: string;
  label: string;
  desc?: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  color?: string;
}) {
  return (
    <div className="flex items-center justify-between py-2 group">
      <div className="flex flex-col gap-0.5">
        <label htmlFor={id} className="text-sm font-medium text-foreground cursor-pointer">
          {label}
        </label>
        {desc && <span className="text-xs text-muted-foreground">{desc}</span>}
      </div>
      <button
        type="button"
        id={id}
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={cn(
          "relative w-11 h-6 rounded-full transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary/30",
          checked ? color || "bg-linear-to-r from-primary to-primary/80" : "bg-muted/50"
        )}
      >
        <span
          className={cn(
            "absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow-md transition-transform duration-300",
            checked && "translate-x-5"
          )}
        />
      </button>
    </div>
  );
}
