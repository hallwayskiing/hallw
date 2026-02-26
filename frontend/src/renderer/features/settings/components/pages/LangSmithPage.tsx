import { Gauge } from "lucide-react";
import type { ChangeEvent } from "react";
import type { Config } from "../../types";
import { Input, InputGroup, SectionCard, ToggleGroup } from "../ui";

export function LangSmithPage({
  config,
  handleChange,
}: {
  config: Config;
  handleChange: (key: string, value: unknown) => void;
}) {
  return (
    <SectionCard
      title="Tracing & Observability"
      icon={<Gauge className="w-4 h-4" />}
      color="text-foreground"
      gradient="from-muted/20 to-muted/5"
    >
      <ToggleGroup
        id="langsmith_tracing"
        label="Enable LangSmith Tracing"
        desc="Send traces to LangSmith for debugging"
        checked={(config.langsmith_tracing as boolean) || false}
        onChange={(checked) => handleChange("langsmith_tracing", checked)}
        color="bg-teal-600"
      />
      <div className="border-t border-border/30 pt-4 mt-4 space-y-4">
        <InputGroup label="Project Name" desc="LangSmith project identifier">
          <Input
            name="langsmith_project"
            value={(config.langsmith_project as string) || ""}
            onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("langsmith_project", e.target.value)}
            placeholder="HALLW"
          />
        </InputGroup>
        <InputGroup label="API Key" desc="LangSmith API key">
          <Input
            name="langsmith_api_key"
            type="password"
            value={(config.langsmith_api_key as string) || ""}
            onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("langsmith_api_key", e.target.value)}
            placeholder="ls-..."
          />
        </InputGroup>
        <InputGroup label="Endpoint" desc="LangSmith API endpoint">
          <Input
            name="langsmith_endpoint"
            value={(config.langsmith_endpoint as string) || ""}
            onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("langsmith_endpoint", e.target.value)}
            placeholder="https://api.smith.langchain.com"
          />
        </InputGroup>
      </div>
    </SectionCard>
  );
}
