import { Search } from "lucide-react";
import type { ChangeEvent } from "react";
import type { Config } from "../../types";
import { Combobox } from "../ui/Combobox";
import { Input } from "../ui/Input";
import { InputGroup } from "../ui/InputGroup";
import { SectionCard } from "../ui/SectionCard";

export function SearchPage({
  config,
  handleChange,
}: {
  config: Config;
  handleChange: (key: string, value: unknown) => void;
}) {
  return (
    <SectionCard
      title="Web Search"
      icon={<Search className="w-4 h-4" />}
      color="text-foreground"
      gradient="from-muted/20 to-muted/5"
    >
      <InputGroup label="Search Engine" desc="Preferred search provider">
        <Combobox
          value={(config.search_engine as string) || "Tavily"}
          onChange={(val) => handleChange("search_engine", val)}
          options={["Tavily", "Bocha"]}
          placeholder="Select search engine"
        />
      </InputGroup>
      {(config.search_engine || "Tavily") === "Tavily" && (
        <InputGroup label="Tavily API Key" desc="Tavily API Key">
          <Input
            name="tavily_api_key"
            type="password"
            value={(config.tavily_api_key as string) || ""}
            onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("tavily_api_key", e.target.value)}
            placeholder="tvly-..."
          />
        </InputGroup>
      )}
      {(config.search_engine || "Tavily") === "Bocha" && (
        <InputGroup label="Bocha API Key" desc="Bocha API Key">
          <Input
            name="bocha_api_key"
            type="password"
            value={(config.bocha_api_key as string) || ""}
            onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("bocha_api_key", e.target.value)}
            placeholder="Enter Bocha API key"
          />
        </InputGroup>
      )}
      <InputGroup label="Search Result Count" desc="Number of results to return">
        <Input
          name="search_result_count"
          type="number"
          min="1"
          max="50"
          value={(config.search_result_count as number) ?? 10}
          onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("search_result_count", e.target.value)}
        />
      </InputGroup>
    </SectionCard>
  );
}
