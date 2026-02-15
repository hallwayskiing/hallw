import { ChangeEvent } from "react";

import { Clock, Globe, Monitor } from "lucide-react";

import { Input } from "../ui/Input";
import { InputGroup } from "../ui/InputGroup";
import { SectionCard } from "../ui/SectionCard";
import { ToggleGroup } from "../ui/ToggleGroup";

interface BrowserPageProps {
  config: any;
  handleChange: (key: string, value: any) => void;
}

export function BrowserPage({ config, handleChange }: BrowserPageProps) {
  return (
    <div className="space-y-6">
      <SectionCard
        title="Browser Options"
        icon={<Globe className="w-4 h-4" />}
        color="text-foreground"
        gradient="from-muted/20 to-muted/5"
      >
        <ToggleGroup
          id="prefer_local_chrome"
          label="Prefer Local Chrome"
          desc="Use local Chrome instead of Playwright Chromium"
          checked={config.prefer_local_chrome ?? true}
          onChange={(checked) => handleChange("prefer_local_chrome", checked)}
          color="bg-teal-600"
        />
        <ToggleGroup
          id="keep_browser_open"
          label="Keep Browser Open"
          desc="Keep browser running after task completion"
          checked={config.keep_browser_open ?? true}
          onChange={(checked) => handleChange("keep_browser_open", checked)}
          color="bg-teal-600"
        />
      </SectionCard>

      <SectionCard
        title="Chrome Settings"
        icon={<Monitor className="w-4 h-4" />}
        color="text-foreground"
        gradient="from-muted/20 to-muted/5"
      >
        <InputGroup label="Chrome User Data Dir" desc="Path to Chrome profile">
          <Input
            name="chrome_user_data_dir"
            value={config.chrome_user_data_dir || ""}
            onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("chrome_user_data_dir", e.target.value)}
            placeholder=".chrome_user_data/"
          />
        </InputGroup>
        <InputGroup label="CDP Port" desc="Chrome DevTools Protocol port">
          <Input
            name="cdp_port"
            type="number"
            value={config.cdp_port ?? 9222}
            onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("cdp_port", e.target.value)}
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
              value={config.pw_goto_timeout ?? 10000}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("pw_goto_timeout", e.target.value)}
            />
          </InputGroup>
          <InputGroup label="Click">
            <Input
              name="pw_click_timeout"
              type="number"
              value={config.pw_click_timeout ?? 6000}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("pw_click_timeout", e.target.value)}
            />
          </InputGroup>
          <InputGroup label="CDP Connect">
            <Input
              name="pw_cdp_timeout"
              type="number"
              value={config.pw_cdp_timeout ?? 1000}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange("pw_cdp_timeout", e.target.value)}
            />
          </InputGroup>
        </div>
      </SectionCard>
    </div>
  );
}
