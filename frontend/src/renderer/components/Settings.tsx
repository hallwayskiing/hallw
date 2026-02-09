import { X, Save, Loader2, Settings2, Sparkles, FileText, Terminal, Globe, Search, Monitor, Clock, ChevronRight, Key } from 'lucide-react';
import { useState, useEffect, ReactNode, ChangeEvent } from 'react';
import { useAppStore } from '../stores/appStore';
import { cn } from '../lib/utils';

// Provider definitions for API Keys tab
const ALL_PROVIDERS = [
    { key: 'openai_api_key', label: 'OpenAI', placeholder: 'sk-...' },
    { key: 'google_api_key', label: 'Google', placeholder: 'AIza...' },
    { key: 'anthropic_api_key', label: 'Anthropic', placeholder: 'sk-ant-...' },
    { key: 'openrouter_api_key', label: 'OpenRouter', placeholder: 'sk-or-...' },
    { key: 'deepseek_api_key', label: 'DeepSeek', placeholder: 'sk-...' },
    { key: 'zai_api_key', label: 'ZAI', placeholder: 'Enter ZAI API key' },
    { key: 'moonshot_api_key', label: 'Moonshot', placeholder: 'sk-...' },
    { key: 'xiaomi_mimo_api_key', label: 'Xiaomi Mimo', placeholder: 'sk-...' },
];

interface SettingsProps {
    isOpen: boolean;
    onClose: () => void;
}

interface Config {
    [key: string]: any;
    // Model
    model_name?: string;
    model_endpoint?: string;
    model_temperature?: number;
    model_max_output_tokens?: number;
    model_reflection_threshold?: number;
    model_max_recursion?: number;
    // Provider API Keys
    openai_api_key?: string;
    google_api_key?: string;
    anthropic_api_key?: string;
    openrouter_api_key?: string;
    zai_api_key?: string;
    moonshot_api_key?: string;
    // LangSmith
    langsmith_tracing?: boolean;
    langsmith_endpoint?: string;
    langsmith_api_key?: string;
    langsmith_project?: string;
    // Logging
    logging_level?: string;
    logging_file_dir?: string;
    logging_max_chars?: number;
    // Exec & Search
    auto_allow_exec?: boolean;
    auto_allow_blacklist?: string[];
    brave_search_api_key?: string;
    brave_search_result_count?: number;
    // Browser
    prefer_local_chrome?: boolean;
    chrome_user_data_dir?: string;
    cdp_port?: number;
    pw_headless_mode?: boolean;
    pw_window_width?: number;
    pw_window_height?: number;
    keep_browser_open?: boolean;
    pw_goto_timeout?: number;
    pw_click_timeout?: number;
    pw_cdp_timeout?: number;
}

interface ServerResponse {
    success: boolean;
    error?: string;
}

interface TabConfig {
    id: string;
    label: string;
    icon: ReactNode;
    color: string;
    gradient: string;
}

const TABS: TabConfig[] = [
    { id: 'model', label: 'Model', icon: <Sparkles className="w-4 h-4" />, color: 'text-amber-300', gradient: 'from-amber-500/15 to-orange-500/5' },
    { id: 'api-keys', label: 'API Keys', icon: <Key className="w-4 h-4" />, color: 'text-cyan-300', gradient: 'from-cyan-500/15 to-teal-500/5' },
    { id: 'langsmith', label: 'LangSmith', icon: <FileText className="w-4 h-4" />, color: 'text-emerald-300', gradient: 'from-emerald-500/15 to-teal-500/5' },
    { id: 'logging', label: 'Logging', icon: <Terminal className="w-4 h-4" />, color: 'text-sky-300', gradient: 'from-sky-500/15 to-cyan-500/5' },
    { id: 'exec-search', label: 'Exec & Search', icon: <Search className="w-4 h-4" />, color: 'text-violet-300', gradient: 'from-violet-500/15 to-purple-500/5' },
    { id: 'browser', label: 'Browser', icon: <Globe className="w-4 h-4" />, color: 'text-rose-300', gradient: 'from-rose-500/15 to-pink-500/5' },
];

