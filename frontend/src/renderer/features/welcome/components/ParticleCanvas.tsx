import { useEffect, useRef } from "react";

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  opacity: number;
  hue: number;
}

export function ParticleCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const mouseRef = useRef({ x: -1000, y: -1000 });
  const animationRef = useRef<number>(0);
  const sizeRef = useRef({ width: 0, height: 0 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
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
    window.addEventListener("resize", resize);
    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("click", handleClick);
    animate();

    return () => {
      window.removeEventListener("resize", resize);
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("click", handleClick);
    };
  }, []);

  return <canvas ref={canvasRef} className="absolute inset-0 w-full h-full pointer-events-none" />;
}
