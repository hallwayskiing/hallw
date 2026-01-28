import { Sparkles, Bot, Terminal, Globe, FileText, Command, House, LucideIcon } from 'lucide-react';
import { cn } from '../lib/utils';
import { ReactNode } from 'react';

interface WelcomeScreenProps {
    onQuickStart: (text: string) => void;
}

export function WelcomeScreen({ onQuickStart }: WelcomeScreenProps) {
    return (
        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center animate-in fade-in duration-500">
            <div className="max-w-5xl w-full text-left space-y-8">

                {/* Header */}
                <div>
                    <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                        HALLW • Autonomous Workspace
                    </h2>
                    <h1 className="text-4xl font-bold text-foreground flex items-center gap-3 mb-4">
                        <Sparkles className="w-8 h-8 text-amber-400 fill-amber-400/20" />
                        HALLW - Your AI Assistant
                    </h1>
                    <p className="text-lg text-muted-foreground mb-2">
                        Orchestrate web automation, file operations, and system commands.
                    </p>
                    <p className="text-sm text-muted-foreground">
                        Think in natural language — HALLW turns it into deterministic workflows.
                    </p>
                </div>

                {/* Features Layout */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <FeatureCard icon={Bot} title="Core Skills" color="text-pink-500">
                        <ul className="text-sm text-muted-foreground space-y-1 mt-2">
                            <li>• Browse and extract information</li>
                            <li>• Analyze and transform documents</li>
                            <li>• Generate code, scripts, and reports</li>
                        </ul>
                    </FeatureCard>
                    <FeatureCard icon={Terminal} title="Automation" color="text-purple-500">
                        <ul className="text-sm text-muted-foreground space-y-1 mt-2">
                            <li>• Run multi-stage workflows</li>
                            <li>• Think with reflection</li>
                            <li>• Keep a structured task history</li>
                        </ul>
                    </FeatureCard>
                    <FeatureCard icon={Command} title="Environment" color="text-blue-500">
                        <ul className="text-sm text-muted-foreground space-y-1 mt-2">
                            <li>• Local-first desktop agent</li>
                            <li>• Transparent tool usage</li>
                            <li>• Human-in-the-loop approvals</li>
                        </ul>
                    </FeatureCard>
                </div>

                {/* Quick Start */}
                <div className="pt-8">
                    <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4">
                        Quick Start
                    </h3>
                    <div className="space-y-2">
                        <QuickStartItem
                            icon={<FileText className="w-4 h-4 text-emerald-400" />}
                            text="Summarize today's tech headlines and save as tech_news.md."
                            onClick={onQuickStart}
                        />
                        <QuickStartItem
                            icon={<Globe className="w-4 h-4 text-orange-400" />}
                            text="Learn how to cook a Chinese dish and create recipe.md."
                            onClick={onQuickStart}
                        />
                        <QuickStartItem
                            icon={<House className="w-4 h-4 text-blue-400" />}
                            text="Find and tell me ten interesting places to visit in Paris."
                            onClick={onQuickStart}
                        />
                    </div>
                </div>

            </div>
        </div>
    );
}

interface FeatureCardProps {
    icon: LucideIcon;
    title: string;
    children: ReactNode;
    color: string;
}

function FeatureCard({ icon: Icon, title, children, color }: FeatureCardProps) {
    return (
        <div className="p-4 rounded-lg bg-card/5 border border-border/50">
            <div className="flex items-center gap-2 mb-2">
                <Icon className={cn("w-5 h-5", color)} />
                <h3 className="font-medium text-foreground">{title}</h3>
            </div>
            {children}
        </div>
    )
}

interface QuickStartItemProps {
    icon: ReactNode;
    text: string;
    onClick: (text: string) => void;
}

function QuickStartItem({ icon, text, onClick }: QuickStartItemProps) {
    return (
        <button
            onClick={() => onClick(text)}
            className="w-full flex items-center gap-3 p-3 text-left rounded-md hover:bg-white/5 transition-colors group"
        >
            {icon}
            <span className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">
                {text}
            </span>
        </button>
    )
}
