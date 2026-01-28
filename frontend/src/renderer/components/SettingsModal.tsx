import { X, Save, RotateCcw, Loader2 } from 'lucide-react';
import { useState, useEffect, ReactNode, ChangeEvent } from 'react';
import { useSocket } from '../contexts/SocketContext';
import { cn } from '../lib/utils';

interface SettingsModalProps {
    isOpen: boolean;
    onClose: () => void;
}

interface Config {
    [key: string]: any;
    model_name?: string;
    model_endpoint?: string;
    model_api_key?: string;
    model_temperature?: number;
    model_max_recursion?: number;
    langsmith_tracing?: boolean;
    langsmith_project?: string;
    langsmith_api_key?: string;
    langsmith_endpoint?: string;
    logging_level?: string;
    logging_file_dir?: string;
    keep_browser_open?: boolean;
    pw_headless_mode?: boolean;
    chrome_user_data_dir?: string;
    cdp_port?: number;
    pw_window_width?: number;
    pw_window_height?: number;
    pw_goto_timeout?: number;
    pw_click_timeout?: number;
    manual_captcha_timeout?: number;
    file_read_dir?: string;
    file_save_dir?: string;
    file_max_read_chars?: number;
}

interface ServerResponse {
    success: boolean;
    error?: string;
}

