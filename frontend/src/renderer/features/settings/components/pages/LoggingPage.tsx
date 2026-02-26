import { Logs } from "lucide-react";
import type { ChangeEvent } from "react";
import type { Config } from "../../types";
import { Combobox, Input, InputGroup, SectionCard } from "../ui";

export function LoggingPage({
  config,
  handleChange,
}: {
  config: Config;
  handleChange: (key: string, value: unknown) => void;
}) {
  return (
    <SectionCard
      title="System Logging"
      icon={<Logs className="w-4 h-4" />}
      color="text-foreground"
      gradient="from-muted/20 to-muted/5"
    >
      <InputGroup label="Log Level" desc="Verbosity of logging output">
        <Combobox
          value={(config.logging_level as string) || "INFO"}
          onChange={(val) => handleChange("logging_level", val)}
          options={["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]}
          placeholder="INFO"
        />
      </InputGroup>
      <InputGroup label="Log Directory" desc="Path to store log files">
        <Input
          name="logging_file_dir"
          value={(config.logging_file_dir as string) || ""}
          onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("logging_file_dir", e.target.value)}
          placeholder="logs"
        />
      </InputGroup>
      <InputGroup label="Max Log Chars" desc="Maximum chars per message">
        <Input
          name="logging_max_chars"
          value={(config.logging_max_chars as number) ?? 200}
          onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("logging_max_chars", e.target.value)}
        />
      </InputGroup>
    </SectionCard>
  );
}
