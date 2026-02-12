import { Zap, Clock, RefreshCw } from 'lucide-react';
import { ReactNode, useEffect, useState, useRef } from 'react';
import { useAppStore } from '../../stores/appStore';
import { HistoryList } from './History';
import { QuickStartList } from './QuickStart';
import { cn } from '../../lib/utils';



// ============================================================================
// Particle System with Fixed Mouse Tracking
// ============================================================================

interface Particle {
    x: number;
    y: number;
    vx: number;
    vy: number;
    size: number;
    opacity: number;
    hue: number;
}

function ParticleCanvas() {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const particlesRef = useRef<Particle[]>([]);
    const mouseRef = useRef({ x: -1000, y: -1000 });
    const animationRef = useRef<number>(0);
    const sizeRef = useRef({ width: 0, height: 0 });

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Initialize particles
        const initParticles = (width: number, height: number) => {
            const particles: Particle[] = [];
            const count = Math.floor((width * height) / 6000);

            for (let i = 0; i < Math.min(count, 100); i++) {
                particles.push({
                    x: Math.random() * width,
                    y: Math.random() * height,
                    vx: (Math.random() - 0.5) * 0.5,
                    vy: (Math.random() - 0.5) * 0.5,
                    size: Math.random() * 2 + 1,
                    opacity: Math.random() * 0.5 + 0.3,
                    // Diverse colors: cyan, purple, pink, amber, blue
                    hue: [180, 270, 330, 35, 210][Math.floor(Math.random() * 5)] + (Math.random() - 0.5) * 20,
                });
            }
            particlesRef.current = particles;
        };

        // Resize handler - reset context scale each time
        const resize = () => {
            const dpr = window.devicePixelRatio || 1;
            const rect = canvas.getBoundingClientRect();

            sizeRef.current = { width: rect.width, height: rect.height };

            canvas.width = rect.width * dpr;
            canvas.height = rect.height * dpr;

            ctx.setTransform(1, 0, 0, 1, 0, 0);
            ctx.scale(dpr, dpr);

            if (particlesRef.current.length === 0) {
                initParticles(rect.width, rect.height);
            }
        };

        // Mouse move - use document-level event for better tracking
        const handleMouseMove = (e: MouseEvent) => {
            const rect = canvas.getBoundingClientRect();
            mouseRef.current = {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top,
            };
        };

        // Animation loop
        const animate = () => {
            const { width, height } = sizeRef.current;
            if (width === 0 || height === 0) {
                animationRef.current = requestAnimationFrame(animate);
                return;
            }

            ctx.clearRect(0, 0, width, height);

            const particles = particlesRef.current;
            const mouse = mouseRef.current;

            // Check if mouse is within canvas bounds
            const mouseInCanvas = mouse.x >= 0 && mouse.x <= width && mouse.y >= 0 && mouse.y <= height;

            // Update and draw particles
            for (const p of particles) {
                // Mouse interaction - gentle attraction
                if (mouseInCanvas) {
                    const dx = mouse.x - p.x;
                    const dy = mouse.y - p.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < 180 && dist > 0) {
                        const force = (180 - dist) / 180;
                        p.vx += (dx / dist) * force * 0.03;
                        p.vy += (dy / dist) * force * 0.03;
                    }
                }

                // Slow orbital motion around center
                const centerX = width / 2;
                const centerY = height / 2;
                const toCenterX = centerX - p.x;
                const toCenterY = centerY - p.y;
                // Perpendicular direction for circular motion (counter-clockwise)
                p.vx += -toCenterY * 0.000008;
                p.vy += toCenterX * 0.000008;

                // Apply velocity with damping
                p.x += p.vx;
                p.y += p.vy;
                p.vx *= 0.96;
                p.vy *= 0.96;

                // Add random movement
                p.vx += (Math.random() - 0.5) * 0.03;
                p.vy += (Math.random() - 0.5) * 0.03;

                // Wrap around edges
                if (p.x < -10) p.x = width + 10;
                if (p.x > width + 10) p.x = -10;
                if (p.y < -10) p.y = height + 10;
                if (p.y > height + 10) p.y = -10;

                // Draw particle with glow
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                ctx.fillStyle = `hsla(${p.hue}, 85%, 65%, ${p.opacity})`;
                ctx.fill();
            }

            animationRef.current = requestAnimationFrame(animate);
        };

        // Click to scatter particles
        const handleClick = (e: MouseEvent) => {
            const rect = canvas.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const clickY = e.clientY - rect.top;

            for (const p of particlesRef.current) {
                const dx = p.x - clickX;
                const dy = p.y - clickY;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 200 && dist > 0) {
                    const force = (200 - dist) / 200;
                    // Scatter outward from click point
                    p.vx += (dx / dist) * force * 8;
                    p.vy += (dy / dist) * force * 8;
                }
            }
        };

        resize();
        window.addEventListener('resize', resize);
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('click', handleClick);
        animate();

        return () => {
            window.removeEventListener('resize', resize);
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('click', handleClick);
        };
    }, []);


    return (
        <canvas
            ref={canvasRef}
            className="absolute inset-0 w-full h-full pointer-events-none"
        />
    );
}

// ============================================================================
// Main Component
// ============================================================================

interface WelcomeScreenProps {
    onQuickStart: (text: string) => void;
}

