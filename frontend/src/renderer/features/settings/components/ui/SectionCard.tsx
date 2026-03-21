import { cn } from "@lib/utils";
import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

export function SectionCard({
  title,
  icon: Icon,
  children,
}: {
  title: string;
  icon?: LucideIcon;
  children: ReactNode;
}) {
  return (
    <div className={cn("bg-linear-to-br border border-border/30 rounded-2xl p-5 space-y-4 from-muted/60 to-muted/20")}>
      <div className="flex items-center gap-2 pb-3 border-b border-border/30">
        {Icon && (
          <span className="text-foreground/70">
            <Icon className="w-4 h-4" />
          </span>
        )}
        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">{title}</h3>
      </div>
      <div className="space-y-4">{children}</div>
    </div>
  );
}
