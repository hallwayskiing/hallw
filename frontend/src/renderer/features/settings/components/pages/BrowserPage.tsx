import { Clock, Monitor } from "lucide-react";
import type { ChangeEvent } from "react";
import type { Config } from "../../types";
import { Input, InputGroup, SectionCard } from "../ui";

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
        title="Browser Settings"
        icon={<Monitor className="w-4 h-4" />}
        color="text-foreground"
        gradient="from-muted/20 to-muted/5"
      >
        <InputGroup label="Chrome User Data Directory" desc="Path to persistent browser profile">
          <Input
            name="chrome_user_data_dir"
            value={(config.chrome_user_data_dir as string) || ""}
            onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("chrome_user_data_dir", e.target.value)}
            placeholder=".chrome_user_data/"
          />
        </InputGroup>
        <InputGroup label="Browser Content Max Length" desc="Max length of page content to extract">
          <Input
            name="pw_content_max_length"
            value={(config.pw_content_max_length as number) || 10000}
            onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("pw_content_max_length", e.target.value)}
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
          <InputGroup label="Page Navigate">
            <Input
              name="pw_goto_timeout"
              value={(config.pw_goto_timeout as number) ?? 10000}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("pw_goto_timeout", e.target.value)}
            />
          </InputGroup>
          <InputGroup label="Element Click">
            <Input
              name="pw_click_timeout"
              value={(config.pw_click_timeout as number) ?? 6000}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("pw_click_timeout", e.target.value)}
            />
          </InputGroup>
          <InputGroup label="CDP Connect">
            <Input
              name="pw_cdp_timeout"
              value={(config.pw_cdp_timeout as number) ?? 1000}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("pw_cdp_timeout", e.target.value)}
            />
          </InputGroup>
        </div>
      </SectionCard>
    </div>
  );
}