const NUMBER_FIELDS = [
    'model_temperature', 'model_max_output_tokens', 'model_reflection_threshold', 'model_max_recursion',
    'logging_max_chars', 'brave_search_result_count', 'cdp_port', 'pw_window_width', 'pw_window_height',
    'pw_goto_timeout', 'pw_click_timeout', 'pw_cdp_timeout'
];

export function Settings({ isOpen, onClose }: SettingsProps) {
    const getSocket = useAppStore(s => s.getSocket);
    const [activeTab, setActiveTab] = useState('model');
    const [config, setConfig] = useState<Config>({});
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [statusMsg, setStatusMsg] = useState('');

    const currentTab = TABS.find(t => t.id === activeTab) || TABS[0];

    useEffect(() => {
        const socket = getSocket();
        if (!isOpen || !socket) return;

        setIsLoading(true);
        setStatusMsg('');

        socket.emit('get_config');

        const handleConfigData = (data: Config) => {
            setConfig(data);
            setIsLoading(false);
        };

        const handleConfigUpdated = (response: ServerResponse) => {
            setIsSaving(false);
            if (response.success) {
                setStatusMsg('Settings saved successfully!');
                setTimeout(() => {
                    setStatusMsg('');
                    onClose();
                }, 1000);
            } else {
                setStatusMsg(`Error: ${response.error}`);
            }
        };

        socket.on('config_data', handleConfigData);
        socket.on('config_updated', handleConfigUpdated);

        return () => {
            socket.off('config_data', handleConfigData);
            socket.off('config_updated', handleConfigUpdated);
        };
    }, [isOpen, getSocket]);

    const handleChange = (key: string, value: any) => {
        if (NUMBER_FIELDS.includes(key)) {
            value = Number(value);
        }
        setConfig(prev => ({ ...prev, [key]: value }));
    };

    const handleSave = () => {
        const socket = getSocket();
        if (socket) {
            setIsSaving(true);
            setStatusMsg('Saving...');
            socket.emit('update_config', config);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="w-[900px] h-[650px] bg-gradient-to-br from-card via-card to-background border border-border/50 rounded-2xl shadow-2xl flex flex-col animate-in zoom-in-95 duration-300 overflow-hidden">

                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-border/50 bg-gradient-to-r from-background/80 to-transparent backdrop-blur-sm">
                    <div className="flex items-center gap-3">
                        <div className={cn("p-2 rounded-lg bg-gradient-to-br", currentTab.gradient)}>
                            <Settings2 className={cn("w-5 h-5", currentTab.color)} />
                        </div>
                        <h2 className="font-semibold text-lg tracking-tight">Settings</h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-all duration-200"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Main Content Area */}
                <div className="flex flex-1 overflow-hidden">
                    {/* Sidebar Tabs */}
                    <div className="w-52 border-r border-border/30 bg-muted/5 p-4 space-y-1 flex-shrink-0">
                        {TABS.map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={cn(
                                    "w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 group whitespace-nowrap",
                                    activeTab === tab.id
                                        ? cn("bg-gradient-to-r shadow-sm", tab.gradient, tab.color)
                                        : "text-muted-foreground hover:bg-muted/30 hover:text-foreground"
                                )}
                            >
                                <span className={cn(
                                    "transition-transform duration-200 flex-shrink-0",
                                    activeTab === tab.id ? cn("scale-110", tab.color) : "group-hover:scale-105"
                                )}>
                                    {tab.icon}
                                </span>
                                <span className="truncate">{tab.label}</span>
                            </button>
                        ))}
                    </div>

                    {/* Form Area */}
                    <div className="flex-1 p-6 overflow-y-auto">
                        {isLoading ? (
                            <div className="flex items-center justify-center h-full">
                                <div className="flex flex-col items-center gap-3">
                                    <Loader2 className={cn("w-8 h-8 animate-spin", currentTab.color)} />
                                    <span className="text-sm text-muted-foreground">Loading configuration...</span>
                                </div>
                            </div>
                        ) : (
                            <div className="space-y-6 max-w-2xl">
                                {activeTab === 'model' && (
                                    <>
                                        <SectionCard title="LLM Configuration" icon={<Sparkles className="w-4 h-4" />} color="text-amber-300" gradient="from-amber-500/8 to-orange-500/3">
                                            <InputGroup label="Model Name" desc="e.g. gemini/gemini-2.5-flash">
                                                <Input name="model_name" value={config.model_name || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('model_name', e.target.value)} placeholder="gemini/gemini-2.5-flash" />
                                            </InputGroup>
                                            <InputGroup label="Custom Endpoint" desc="Base URL for the custom model API">
                                                <Input name="model_endpoint" value={config.model_endpoint || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('model_endpoint', e.target.value)} placeholder="https://api.openai.com/v1" />
                                            </InputGroup>
                                        </SectionCard>

                                        <SectionCard title="Generation Parameters" icon={<Sparkles className="w-4 h-4" />} color="text-orange-300" gradient="from-orange-500/8 to-amber-500/3">
                                            <div className="grid grid-cols-2 gap-4">
                                                <InputGroup label="Temperature" desc="0.0 - 2.0">
                                                    <Input name="model_temperature" type="number" step="0.1" min="0" max="2" value={config.model_temperature ?? 1} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('model_temperature', e.target.value)} />
                                                </InputGroup>
                                                <InputGroup label="Max Output Tokens" desc="Token limit">
                                                    <Input name="model_max_output_tokens" type="number" min="1" value={config.model_max_output_tokens ?? 10240} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('model_max_output_tokens', e.target.value)} />
                                                </InputGroup>
                                                <InputGroup label="Reflection Threshold" desc="Threshold for reflection">
                                                    <Input name="model_reflection_threshold" type="number" min="1" value={config.model_reflection_threshold ?? 3} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('model_reflection_threshold', e.target.value)} />
                                                </InputGroup>
                                                <InputGroup label="Max Recursion" desc="Limit loops">
                                                    <Input name="model_max_recursion" type="number" min="1" value={config.model_max_recursion ?? 50} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('model_max_recursion', e.target.value)} />
                                                </InputGroup>
                                            </div>
                                        </SectionCard>
                                    </>
                                )}

                                {activeTab === 'api-keys' && (
                                    <SectionCard title="Provider API Keys" icon={<Key className="w-4 h-4" />} color="text-cyan-300" gradient="from-cyan-500/8 to-teal-500/3">
                                        <div className="space-y-4">
                                            {ALL_PROVIDERS.map(provider => (
                                                <InputGroup key={provider.key} label={provider.label} desc={`${provider.label} API Key`}>
                                                    <Input
                                                        name={provider.key}
                                                        type="password"
                                                        value={config[provider.key] || ''}
                                                        onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange(provider.key, e.target.value)}
                                                        placeholder={provider.placeholder}
                                                    />
                                                </InputGroup>
                                            ))}
                                        </div>
                                    </SectionCard>
                                )}

                                {activeTab === 'langsmith' && (
                                    <SectionCard title="Tracing & Observability" icon={<FileText className="w-4 h-4" />} color="text-emerald-300" gradient="from-emerald-500/8 to-teal-500/3">
                                        <ToggleGroup
                                            id="langsmith_tracing"
                                            label="Enable LangSmith Tracing"
                                            desc="Send traces to LangSmith for debugging"
                                            checked={config.langsmith_tracing || false}
                                            onChange={(checked) => handleChange('langsmith_tracing', checked)}
                                            color="bg-gradient-to-r from-emerald-400 to-teal-400"
                                        />
                                        <div className="border-t border-border/30 pt-4 mt-4 space-y-4">
                                            <InputGroup label="Project Name" desc="LangSmith project identifier">
                                                <Input name="langsmith_project" value={config.langsmith_project || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('langsmith_project', e.target.value)} placeholder="HALLW" />
                                            </InputGroup>
                                            <InputGroup label="API Key" desc="LangSmith API key">
                                                <Input name="langsmith_api_key" type="password" value={config.langsmith_api_key || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('langsmith_api_key', e.target.value)} placeholder="ls-..." />
                                            </InputGroup>
                                            <InputGroup label="Endpoint" desc="LangSmith API endpoint">
                                                <Input name="langsmith_endpoint" value={config.langsmith_endpoint || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('langsmith_endpoint', e.target.value)} placeholder="https://api.smith.langchain.com" />
                                            </InputGroup>
                                        </div>
                                    </SectionCard>
                                )}

                                {activeTab === 'logging' && (
                                    <SectionCard title="System Logging" icon={<Terminal className="w-4 h-4" />} color="text-sky-300" gradient="from-sky-500/8 to-cyan-500/3">
                                        <InputGroup label="Log Level" desc="Verbosity of logging output">
                                            <select
                                                className="w-full bg-input/30 border border-input/50 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400/30 focus:border-sky-400/50 transition-all"
                                                value={config.logging_level || 'INFO'}
                                                onChange={(e) => handleChange('logging_level', e.target.value)}
                                            >
                                                <option value="DEBUG">DEBUG</option>
                                                <option value="INFO">INFO</option>
                                                <option value="WARNING">WARNING</option>
                                                <option value="ERROR">ERROR</option>
                                                <option value="CRITICAL">CRITICAL</option>
                                            </select>
                                        </InputGroup>
                                        <InputGroup label="Log Directory" desc="Path to store log files">
                                            <Input name="logging_file_dir" value={config.logging_file_dir || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('logging_file_dir', e.target.value)} placeholder="logs" />
                                        </InputGroup>
                                        <InputGroup label="Max Log Chars" desc="Maximum chars per message">
                                            <Input name="logging_max_chars" type="number" min="1" value={config.logging_max_chars ?? 200} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('logging_max_chars', e.target.value)} />
                                        </InputGroup>
                                    </SectionCard>
                                )}

                                {activeTab === 'exec-search' && (
                                    <>
                                        <SectionCard title="Execution Settings" icon={<Terminal className="w-4 h-4" />} color="text-violet-300" gradient="from-violet-500/8 to-purple-500/3">
                                            <ToggleGroup
                                                id="auto_allow_exec"
                                                label="Auto-allow Execute Command"
                                                desc="Skip confirmation for system commands"
                                                checked={config.auto_allow_exec || false}
                                                onChange={(checked) => handleChange('auto_allow_exec', checked)}
                                                color="bg-gradient-to-r from-violet-400 to-purple-400"
                                            />
                                            {config.auto_allow_exec && (
                                                <div className="border-t border-border/30 pt-4 mt-4">
                                                    <StringListEditor
                                                        label="Blacklist Commands"
                                                        desc="Commands that still require confirmation"
                                                        items={config.auto_allow_blacklist || []}
                                                        onChange={(items) => handleChange('auto_allow_blacklist', items)}
                                                        placeholder="e.g. rm, del, format..."
                                                    />
                                                </div>
                                            )}
                                        </SectionCard>

                                        <SectionCard title="Search Settings" icon={<Search className="w-4 h-4" />} color="text-purple-300" gradient="from-purple-500/8 to-violet-500/3">
                                            <InputGroup label="Brave Search API Key" desc="For web search functionality">
                                                <Input name="brave_search_api_key" type="password" value={config.brave_search_api_key || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('brave_search_api_key', e.target.value)} placeholder="BSA..." />
                                            </InputGroup>
                                            <InputGroup label="Search Result Count" desc="Number of results to return">
                                                <Input name="brave_search_result_count" type="number" min="1" max="20" value={config.brave_search_result_count ?? 5} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('brave_search_result_count', e.target.value)} />
                                            </InputGroup>
                                        </SectionCard>
                                    </>
                                )}

                                {activeTab === 'browser' && (
                                    <>
                                        <SectionCard title="Browser Options" icon={<Globe className="w-4 h-4" />} color="text-rose-300" gradient="from-rose-500/8 to-pink-500/3">
                                            <ToggleGroup
                                                id="prefer_local_chrome"
                                                label="Prefer Local Chrome"
                                                desc="Use local Chrome instead of Playwright Chromium"
                                                checked={config.prefer_local_chrome ?? true}
                                                onChange={(checked) => handleChange('prefer_local_chrome', checked)}
                                                color="bg-gradient-to-r from-rose-400 to-pink-400"
                                            />
                                            <ToggleGroup
                                                id="keep_browser_open"
                                                label="Keep Browser Open"
                                                desc="Keep browser running after task completion"
                                                checked={config.keep_browser_open ?? true}
                                                onChange={(checked) => handleChange('keep_browser_open', checked)}
                                                color="bg-gradient-to-r from-rose-400 to-pink-400"
                                            />
                                            <ToggleGroup
                                                id="pw_headless_mode"
                                                label="Headless Mode"
                                                desc="Run browser without visible window"
                                                checked={config.pw_headless_mode || false}
                                                onChange={(checked) => handleChange('pw_headless_mode', checked)}
                                                color="bg-gradient-to-r from-rose-400 to-pink-400"
                                            />
                                        </SectionCard>

                                        <SectionCard title="Chrome Settings" icon={<Monitor className="w-4 h-4" />} color="text-pink-300" gradient="from-pink-500/8 to-rose-500/3">
                                            <InputGroup label="Chrome User Data Dir" desc="Path to Chrome profile">
                                                <Input name="chrome_user_data_dir" value={config.chrome_user_data_dir || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('chrome_user_data_dir', e.target.value)} placeholder=".chrome_user_data/" />
                                            </InputGroup>
                                            <InputGroup label="CDP Port" desc="Chrome DevTools Protocol port">
                                                <Input name="cdp_port" type="number" value={config.cdp_port ?? 9222} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('cdp_port', e.target.value)} />
                                            </InputGroup>
                                            <div className="grid grid-cols-2 gap-4">
                                                <InputGroup label="Window Width">
                                                    <Input name="pw_window_width" type="number" value={config.pw_window_width ?? 1920} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('pw_window_width', e.target.value)} />
                                                </InputGroup>
                                                <InputGroup label="Window Height">
                                                    <Input name="pw_window_height" type="number" value={config.pw_window_height ?? 1080} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('pw_window_height', e.target.value)} />
                                                </InputGroup>
                                            </div>
                                        </SectionCard>

                                        <SectionCard title="Timeouts (ms)" icon={<Clock className="w-4 h-4" />} color="text-amber-300" gradient="from-amber-500/8 to-yellow-500/3">
                                            <div className="grid grid-cols-3 gap-4">
                                                <InputGroup label="Page Load">
                                                    <Input name="pw_goto_timeout" type="number" value={config.pw_goto_timeout ?? 10000} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('pw_goto_timeout', e.target.value)} />
                                                </InputGroup>
                                                <InputGroup label="Click">
                                                    <Input name="pw_click_timeout" type="number" value={config.pw_click_timeout ?? 6000} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('pw_click_timeout', e.target.value)} />
                                                </InputGroup>
                                                <InputGroup label="CDP Connect">
                                                    <Input name="pw_cdp_timeout" type="number" value={config.pw_cdp_timeout ?? 1000} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('pw_cdp_timeout', e.target.value)} />
                                                </InputGroup>
                                            </div>
                                        </SectionCard>
                                    </>
                                )}
                            </div>
                        )}
                    </div>
                </div>

                {/* Footer */}
                <div className="px-6 py-4 border-t border-border/50 bg-gradient-to-r from-muted/20 to-transparent flex items-center justify-between">
                    <span className={cn(
                        "text-sm font-medium transition-colors",
                        statusMsg.startsWith("Error") ? "text-red-400" : "text-emerald-400"
                    )}>
                        {statusMsg}
                    </span>
                    <div className="flex gap-3">
                        <button
                            onClick={onClose}
                            className="px-5 py-2.5 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted/50 rounded-xl transition-all duration-200"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={handleSave}
                            disabled={isSaving || isLoading}
                            className={cn(
                                "flex items-center gap-2 px-5 py-2.5 text-sm font-medium text-white rounded-xl transition-all duration-200 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed",
                                "bg-gradient-to-r", currentTab.gradient.replace('/20', '').replace('/10', ''),
                                "hover:opacity-90"
                            )}
                            style={{
                                background: activeTab === 'model' ? 'linear-gradient(to right, #fbbf24, #f97316)' :
                                    activeTab === 'langsmith' ? 'linear-gradient(to right, #34d399, #2dd4bf)' :
                                        activeTab === 'logging' ? 'linear-gradient(to right, #38bdf8, #22d3ee)' :
                                            activeTab === 'exec-search' ? 'linear-gradient(to right, #a78bfa, #c084fc)' :
                                                'linear-gradient(to right, #fb7185, #f472b6)'
                            }}
                        >
                            {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                            Save Changes
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

// ===== Sub-components =====

function SectionCard({ title, icon, color, gradient, children }: { title: string; icon?: ReactNode; color?: string; gradient?: string; children: ReactNode }) {
    return (
        <div className={cn("bg-gradient-to-br border border-border/30 rounded-2xl p-5 space-y-4", gradient || "from-muted/20 to-muted/5")}>
            <div className="flex items-center gap-2 pb-3 border-b border-border/30">
                {icon && <span className={color || "text-primary/70"}>{icon}</span>}
                <h3 className={cn("text-sm font-semibold uppercase tracking-wider", color ? color.replace('text-', 'text-') : "text-muted-foreground")}>{title}</h3>
            </div>
            <div className="space-y-4">
                {children}
            </div>
        </div>
    );
}

function InputGroup({ label, desc, children }: { label: string; desc?: string; children: ReactNode }) {
    return (
        <div className="space-y-2">
            <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-foreground">{label}</label>
                {desc && <span className="text-xs text-muted-foreground">{desc}</span>}
            </div>
            {children}
        </div>
    );
}

function ToggleGroup({ id, label, desc, checked, onChange, color }: { id: string; label: string; desc?: string; checked: boolean; onChange: (checked: boolean) => void; color?: string }) {
    return (
        <div className="flex items-center justify-between py-2 group">
            <div className="flex flex-col gap-0.5">
                <label htmlFor={id} className="text-sm font-medium text-foreground cursor-pointer">{label}</label>
                {desc && <span className="text-xs text-muted-foreground">{desc}</span>}
            </div>
            <button
                id={id}
                role="switch"
                aria-checked={checked}
                onClick={() => onChange(!checked)}
                className={cn(
                    "relative w-11 h-6 rounded-full transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary/30",
                    checked ? (color || "bg-gradient-to-r from-primary to-primary/80") : "bg-muted/50"
                )}
            >
                <span className={cn(
                    "absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow-md transition-transform duration-300",
                    checked && "translate-x-5"
                )} />
            </button>
        </div>
    );
}

function Input({ className, ...props }: React.InputHTMLAttributes<HTMLInputElement>) {
    return (
        <input
            {...props}
            className={cn(
                "w-full bg-input/30 border border-input/50 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-all placeholder:text-muted-foreground/40",
                props.type === "password" && "font-mono tracking-wider",
                className
            )}
        />
    )
}

function StringListEditor({ label, desc, items, onChange, placeholder }: {
    label: string;
    desc?: string;
    items: string[];
    onChange: (items: string[]) => void;
    placeholder?: string;
}) {
    const [inputValue, setInputValue] = useState('');

    const handleAdd = () => {
        const trimmed = inputValue.trim();
        if (trimmed && !items.includes(trimmed)) {
            onChange([...items, trimmed]);
            setInputValue('');
        }
    };

    const handleRemove = (index: number) => {
        onChange(items.filter((_, i) => i !== index));
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleAdd();
        }
    };

    return (
        <div className="space-y-3">
            <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-foreground">{label}</label>
                {desc && <span className="text-xs text-muted-foreground">{desc}</span>}
            </div>

            {/* Input row */}
            <div className="flex gap-2">
                <input
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={placeholder}
                    className="flex-1 bg-input/30 border border-input/50 rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 transition-all placeholder:text-muted-foreground/40"
                />
                <button
                    type="button"
                    onClick={handleAdd}
                    className="px-4 py-2 text-sm font-medium bg-violet-500/20 text-violet-300 hover:bg-violet-500/30 rounded-xl transition-colors"
                >
                    Add
                </button>
            </div>

            {/* Tags */}
            {items.length > 0 && (
                <div className="flex flex-wrap gap-2">
                    {items.map((item, index) => (
                        <span
                            key={index}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-violet-500/15 text-violet-300 rounded-lg text-sm group"
                        >
                            {item}
                            <button
                                type="button"
                                onClick={() => handleRemove(index)}
                                className="w-4 h-4 flex items-center justify-center rounded-full hover:bg-violet-500/30 transition-colors"
                            >
                                ×
                            </button>
                        </span>
                    ))}
                </div>
            )}
        </div>
    );
}
