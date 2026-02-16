import { Gauge, Globe, Key, Logs, Palette, Search, Sparkles, Terminal } from "lucide-react";

import type { TabConfig } from "./types";

export const TABS: TabConfig[] = [
  {
    id: "model",
    label: "Model",
    icon: <Sparkles className="w-4 h-4" />,
    color: "text-foreground",
    gradient: "from-zinc-500/10 to-zinc-500/5",
  },
  {
    id: "api-keys",
    label: "API Keys",
    icon: <Key className="w-4 h-4" />,
    color: "text-foreground",
    gradient: "from-zinc-500/10 to-zinc-500/5",
  },
  {
    id: "langsmith",
    label: "LangSmith",
    icon: <Gauge className="w-4 h-4" />,
    color: "text-foreground",
    gradient: "from-zinc-500/10 to-zinc-500/5",
  },
  {
    id: "logging",
    label: "Logging",
    icon: <Logs className="w-4 h-4" />,
    color: "text-foreground",
    gradient: "from-zinc-500/10 to-zinc-500/5",
  },
  {
    id: "exec",
    label: "Execution",
    icon: <Terminal className="w-4 h-4" />,
    color: "text-foreground",
    gradient: "from-zinc-500/10 to-zinc-500/5",
  },
  {
    id: "search",
    label: "Search",
    icon: <Search className="w-4 h-4" />,
    color: "text-foreground",
    gradient: "from-zinc-500/10 to-zinc-500/5",
  },
  {
    id: "browser",
    label: "Browser",
    icon: <Globe className="w-4 h-4" />,
    color: "text-foreground",
    gradient: "from-zinc-500/10 to-zinc-500/5",
  },
  {
    id: "appearance",
    label: "Appearance",
    icon: <Palette className="w-4 h-4" />,
    color: "text-foreground",
    gradient: "from-zinc-500/10 to-zinc-500/5",
  },
];

export const NUMBER_FIELDS = [
  "model_temperature",
  "model_max_output_tokens",
  "model_reflection_threshold",
  "model_max_recursion",
  "logging_max_chars",
  "search_result_count",
  "cdp_port",
  "pw_goto_timeout",
  "pw_click_timeout",
  "pw_cdp_timeout",
];
