import { Key } from "lucide-react";
import type { ChangeEvent } from "react";
import type { Config } from "../../types";
import { Input } from "../ui/Input";
import { InputGroup } from "../ui/InputGroup";
import { SectionCard } from "../ui/SectionCard";

const ALL_PROVIDERS = [
  { key: "openai_api_key", label: "OpenAI", placeholder: "sk-..." },
  { key: "google_api_key", label: "Google", placeholder: "AIza..." },
  { key: "anthropic_api_key", label: "Anthropic", placeholder: "sk-ant-..." },
  { key: "openrouter_api_key", label: "OpenRouter", placeholder: "sk-or-..." },
  { key: "deepseek_api_key", label: "DeepSeek", placeholder: "sk-..." },
  { key: "zai_api_key", label: "ZAI", placeholder: "..." },
  { key: "moonshot_api_key", label: "Moonshot", placeholder: "sk-..." },
  { key: "xiaomi_mimo_api_key", label: "Xiaomi Mimo", placeholder: "sk-..." },
];

export function KeysPage({
  config,
  handleChange,
}: {
  config: Config;
  handleChange: (key: string, value: unknown) => void;
}) {
  return (
    <SectionCard
      title="Provider API Keys"
      icon={<Key className="w-4 h-4" />}
      color="text-foreground"
      gradient="from-muted/20 to-muted/5"
    >
      <div className="space-y-4">
        {ALL_PROVIDERS.map((provider) => (
          <InputGroup key={provider.key} label={provider.label} desc={`${provider.label} API Key`}>
            <Input
              name={provider.key}
              type="password"
              value={(config[provider.key] as string) || ""}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange(provider.key, e.target.value)}
              placeholder={provider.placeholder}
            />
          </InputGroup>
        ))}
      </div>
    </SectionCard>
  );
}
