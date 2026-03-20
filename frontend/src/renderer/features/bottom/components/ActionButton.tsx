import { cn } from "@lib/utils";

import type { ActionButtonProps } from "../types";

export function ActionButton({ onClick, icon: Icon, tooltip, active }: ActionButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex items-center justify-center px-3 rounded-xl transition-all duration-200 border border-transparent text-muted-foreground hover:text-foreground",
        active && "text-foreground bg-muted/50",
        "w-[38px] h-[38px] p-0 rounded-xl"
      )}
      title={tooltip}
    >
      <Icon className="w-[22px] h-[22px]" />
    </button>
  );
}
