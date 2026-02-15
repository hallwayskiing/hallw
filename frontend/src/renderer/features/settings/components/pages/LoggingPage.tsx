import { ChangeEvent } from "react";

import { Logs } from "lucide-react";

import { Combobox } from "../ui/Combobox";
import { Input } from "../ui/Input";
import { InputGroup } from "../ui/InputGroup";
import { SectionCard } from "../ui/SectionCard";

interface LoggingPageProps {
  config: any;
  handleChange: (key: string, value: any) => void;
}

export function LoggingPage({ config, handleChange }: LoggingPageProps) {
  return (
    <SectionCard
      title="System Logging"
      icon={<Logs className="w-4 h-4" />}
      color="text-foreground"
      gradient="from-muted/20 to-muted/5"
    >
      <InputGroup label="Log Level" desc="Verbosity of logging output">
        <Combobox
          value={config.logging_level || "INFO"}
          onChange={(val) => handleChange("logging_level", val)}
          options={["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]}
          placeholder="INFO"
        />
      </InputGroup>
      <InputGroup label="Log Directory" desc="Path to store log files">
        <Input
          name="logging_file_dir"
          value={config.logging_file_dir || ""}
          onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("logging_file_dir", e.target.value)}
          placeholder="logs"
        />
      </InputGroup>
      <InputGroup label="Max Log Chars" desc="Maximum chars per message">
        <Input
          name="logging_max_chars"
          type="number"
          min="1"
          value={config.logging_max_chars ?? 200}
          onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("logging_max_chars", e.target.value)}
        />
      </InputGroup>
    </SectionCard>
  );
}
