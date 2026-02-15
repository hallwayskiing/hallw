import { ChangeEvent } from "react";

import { Sparkles } from "lucide-react";

import { Combobox } from "../ui/Combobox";
import { Input } from "../ui/Input";
import { InputGroup } from "../ui/InputGroup";
import { SectionCard } from "../ui/SectionCard";

export function ModelPage({ config, handleChange }: { config: any; handleChange: (key: string, value: any) => void }) {
  return (
    <div className="space-y-6 max-w-2xl">
      <SectionCard
        title="LLM Configuration"
        icon={<Sparkles className="w-4 h-4" />}
        color="text-foreground"
        gradient="from-muted/20 to-muted/5"
      >
        <InputGroup label="Model Name" desc="e.g. gemini/gemini-2.5-flash">
          <Combobox
            value={config.model_name || ""}
            onChange={(val) => handleChange("model_name", val)}
            options={config.model_recent_used || []}
            placeholder="gemini/gemini-2.5-flash"
          />
        </InputGroup>
        <InputGroup label="OpenAI-Compatible Endpoint" desc="Endpoint for the custom OpenAI provider">
          <Input
            name="openai_api_base"
            value={config.openai_api_base || ""}
            onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("openai_api_base", e.target.value)}
            placeholder="https://api.openai.com/v1"
          />
        </InputGroup>
        <InputGroup label="Anthropic-Compatible Endpoint" desc="Endpoint for the custom Anthropic provider">
          <Input
            name="anthropic_api_base"
            value={config.anthropic_api_base || ""}
            onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("anthropic_api_base", e.target.value)}
            placeholder="https://api.anthropic.com"
          />
        </InputGroup>
      </SectionCard>

      <SectionCard
        title="Generation Parameters"
        icon={<Sparkles className="w-4 h-4" />}
        color="text-foreground"
        gradient="from-muted/20 to-muted/5"
      >
        <InputGroup label="Reasoning Effort" desc="For supported models">
          <Combobox
            value={config.model_reasoning_effort || "low"}
            onChange={(val) => handleChange("model_reasoning_effort", val)}
            options={["low", "medium", "high"]}
            placeholder="low"
          />
        </InputGroup>
        <div className="grid grid-cols-2 gap-4">
          <InputGroup label="Temperature" desc="0.0 - 2.0">
            <Input
              name="model_temperature"
              type="number"
              step="0.1"
              min="0"
              max="2"
              value={config.model_temperature ?? 1}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("model_temperature", e.target.value)}
            />
          </InputGroup>
          <InputGroup label="Max Output Tokens" desc="Token limit">
            <Input
              name="model_max_output_tokens"
              type="number"
              min="1"
              value={config.model_max_output_tokens ?? 10240}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("model_max_output_tokens", e.target.value)}
            />
          </InputGroup>
          <InputGroup label="Reflection Threshold" desc="Threshold for reflection">
            <Input
              name="model_reflection_threshold"
              type="number"
              min="1"
              value={config.model_reflection_threshold ?? 3}
              onChange={(e: ChangeEvent<HTMLInputElement>) =>
                handleChange("model_reflection_threshold", e.target.value)
              }
            />
          </InputGroup>
          <InputGroup label="Max Recursion" desc="Limit loops">
            <Input
              name="model_max_recursion"
              type="number"
              min="1"
              value={config.model_max_recursion ?? 50}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("model_max_recursion", e.target.value)}
            />
          </InputGroup>
        </div>
      </SectionCard>
    </div>
  );
}
