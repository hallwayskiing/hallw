import { cn } from "@lib/utils";
import { useAppStore } from "@store/store";
import {
  Atom,
  Bot,
  BrainCircuit,
  Cat,
  CircuitBoard,
  Cpu,
  Crown,
  Dog,
  Gem,
  Ghost,
  Heart,
  type LucideIcon,
  Moon,
  Orbit,
  Palette,
  Rabbit,
  Rocket,
  Smile,
  Sparkles,
  Squirrel,
  Sun,
  User,
  UserCircle,
  Zap,
} from "lucide-react";

import { SectionCard } from "../ui";

interface AvatarOption {
  name: string;
  icon: LucideIcon;
}

const USER_AVATAR_OPTIONS: AvatarOption[] = [
  { name: "User", icon: User },
  { name: "UserCircle", icon: UserCircle },
  { name: "Smile", icon: Smile },
  { name: "Ghost", icon: Ghost },
  { name: "Cat", icon: Cat },
  { name: "Dog", icon: Dog },
  { name: "Heart", icon: Heart },
  { name: "Squirrel", icon: Squirrel },
  { name: "Rabbit", icon: Rabbit },
  { name: "Crown", icon: Crown },
];

const AI_AVATAR_OPTIONS: AvatarOption[] = [
  { name: "Bot", icon: Bot },
  { name: "BrainCircuit", icon: BrainCircuit },
  { name: "Cpu", icon: Cpu },
  { name: "Sparkles", icon: Sparkles },
  { name: "Zap", icon: Zap },
  { name: "CircuitBoard", icon: CircuitBoard },
  { name: "Atom", icon: Atom },
  { name: "Orbit", icon: Orbit },
  { name: "Gem", icon: Gem },
  { name: "Rocket", icon: Rocket },
];

function AvatarPicker({
  label,
  description,
  options,
  selected,
  onSelect,
  activeColor,
  activeBg,
}: {
  label: string;
  description: string;
  options: AvatarOption[];
  selected: string;
  onSelect: (name: string) => void;
  activeColor: string;
  activeBg: string;
}) {
  return (
    <div className="flex flex-col gap-3 py-3">
      <div className="flex flex-col gap-0.5">
        <span className="text-sm font-medium text-foreground">{label}</span>
        <span className="text-xs text-muted-foreground">{description}</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {options.map(({ name, icon: Icon }) => {
          const isActive = selected === name;
          return (
            <button
              type="button"
              key={name}
              onClick={() => onSelect(name)}
              className={cn(
                "relative w-10 h-10 rounded-xl flex items-center justify-center border transition-all duration-200 group",
                isActive
                  ? `${activeBg} ${activeColor} border-current shadow-sm scale-105`
                  : "bg-muted/10 border-border/30 text-muted-foreground hover:bg-muted/20 hover:text-foreground hover:border-border/50 hover:scale-105"
              )}
              title={name}
            >
              <Icon className="w-5 h-5" />
              {isActive && (
                <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-current ring-2 ring-background animate-in zoom-in duration-200" />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export function AppearancePage() {
  const theme = useAppStore((s) => s.theme);
  const toggleTheme = useAppStore((s) => s.toggleTheme);
  const userAvatarIcon = useAppStore((s) => s.userAvatarIcon);
  const aiAvatarIcon = useAppStore((s) => s.aiAvatarIcon);
  const setUserAvatarIcon = useAppStore((s) => s.setUserAvatarIcon);
  const setAiAvatarIcon = useAppStore((s) => s.setAiAvatarIcon);

  return (
    <div className="space-y-5">
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

      <SectionCard
        title="Avatars"
        icon={<User className="w-4 h-4" />}
        color="text-foreground"
        gradient="from-muted/20 to-muted/5"
      >
        <AvatarPicker
          label="Your Avatar"
          description="Choose an icon for your messages"
          options={USER_AVATAR_OPTIONS}
          selected={userAvatarIcon}
          onSelect={setUserAvatarIcon}
          activeColor="text-indigo-400"
          activeBg="bg-indigo-500/15"
        />
        <div className="border-t border-border/20" />
        <AvatarPicker
          label="AI Avatar"
          description="Choose an icon for AI messages"
          options={AI_AVATAR_OPTIONS}
          selected={aiAvatarIcon}
          onSelect={setAiAvatarIcon}
          activeColor="text-teal-400"
          activeBg="bg-teal-500/15"
        />
      </SectionCard>
    </div>
  );
}
