import { Clock, Monitor } from "lucide-react";
import type { ChangeEvent } from "react";
import type { Config } from "../../types";
import { Input } from "../ui/Input";
import { InputGroup } from "../ui/InputGroup";
import { SectionCard } from "../ui/SectionCard";

export function BrowserPage({
  config,
  handleChange,
}: {
  config: Config;
  handleChange: (key: string, value: unknown) => void;
}) {
  return (
    <div className="space-y-6">
      <SectionCard
        title="Chrome Settings"
        icon={<Monitor className="w-4 h-4" />}
        color="text-foreground"
        gradient="from-muted/20 to-muted/5"
      >
        <InputGroup label="Chrome User Data Dir" desc="Path to persistent browser profile/session">
          <Input
            name="chrome_user_data_dir"
            value={(config.chrome_user_data_dir as string) || ""}
            onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("chrome_user_data_dir", e.target.value)}
            placeholder=".chrome_user_data/"
          />
        </InputGroup>
      </SectionCard>
      <SectionCard
        title="Timeouts (ms)"
        icon={<Clock className="w-4 h-4" />}
        color="text-foreground"
        gradient="from-muted/20 to-muted/5"
      >
        <div className="grid grid-cols-3 gap-4">
          <InputGroup label="Page Load">
            <Input
              name="pw_goto_timeout"
              type="number"
              value={(config.pw_goto_timeout as number) ?? 10000}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("pw_goto_timeout", e.target.value)}
            />
          </InputGroup>
          <InputGroup label="Click">
            <Input
              name="pw_click_timeout"
              type="number"
              value={(config.pw_click_timeout as number) ?? 6000}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("pw_click_timeout", e.target.value)}
            />
          </InputGroup>
          <InputGroup label="CDP Connect">
            <Input
              name="pw_cdp_timeout"
              type="number"
              value={(config.pw_cdp_timeout as number) ?? 1000}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("pw_cdp_timeout", e.target.value)}
            />
          </InputGroup>
        </div>
      </SectionCard>
    </div>
  );
}
