import { FileText, Globe, House, Code, Search, Mail, Calendar, Music, Camera, Coffee, Zap } from 'lucide-react';
import { ReactNode, useEffect, useState, useMemo, useRef } from 'react';
import { cn } from '../lib/utils';

// ============================================================================
// Quick Start Data
// ============================================================================

const ALL_QUICK_STARTS = [
    { icon: <FileText className="w-4 h-4" />, color: 'emerald', text: "Summarize today's tech headlines and save as tech_news.md." },
    { icon: <Globe className="w-4 h-4" />, color: 'orange', text: "Learn how to cook a Chinese dish and create recipe.md." },
    { icon: <House className="w-4 h-4" />, color: 'blue', text: "Find and tell me ten interesting places to visit in Paris." },
    { icon: <Code className="w-4 h-4" />, color: 'purple', text: "Create a simple Python script that generates random passwords." },
    { icon: <Search className="w-4 h-4" />, color: 'pink', text: "Research the latest AI trends and summarize key findings." },
    { icon: <Mail className="w-4 h-4" />, color: 'cyan', text: "Draft a professional email template for job applications." },
    { icon: <Calendar className="w-4 h-4" />, color: 'amber', text: "Create a weekly study schedule and save it as schedule.md." },
    { icon: <Music className="w-4 h-4" />, color: 'rose', text: "Find top 10 relaxing instrumental music for studying." },
    { icon: <Camera className="w-4 h-4" />, color: 'teal', text: "Research best practices for smartphone photography." },
    { icon: <Coffee className="w-4 h-4" />, color: 'yellow', text: "Find the best coffee shops near Times Square, New York." },
] as const;

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
    const mouseRef = useRef({ x: -1000, y: -1000 }); // Start off-screen
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

            ctx.setTransform(1, 0, 0, 1, 0, 0); // Reset transform
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
                p.vx += -toCenterY * 0.000012;
                p.vy += toCenterX * 0.000012;

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
            cancelAnimationFrame(animationRef.current);
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
    const [isLoaded, setIsLoaded] = useState(false);

    const quickStarts = useMemo(() => {
        const shuffled = [...ALL_QUICK_STARTS].sort(() => Math.random() - 0.5);
        return shuffled.slice(0, 3);
    }, []);

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

                    {/* Elegant Logo - Abstract Shape */}
                    <div className={cn(
                        "relative mb-6 transition-all duration-500 delay-100",
                        isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
                    )}>
                        {/* Outer glow */}
                        <div className="absolute -inset-4 rounded-full bg-amber-500/10 blur-2xl animate-pulse" />

                        {/* Logo Container */}
                        <div className="relative w-20 h-20 flex items-center justify-center">
                            {/* Rotating ring */}
                            <div className="absolute inset-0 rounded-full border border-amber-500/30 animate-spin-slow" />

                            {/* Inner circle */}
                            <div className="absolute inset-2 rounded-full bg-gradient-to-br from-amber-500/20 to-orange-500/10" />

                            {/* Center dot */}
                            <div className="w-3 h-3 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 shadow-lg shadow-amber-500/50" />
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

            {/* Bottom - Quick Start */}
            <div className={cn(
                "w-full max-w-2xl mx-auto px-6 pb-6 z-10 transition-all duration-500 delay-400",
                isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
            )}>
                <div className="flex items-center gap-2 mb-3">
                    <Zap className="w-3 h-3 text-amber-500/50" />
                    <span className="text-[12px] text-muted-foreground/40 uppercase tracking-[0.2em]">
                        Quick Start
                    </span>
                </div>
                <div className="grid grid-cols-1 gap-2">
                    {quickStarts.map((item, idx) => (
                        <QuickStartCard
                            key={idx}
                            icon={item.icon}
                            color={item.color as ColorName}
                            text={item.text}
                            onClick={onQuickStart}
                            delay={100}
                            isLoaded={isLoaded}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
}

// ============================================================================
// Quick Start Card
// ============================================================================

type ColorName = 'emerald' | 'orange' | 'blue' | 'purple' | 'pink' | 'cyan' | 'amber' | 'rose' | 'teal' | 'yellow';

const colorMap: Record<ColorName, { bg: string; border: string; icon: string }> = {
    emerald: { bg: 'hover:bg-emerald-500/5', border: 'hover:border-emerald-500/30', icon: 'text-emerald-400' },
    orange: { bg: 'hover:bg-orange-500/5', border: 'hover:border-orange-500/30', icon: 'text-orange-400' },
    blue: { bg: 'hover:bg-blue-500/5', border: 'hover:border-blue-500/30', icon: 'text-blue-400' },
    purple: { bg: 'hover:bg-purple-500/5', border: 'hover:border-purple-500/30', icon: 'text-purple-400' },
    pink: { bg: 'hover:bg-pink-500/5', border: 'hover:border-pink-500/30', icon: 'text-pink-400' },
    cyan: { bg: 'hover:bg-cyan-500/5', border: 'hover:border-cyan-500/30', icon: 'text-cyan-400' },
    amber: { bg: 'hover:bg-amber-500/5', border: 'hover:border-amber-500/30', icon: 'text-amber-400' },
    rose: { bg: 'hover:bg-rose-500/5', border: 'hover:border-rose-500/30', icon: 'text-rose-400' },
    teal: { bg: 'hover:bg-teal-500/5', border: 'hover:border-teal-500/30', icon: 'text-teal-400' },
    yellow: { bg: 'hover:bg-yellow-500/5', border: 'hover:border-yellow-500/30', icon: 'text-yellow-400' },
};

interface QuickStartCardProps {
    icon: ReactNode;
    color: ColorName;
    text: string;
    onClick: (text: string) => void;
    delay: number;
    isLoaded: boolean;
}

function QuickStartCard({ icon, color, text, onClick, delay, isLoaded }: QuickStartCardProps) {
    const colors = colorMap[color] || colorMap.blue;

    return (
        <button
            onClick={() => onClick(text)}
            className={cn(
                "group w-full flex items-center gap-3 p-3 text-left rounded-xl",
                "bg-card/20 backdrop-blur-sm border border-border/30",
                "transition-all duration-200 ease-out",
                colors.bg, colors.border,
                "hover:shadow-lg hover:-translate-y-0.5",
                "active:scale-[0.99]",
                isLoaded ? "opacity-100 translate-x-0" : "opacity-0 -translate-x-4"
            )}
            style={{ transitionDelay: isLoaded ? `${delay}ms` : '0ms' }}
        >
            <div className={cn("flex items-center justify-center w-7 h-7 rounded-lg bg-white/5 transition-transform duration-200 group-hover:scale-110", colors.icon)}>
                {icon}
            </div>
            <span className="flex-1 text-sm text-muted-foreground/80 group-hover:text-foreground transition-colors duration-200">
                {text}
            </span>
            <span className="text-muted-foreground/20 group-hover:text-foreground/40 group-hover:translate-x-1 transition-all duration-200">
                →
            </span>
        </button>
    );
}
