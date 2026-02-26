import { Clock, Terminal } from "lucide-react";
import type { ChangeEvent } from "react";

import type { Config } from "../../types";
import { Input, InputGroup, SectionCard, StringListEditor, ToggleGroup } from "../ui";

export function ExecutionPage({
  config,
  handleChange,
}: {
  config: Config;
  handleChange: (key: string, value: unknown) => void;
}) {
  return (
    <div className="space-y-6">
      <SectionCard
        title="System Command Execution"
        icon={<Terminal className="w-4 h-4" />}
        color="text-foreground"
        gradient="from-muted/20 to-muted/5"
      >
        <ToggleGroup
          id="auto_allow_exec"
          label="Auto-allow Execute Command"
          desc="Skip confirmation for system commands"
          checked={(config.auto_allow_exec as boolean) || false}
          onChange={(checked) => handleChange("auto_allow_exec", checked)}
          color="bg-teal-600"
        />
        {(config.auto_allow_exec as boolean) && (
          <div className="border-t border-border/30 pt-4 mt-4">
            <StringListEditor
              label="Blacklist Commands"
              desc="Commands that still require confirmation"
              items={(config.auto_allow_blacklist as string[]) || []}
              onChange={(items) => handleChange("auto_allow_blacklist", items)}
              placeholder="e.g. rm, del, shutdown..."
            />
          </div>
        )}
      </SectionCard>
      <SectionCard
        title="Timeouts (s)"
        icon={<Clock className="w-4 h-4" />}
        color="text-foreground"
        gradient="from-muted/20 to-muted/5"
      >
        <div className="grid grid-cols-3 gap-4">
          <InputGroup label="Command Execution">
            <Input
              name="exec_command_timeout"
              value={(config.exec_command_timeout as number) ?? 30}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("exec_command_timeout", e.target.value)}
            />
          </InputGroup>
          <InputGroup label="Request Confirmation">
            <Input
              name="request_confirm_timeout"
              value={(config.request_confirm_timeout as number) ?? 60}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("request_confirm_timeout", e.target.value)}
            />
          </InputGroup>
          <InputGroup label="Request Decision">
            <Input
              name="request_decision_timeout"
              value={(config.request_decision_timeout as number) ?? 60}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("request_decision_timeout", e.target.value)}
            />
          </InputGroup>
        </div>
      </SectionCard>
    </div>
  );
}
