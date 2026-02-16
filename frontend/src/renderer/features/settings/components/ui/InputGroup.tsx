import type { ReactNode } from "react";

export function InputGroup({ label, desc, children }: { label: string; desc?: string; children: ReactNode }) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="text-sm font-medium text-foreground">{label}</div>
        {desc && <span className="text-xs text-muted-foreground">{desc}</span>}
      </div>
      {children}
    </div>
  );
}
