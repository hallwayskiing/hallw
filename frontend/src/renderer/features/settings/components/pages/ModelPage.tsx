import { Sparkles } from "lucide-react";
import type { ChangeEvent } from "react";
import type { Config } from "../../types";
import { Combobox, Input, InputGroup, SectionCard } from "../ui";

export function ModelPage({
  config,
  recentModels,
  handleChange,
  handleDeleteRecentModel,
}: {
  config: Config;
  recentModels: string[];
  handleChange: (key: string, value: unknown) => void;
  handleDeleteRecentModel: (modelName: string) => void;
}) {
  return (
    <div className="space-y-6 max-w-2xl">
      <SectionCard title="LLM Configuration" icon={Sparkles}>
        <InputGroup label="Model Name" desc="e.g. gemini/gemini-2.5-flash">
          <Combobox
            value={(config.model_name as string) || ""}
            onChange={(val) => handleChange("model_name", val)}
            options={recentModels}
            onDelete={handleDeleteRecentModel}
            placeholder="gemini/gemini-2.5-flash"
          />
        </InputGroup>
        <InputGroup label="OpenAI-Compatible Endpoint" desc="Endpoint for the custom OpenAI provider">
          <Input
            name="openai_api_base"
            value={(config.openai_api_base as string) || ""}
            onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("openai_api_base", e.target.value)}
            placeholder="https://api.openai.com/v1"
          />
        </InputGroup>
        <InputGroup label="Anthropic-Compatible Endpoint" desc="Endpoint for the custom Anthropic provider">
          <Input
            name="anthropic_api_base"
            value={(config.anthropic_api_base as string) || ""}
            onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("anthropic_api_base", e.target.value)}
            placeholder="https://api.anthropic.com"
          />
        </InputGroup>
      </SectionCard>

      <SectionCard title="Generation Parameters" icon={Sparkles}>
        <InputGroup label="Reasoning Effort" desc="For supported models">
          <Combobox
            value={(config.model_reasoning_effort as string) || "low"}
            onChange={(val) => handleChange("model_reasoning_effort", val)}
            options={["low", "medium", "high"]}
            placeholder="low"
          />
        </InputGroup>
        <div className="grid grid-cols-2 gap-4">
          <InputGroup label="Temperature" desc="0.0 - 2.0">
            <Input
              name="model_temperature"
              step="0.1"
              min="0"
              max="2"
              value={(config.model_temperature as number) ?? 1}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("model_temperature", e.target.value)}
            />
          </InputGroup>
          <InputGroup label="Top P" desc="0.0 - 1.0">
            <Input
              name="model_top_p"
              step="0.01"
              min="0"
              max="1"
              value={(config.model_top_p as number) ?? 0.95}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("model_top_p", e.target.value)}
            />
          </InputGroup>
          <InputGroup label="Top K" desc="0 - 100">
            <Input
              name="model_top_k"
              step="1"
              min="0"
              max="100"
              value={(config.model_top_k as number) ?? 64}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("model_top_k", e.target.value)}
            />
          </InputGroup>
          <InputGroup label="Repetition Penalty" desc="1.0 - 2.0">
            <Input
              name="model_repetition_penalty"
              step="0.1"
              min="1"
              max="2"
              value={(config.model_repetition_penalty as number) ?? 1.2}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("model_repetition_penalty", e.target.value)}
            />
          </InputGroup>
          <InputGroup label="Max Output Tokens" desc="Token limit">
            <Input
              name="model_max_output_tokens"
              min="512"
              value={(config.model_max_output_tokens as number) ?? 5120}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("model_max_output_tokens", e.target.value)}
            />
          </InputGroup>
        </div>
      </SectionCard>
      <SectionCard title="Workflow Parameters" icon={Sparkles}>
        <div className="grid grid-cols-2 gap-4">
          <InputGroup label="Reflection Threshold" desc="Threshold for reflection">
            <Input
              name="model_reflection_threshold"
              min="1"
              value={(config.model_reflection_threshold as number) ?? 3}
              onChange={(e: ChangeEvent<HTMLInputElement>) =>
                handleChange("model_reflection_threshold", e.target.value)
              }
            />
          </InputGroup>
          <InputGroup label="Max Recursion" desc="Limit loops">
            <Input
              name="model_max_recursion"
              min="10"
              value={(config.model_max_recursion as number) ?? 50}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("model_max_recursion", e.target.value)}
            />
          </InputGroup>
        </div>
      </SectionCard>
    </div>
  );
}
