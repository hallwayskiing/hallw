import { ReactNode } from 'react';
import { cn } from '@lib/utils';

export function SectionCard({ title, icon, color, gradient, children }: { title: string; icon?: ReactNode; color?: string; gradient?: string; children: ReactNode }) {
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