export function WelcomeScreen({ onQuickStart }: WelcomeScreenProps) {
    const { theme } = useAppStore();
    const [isLoaded, setIsLoaded] = useState(false);
    const [refreshKey, setRefreshKey] = useState(0);

    const refreshQuickStarts = () => {
        setRefreshKey(prev => prev + 1);
    };

    const isHistoryOpen = useAppStore(s => s.isHistoryOpen);

    useEffect(() => {
        const timer = setTimeout(() => setIsLoaded(true), 50);
        return () => clearTimeout(timer);
    }, []);

    return (
        <div className="flex-1 flex flex-col overflow-hidden relative">

            {/* Interactive Particle Canvas */}
            <ParticleCanvas />

            {/* Center Hero */}
            <div className="flex-1 flex items-center justify-center z-10 pointer-events-none">
                <div className={cn(
                    "flex flex-col items-center transition-all duration-700 ease-out",
                    isLoaded ? "opacity-100 scale-100" : "opacity-0 scale-95"
                )}>

                    {/* Elegant Glowing Orb */}
                    <div className={cn(
                        "relative mb-8 transition-all duration-500 delay-100",
                        isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
                    )}>
                        <div className="relative w-24 h-24 flex items-center justify-center">
                            {/* Outer soft glow */}
                            <div className="absolute w-36 h-36 bg-amber-500/15 blur-2xl rounded-full" />

                            {/* Rotating ring */}
                            <div className="absolute w-24 h-24 rounded-full border border-amber-500/20 animate-spin-slow" />

                            {/* Inner Glow effects - Dark Mode Only */}
                            {theme === 'dark' && (
                                <>
                                    <div className="absolute w-12 h-12 bg-amber-400/25 blur-xl rounded-full" />
                                    <div className="absolute w-6 h-6 bg-amber-300/50 blur-md rounded-full" />
                                </>
                            )}

                            {/* Core orb - Dynamic in Dark Mode, Static in Light Mode */}
                            <div className={cn(
                                "relative w-4 h-4 rounded-full",
                                theme === 'dark' ? "bg-amber-400 animate-rainbow-pulse" : "bg-amber-400"
                            )} />
                        </div>
                    </div>

                    {/* Title */}
                    <h1 className={cn(
                        "text-2xl font-light tracking-[0.3em] text-foreground/90 mb-1 transition-all duration-500 delay-200",
                        isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
                    )}>
                        HALLW
                    </h1>

                    {/* Tagline */}
                    <p className={cn(
                        "text-xs text-muted-foreground/50 tracking-[0.2em] uppercase transition-all duration-500 delay-300",
                        isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
                    )}>
                        Autonomous Workspace
                    </p>
                </div>
            </div>

            {/* Bottom - Quick Start / History Toggle Area */}
            <div className={cn(
                "w-full max-w-2xl mx-auto px-6 pb-6 z-10 transition-all duration-700 delay-400",
                isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
            )}>
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2 relative h-6 w-48">
                        {/* Quick Start Header */}
                        <div className={cn(
                            "flex items-center gap-2 transition-all duration-500 ease-in-out",
                            isHistoryOpen ? "opacity-0 -translate-y-2 pointer-events-none" : "opacity-100 translate-y-0"
                        )}>
                            <div className="relative flex items-center justify-center w-5 h-5 shrink-0">
                                {theme === 'dark' && <div className="absolute inset-0 bg-amber-400/60 blur-lg rounded-full animate-pulse" />}
                                <Zap className={cn("relative w-3.5 h-3.5", theme === 'dark' ? "text-amber-400 drop-shadow-[0_0_4px_rgba(251,191,36,0.8)]" : "text-amber-600")} />
                            </div>
                            <span className={cn(
                                "text-[12px] uppercase tracking-[0.2em] whitespace-nowrap",
                                theme === 'dark' ? "font-light text-amber-300 drop-shadow-[0_0_8px_rgba(251,191,36,0.8)]" : "font-medium text-amber-600"
                            )}>
                                Quick Start
                            </span>
                        </div>

                        {/* History Header */}
                        <div className={cn(
                            "absolute inset-0 flex items-center gap-2 transition-all duration-500 ease-in-out",
                            isHistoryOpen ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2 pointer-events-none"
                        )}>
                            <div className="relative flex items-center justify-center w-5 h-5 shrink-0">
                                {theme === 'dark' && <div className="absolute inset-0 bg-emerald-400/60 blur-lg rounded-full animate-pulse" />}
                                <Clock className={cn("relative w-3.5 h-3.5", theme === 'dark' ? "text-emerald-400 drop-shadow-[0_0_4px_rgba(52,211,153,0.8)]" : "text-emerald-600")} />
                            </div>
                            <span className={cn(
                                "text-[12px] uppercase tracking-[0.2em] whitespace-nowrap",
                                theme === 'dark' ? "font-light text-emerald-300 drop-shadow-[0_0_8px_rgba(52,211,153,0.8)]" : "font-medium text-emerald-600"
                            )}>
                                History
                            </span>
                        </div>
                    </div>

                    {!isHistoryOpen && (
                        <button
                            onClick={refreshQuickStarts}
                            className="group p-1.5 rounded-lg text-muted-foreground/40 hover:text-foreground/60 hover:bg-white/5 transition-all duration-200 active:scale-90"
                            title="Shuffle prompts"
                        >
                            <RefreshCw className="w-3.5 h-3.5 transition-transform duration-500 group-hover:rotate-180" />
                        </button>
                    )}
                </div>

                <div className="relative h-[192px] overflow-hidden pt-1">
                    {/* Quick Start List */}
                    <QuickStartList
                        onQuickStart={onQuickStart}
                        isVisible={!isHistoryOpen}
                        refreshKey={refreshKey}
                    />

                    {/* History List */}
                    <HistoryList
                        isVisible={isHistoryOpen}
                    />
                </div>
            </div>
        </div>
    );
}
