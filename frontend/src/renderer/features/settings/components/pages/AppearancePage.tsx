import { cn } from "@lib/utils";
import { useAppStore } from "@store/store";
import { Moon, Palette, Sun } from "lucide-react";

import { SectionCard } from "../ui/SectionCard";

export function AppearancePage() {
  const theme = useAppStore((s) => s.theme);
  const toggleTheme = useAppStore((s) => s.toggleTheme);

  return (
    <SectionCard
      title="Theme"
      icon={<Palette className="w-4 h-4" />}
      color="text-foreground"
      gradient="from-muted/20 to-muted/5"
    >
      <div className="flex items-center justify-between py-3">
        <div className="flex flex-col gap-0.5">
          <span className="text-sm font-medium text-foreground">Dark Mode</span>
          <span className="text-xs text-muted-foreground">Toggle between light and dark theme</span>
        </div>
        <button
          type="button"
          onClick={toggleTheme}
          className={cn(
            "relative flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-300",
            theme === "dark"
              ? "bg-linear-to-r from-indigo-500/20 to-purple-500/20 text-indigo-300"
              : "bg-linear-to-r from-amber-500/20 to-orange-500/20 text-amber-300"
          )}
        >
          {theme === "dark" ? (
            <>
              <Moon className="w-4 h-4" />
              <span className="text-sm font-medium">Dark</span>
            </>
          ) : (
            <>
              <Sun className="w-4 h-4" />
              <span className="text-sm font-medium">Light</span>
            </>
          )}
        </button>
      </div>
    </SectionCard>
  );
}