export function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
    const { socket } = useSocket();
    const [activeTab, setActiveTab] = useState('Model');
    const [config, setConfig] = useState<Config>({});
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [statusMsg, setStatusMsg] = useState('');

    useEffect(() => {
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
    }, [isOpen, socket]);

    const handleChange = (key: string, value: any) => {
        // Convert numbers
        if (['model_temperature', 'model_max_output_tokens', 'model_reflection_threshold', 'model_max_recursion',
            'pw_cdp_port', 'pw_window_width', 'pw_window_height', 'search_result_count', 'max_page_content_chars',
            'manual_captcha_timeout', 'pw_goto_timeout', 'pw_click_timeout', 'pw_cdp_timeout', 'file_max_read_chars'
        ].includes(key)) {
            value = Number(value);
        }
        // Convert booleans (checkboxes usually pass boolean directly, but ensure)

        setConfig(prev => ({ ...prev, [key]: value }));
    };

    const handleSave = () => {
        if (socket) {
            setIsSaving(true);
            setStatusMsg('Saving...');
            socket.emit('update_config', config);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 animate-in fade-in duration-200">
            <div className="w-[800px] h-[600px] bg-card border border-border rounded-lg shadow-2xl flex flex-col animate-in zoom-in-95 duration-200">

                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-background/50">
                    <h2 className="font-semibold text-lg">Settings</h2>
                    <button onClick={onClose} className="text-muted-foreground hover:text-foreground transition-colors">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Main Content Area */}
                <div className="flex flex-1 overflow-hidden">
                    {/* Sidebar Tabs */}
                    <div className="w-48 border-r border-border bg-muted/10 p-4 space-y-1">
                        {['Model', 'LangSmith', 'Logging', 'Browser', 'File'].map(tab => (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab)}
                                className={cn(
                                    "w-full text-left px-3 py-2 rounded-md text-sm font-medium transition-colors",
                                    activeTab === tab
                                        ? "bg-primary/10 text-primary"
                                        : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                                )}
                            >
                                {tab}
                            </button>
                        ))}
                    </div>

                    {/* Form Area */}
                    <div className="flex-1 p-6 overflow-y-auto bg-background/30">
                        {isLoading ? (
                            <div className="flex items-center justify-center h-full">
                                <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
                            </div>
                        ) : (
                            <div className="space-y-6 max-w-2xl">
                                {activeTab === 'Model' && (
                                    <>
                                        <SectionTitle>LLM Configuration</SectionTitle>
                                        <InputGroup label="Model Name" desc="Model name to use">
                                            <Input name="model_name" value={config.model_name || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('model_name', e.target.value)} />
                                        </InputGroup>
                                        <InputGroup label="Endpoint" desc="Base URL for the model API">
                                            <Input name="model_endpoint" value={config.model_endpoint || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('model_endpoint', e.target.value)} />
                                        </InputGroup>
                                        <InputGroup label="API Key" desc="Secret key for authentication">
                                            <Input name="model_api_key" type="password" value={config.model_api_key || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('model_api_key', e.target.value)} />
                                        </InputGroup>
                                        <div className="grid grid-cols-2 gap-4">
                                            <InputGroup label="Temperature" desc="0.0 - 1.0">
                                                <Input name="model_temperature" type="number" step="0.1" value={config.model_temperature || 0} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('model_temperature', e.target.value)} />
                                            </InputGroup>
                                            <InputGroup label="Max Recursion" desc="Limit loops">
                                                <Input name="model_max_recursion" type="number" value={config.model_max_recursion || 0} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('model_max_recursion', e.target.value)} />
                                            </InputGroup>
                                        </div>
                                    </>
                                )}

                                {activeTab === 'LangSmith' && (
                                    <>
                                        <SectionTitle>Tracing & Observability</SectionTitle>
                                        <div className="flex items-center gap-2 mb-4">
                                            <input
                                                type="checkbox"
                                                id="ls_enabled"
                                                checked={config.langsmith_tracing || false}
                                                onChange={(e) => handleChange('langsmith_tracing', e.target.checked)}
                                                className="w-4 h-4 rounded border-input"
                                            />
                                            <label htmlFor="ls_enabled" className="text-sm font-medium">Enable LangSmith Tracing</label>
                                        </div>
                                        <InputGroup label="Project Name">
                                            <Input name="langsmith_project" value={config.langsmith_project || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('langsmith_project', e.target.value)} />
                                        </InputGroup>
                                        <InputGroup label="API Key">
                                            <Input name="langsmith_api_key" type="password" value={config.langsmith_api_key || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('langsmith_api_key', e.target.value)} />
                                        </InputGroup>
                                        <InputGroup label="Endpoint">
                                            <Input name="langsmith_endpoint" value={config.langsmith_endpoint || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('langsmith_endpoint', e.target.value)} />
                                        </InputGroup>
                                    </>
                                )}

                                {activeTab === 'Logging' && (
                                    <>
                                        <SectionTitle>System Logging</SectionTitle>
                                        <InputGroup label="Log Level" desc="INFO, DEBUG, WARNING, ERROR">
                                            <select
                                                className="w-full bg-input/50 border border-input rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
                                                value={config.logging_level || 'INFO'}
                                                onChange={(e) => handleChange('logging_level', e.target.value)}
                                            >
                                                <option value="DEBUG">DEBUG</option>
                                                <option value="INFO">INFO</option>
                                                <option value="WARNING">WARNING</option>
                                                <option value="ERROR">ERROR</option>
                                            </select>
                                        </InputGroup>
                                        <InputGroup label="Log Directory">
                                            <Input name="logging_file_dir" value={config.logging_file_dir || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('logging_file_dir', e.target.value)} />
                                        </InputGroup>
                                    </>
                                )}

                                {activeTab === 'Browser' && (
                                    <>
                                        <SectionTitle>Browser Automation (Playwright)</SectionTitle>
                                        <div className="flex items-center gap-2 mb-4">
                                            <input
                                                type="checkbox"
                                                id="keep_browser"
                                                checked={config.keep_browser_open || false}
                                                onChange={(e) => handleChange('keep_browser_open', e.target.checked)}
                                                className="w-4 h-4 rounded border-input"
                                            />
                                            <label htmlFor="keep_browser" className="text-sm font-medium">Keep Browser Open</label>
                                        </div>
                                        <div className="flex items-center gap-2 mb-4">
                                            <input
                                                type="checkbox"
                                                id="headless"
                                                checked={config.pw_headless_mode || false}
                                                onChange={(e) => handleChange('pw_headless_mode', e.target.checked)}
                                                className="w-4 h-4 rounded border-input"
                                            />
                                            <label htmlFor="headless" className="text-sm font-medium">Headless Mode</label>
                                        </div>
                                        <InputGroup label="User Data Dir" desc="Path to Chrome profile">
                                            <Input name="chrome_user_data_dir" value={config.chrome_user_data_dir || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('chrome_user_data_dir', e.target.value)} />
                                        </InputGroup>
                                        <InputGroup label="CDP Port">
                                            <Input name="cdp_port" type="number" value={config.cdp_port || 0} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('cdp_port', e.target.value)} />
                                        </InputGroup>

                                        <div className="grid grid-cols-2 gap-4">
                                            <InputGroup label="Window Width">
                                                <Input name="pw_window_width" type="number" value={config.pw_window_width || 0} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('pw_window_width', e.target.value)} />
                                            </InputGroup>
                                            <InputGroup label="Window Height">
                                                <Input name="pw_window_height" type="number" value={config.pw_window_height || 0} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('pw_window_height', e.target.value)} />
                                            </InputGroup>
                                        </div>

                                        <SectionTitle className="mt-6">Timeouts (ms)</SectionTitle>
                                        <div className="grid grid-cols-2 gap-4">
                                            <InputGroup label="Page Load">
                                                <Input name="pw_goto_timeout" type="number" value={config.pw_goto_timeout || 0} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('pw_goto_timeout', e.target.value)} />
                                            </InputGroup>
                                            <InputGroup label="Click">
                                                <Input name="pw_click_timeout" type="number" value={config.pw_click_timeout || 0} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('pw_click_timeout', e.target.value)} />
                                            </InputGroup>
                                            <InputGroup label="Manual Captcha">
                                                <Input name="manual_captcha_timeout" type="number" value={config.manual_captcha_timeout || 0} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('manual_captcha_timeout', e.target.value)} />
                                            </InputGroup>
                                        </div>
                                    </>
                                )}

                                {activeTab === 'File' && (
                                    <>
                                        <SectionTitle>File System</SectionTitle>
                                        <InputGroup label="Working Directory" desc="Root for file reads">
                                            <Input name="file_read_dir" value={config.file_read_dir || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('file_read_dir', e.target.value)} />
                                        </InputGroup>
                                        <InputGroup label="Save Directory" desc="Where to save artifacts">
                                            <Input name="file_save_dir" value={config.file_save_dir || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('file_save_dir', e.target.value)} />
                                        </InputGroup>
                                        <InputGroup label="Max Read Chars">
                                            <Input name="file_max_read_chars" type="number" value={config.file_max_read_chars || 0} onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('file_max_read_chars', e.target.value)} />
                                        </InputGroup>
                                    </>
                                )}
                            </div>
                        )}
                    </div>
                </div>

                {/* Footer */}
                <div className="px-6 py-4 border-t border-border bg-muted/20 flex items-center justify-between">
                    <span className={cn("text-sm transition-colors", statusMsg.startsWith("Error") ? "text-red-500" : "text-green-500")}>
                        {statusMsg}
                    </span>
                    <div className="flex gap-3">
                        <button
                            onClick={onClose}
                            className="px-4 py-2 text-sm text-foreground hover:bg-muted/80 rounded-md transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={handleSave}
                            disabled={isSaving || isLoading}
                            className="flex items-center gap-2 px-4 py-2 text-sm bg-primary text-primary-foreground hover:bg-primary/90 rounded-md transition-colors shadow-sm disabled:opacity-50"
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

function SectionTitle({ children, className }: { children: ReactNode; className?: string }) {
    return <h3 className={cn("text-sm font-semibold uppercase tracking-wider text-muted-foreground border-b border-border pb-2 mb-4", className)}>{children}</h3>;
}

function InputGroup({ label, desc, children }: { label: string; desc?: string; children: ReactNode }) {
    return (
        <div className="space-y-1.5">
            <div className="flex justify-between items-baseline">
                <label className="text-sm font-medium text-foreground">{label}</label>
                {desc && <span className="text-xs text-muted-foreground">{desc}</span>}
            </div>
            {children}
        </div>
    );
}

function Input({ className, ...props }: React.InputHTMLAttributes<HTMLInputElement>) {
    return (
        <input
            {...props}
            defaultValue={undefined} // Controlled component
            className={cn(
                "w-full bg-input/50 border border-input rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring transition-all placeholder:text-muted-foreground/50",
                props.type === "password" && "font-mono",
                className
            )}
        />
    )
}
