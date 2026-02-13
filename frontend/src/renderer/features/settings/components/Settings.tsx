import { X, Loader2, Settings2 } from 'lucide-react';
import { useState } from 'react';
import { cn } from '@lib/utils';
import { ModelPage } from './pages/ModelPage';
import { KeysPage } from './pages/KeysPage';
import { LangSmithPage } from './pages/LangSmithPage';
import { LoggingPage } from './pages/LoggingPage';
import { ExecutionPage } from './pages/ExecutionPage';
import { SearchPage } from './pages/SearchPage';
import { BrowserPage } from './pages/BrowserPage';
import { AppearancePage } from './pages/AppearancePage';
import { TABS } from '../constants';
import { useSettingsSocket } from '../hooks/useSettingsSocket';
import { useAppStore } from '@store/store';
import { SaveStatusIndicator } from './SaveStatusIndicator';

export function Settings({ isOpen }: { isOpen: boolean }) {
    const [activeTab, setActiveTab] = useState('model');
    const toggleSettings = useAppStore(s => s.toggleSettings);
    const {
        config,
        isLoading,
        handleChange
    } = useSettingsSocket(isOpen);

    const currentTab = TABS.find(t => t.id === activeTab) || TABS[0];

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
                        onClick={() => toggleSettings()}
                        className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-all duration-200"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Main Content Area */}
                <div className="flex flex-1 overflow-hidden">
                    {/* Sidebar Tabs */}
                    <div className="w-52 border-r border-border/30 bg-muted/5 p-4 flex flex-col flex-shrink-0">
                        <div className="space-y-1 flex-1">
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
                        {/* Save status indicator */}
                        <SaveStatusIndicator />
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
                                {activeTab === 'model' && <ModelPage config={config} handleChange={handleChange} />}
                                {activeTab === 'api-keys' && <KeysPage config={config} handleChange={handleChange} />}
                                {activeTab === 'langsmith' && <LangSmithPage config={config} handleChange={handleChange} />}
                                {activeTab === 'logging' && <LoggingPage config={config} handleChange={handleChange} />}
                                {activeTab === 'exec' && <ExecutionPage config={config} handleChange={handleChange} />}
                                {activeTab === 'search' && <SearchPage config={config} handleChange={handleChange} />}
                                {activeTab === 'browser' && <BrowserPage config={config} handleChange={handleChange} />}
                                {activeTab === 'appearance' && <AppearancePage config={config} handleChange={handleChange} />}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
