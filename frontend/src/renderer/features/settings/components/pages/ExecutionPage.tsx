import { Terminal } from 'lucide-react';
import { SectionCard } from '../ui/SectionCard';
import { StringListEditor } from '../ui/StringListEditor';
import { ToggleGroup } from '../ui/ToggleGroup';

interface ExecPageProps {
    config: any;
    handleChange: (key: string, value: any) => void;
}

export function ExecutionPage({ config, handleChange }: ExecPageProps) {
    return (
        <SectionCard title="System Command Execution" icon={<Terminal className="w-4 h-4" />} color="text-foreground" gradient="from-muted/20 to-muted/5">
            <ToggleGroup
                id="auto_allow_exec"
                label="Auto-allow Execute Command"
                desc="Skip confirmation for system commands"
                checked={config.auto_allow_exec || false}
                onChange={(checked) => handleChange('auto_allow_exec', checked)}
                color="bg-teal-600"
            />
            {config.auto_allow_exec && (
                <div className="border-t border-border/30 pt-4 mt-4">
                    <StringListEditor
                        label="Blacklist Commands"
                        desc="Commands that still require confirmation"
                        items={config.auto_allow_blacklist || []}
                        onChange={(items) => handleChange('auto_allow_blacklist', items)}
                        placeholder="e.g. rm, del, shutdown..."
                    />
                </div>
            )}
        </SectionCard>
    );
}
