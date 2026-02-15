import { useEffect, useRef } from "react";

interface Star {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  alpha: number;
  twinkleSpeed: number;
  depth: number;
}

interface Meteor {
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  maxLife: number;
  length: number;
  alpha: number;
}

export function ParticleCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const starsRef = useRef<Star[]>([]);
  const meteorsRef = useRef<Meteor[]>([]);
  const mouseRef = useRef({ x: -1000, y: -1000 });
  const animationRef = useRef<number>(0);
  const sizeRef = useRef({ width: 0, height: 0 });
  const frameRef = useRef(0);
  const lastMeteorFrameRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const initStars = (width: number, height: number) => {
      const stars: Star[] = [];
      const count = Math.floor((width * height) / 4500);

      for (let i = 0; i < Math.min(count, 220); i++) {
        stars.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.06,
          vy: (Math.random() - 0.5) * 0.06,
          size: Math.random() * 1.6 + 0.5,
          alpha: Math.random() * 0.55 + 0.25,
          twinkleSpeed: Math.random() * 0.03 + 0.01,
          depth: Math.random() * 0.85 + 0.15,
        });
      }
      starsRef.current = stars;
    };

    const resize = () => {
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();

      sizeRef.current = { width: rect.width, height: rect.height };

      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;

      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(dpr, dpr);

      if (starsRef.current.length === 0) {
        initStars(rect.width, rect.height);
      }
    };

    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouseRef.current = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      };
    };

    const maybeSpawnMeteor = (width: number, height: number) => {
      if (meteorsRef.current.length >= 2) return;

      const minInterval = 480;
      const framesSinceLastMeteor = frameRef.current - lastMeteorFrameRef.current;
      if (framesSinceLastMeteor < minInterval) return;
      if (Math.random() >= 0.0015) return;

      const startX = Math.random() * width * 0.8;
      const startY = -20 - Math.random() * 80;
      const speed = Math.random() * 1.6 + 2.2;
      const angle = Math.PI / 3 + Math.random() * 0.4;
      const vx = Math.cos(angle) * speed;
      const vy = Math.sin(angle) * speed;
      const length = Math.random() * 130 + 80;
      const framesToExitX = (width + length - startX) / Math.max(vx, 0.001);
      const framesToExitY = (height + length - startY) / Math.max(vy, 0.001);
      const maxLife = Math.ceil(Math.max(framesToExitX, framesToExitY)) + 20;

      meteorsRef.current.push({
        x: startX,
        y: startY,
        vx,
        vy,
        life: 0,
        maxLife,
        length,
        alpha: Math.random() * 0.4 + 0.45,
      });
      lastMeteorFrameRef.current = frameRef.current;
    };

    const drawNebulaGlow = (width: number, height: number) => {
      const gradientA = ctx.createRadialGradient(
        width * 0.18,
        height * 0.22,
        0,
        width * 0.18,
        height * 0.22,
        width * 0.35
      );
      gradientA.addColorStop(0, "rgba(59, 130, 246, 0.12)");
      gradientA.addColorStop(1, "rgba(59, 130, 246, 0)");
      ctx.fillStyle = gradientA;
      ctx.fillRect(0, 0, width, height);

      const gradientB = ctx.createRadialGradient(
        width * 0.82,
        height * 0.68,
        0,
        width * 0.82,
        height * 0.68,
        width * 0.28
      );
      gradientB.addColorStop(0, "rgba(147, 51, 234, 0.1)");
      gradientB.addColorStop(1, "rgba(147, 51, 234, 0)");
      ctx.fillStyle = gradientB;
      ctx.fillRect(0, 0, width, height);
    };

    const animate = () => {
      frameRef.current += 1;
      const { width, height } = sizeRef.current;
      if (width === 0 || height === 0) {
        animationRef.current = requestAnimationFrame(animate);
        return;
      }

      ctx.clearRect(0, 0, width, height);
      drawNebulaGlow(width, height);

      const stars = starsRef.current;
      const mouse = mouseRef.current;

      const mouseInCanvas = mouse.x >= 0 && mouse.x <= width && mouse.y >= 0 && mouse.y <= height;

      for (const star of stars) {
        if (mouseInCanvas) {
          const dx = mouse.x - star.x;
          const dy = mouse.y - star.y;
          const distSq = dx * dx + dy * dy;
          const dist = Math.sqrt(distSq);

          if (dist < 150 && dist > 0) {
            const inverseSquareForce = 36 / Math.max(distSq, 36);
            const cappedForce = Math.min(inverseSquareForce, 0.01);
            star.vx += (dx / dist) * cappedForce * star.depth;
            star.vy += (dy / dist) * cappedForce * star.depth;
          }
        }

        const centerX = width / 2;
        const centerY = height / 2;
        const toCenterX = centerX - star.x;
        const toCenterY = centerY - star.y;
        star.vx += -toCenterY * 0.0000022 * star.depth;
        star.vy += toCenterX * 0.0000022 * star.depth;

        star.x += star.vx;
        star.y += star.vy;
        star.vx *= 0.985;
        star.vy *= 0.985;
        star.vx += (Math.random() - 0.5) * 0.006;
        star.vy += (Math.random() - 0.5) * 0.006;

        if (star.x < -15) star.x = width + 15;
        if (star.x > width + 15) star.x = -15;
        if (star.y < -15) star.y = height + 15;
        if (star.y > height + 15) star.y = -15;

        const twinkle = 0.65 + Math.sin(frameRef.current * star.twinkleSpeed + star.x * 0.01) * 0.35;
        const alpha = star.alpha * twinkle;

        ctx.beginPath();
        ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(226, 232, 255, ${alpha})`;
        ctx.fill();

        const glow = star.size * 2.4;
        ctx.beginPath();
        ctx.arc(star.x, star.y, glow, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(147, 197, 253, ${alpha * 0.16})`;
        ctx.fill();
      }

      maybeSpawnMeteor(width, height);

      meteorsRef.current = meteorsRef.current.filter((meteor) => meteor.life <= meteor.maxLife);
      for (const meteor of meteorsRef.current) {
        meteor.life += 1;
        meteor.x += meteor.vx;
        meteor.y += meteor.vy;

        const lifeProgress = meteor.life / meteor.maxLife;
        const fade = lifeProgress < 0.7 ? 1 : 1 - (lifeProgress - 0.7) / 0.3;
        const opacity = meteor.alpha * fade;

        const tailX = meteor.x - (meteor.vx / 14) * meteor.length;
        const tailY = meteor.y - (meteor.vy / 14) * meteor.length;
        const meteorGradient = ctx.createLinearGradient(meteor.x, meteor.y, tailX, tailY);
        meteorGradient.addColorStop(0, `rgba(255, 255, 255, ${opacity})`);
        meteorGradient.addColorStop(1, "rgba(147, 197, 253, 0)");

        ctx.beginPath();
        ctx.moveTo(meteor.x, meteor.y);
        ctx.lineTo(tailX, tailY);
        ctx.strokeStyle = meteorGradient;
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    const handleClick = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const clickY = e.clientY - rect.top;

      for (const star of starsRef.current) {
        const dx = star.x - clickX;
        const dy = star.y - clickY;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 150 && dist > 0) {
          const force = (150 - dist) / 150;
          star.vx += (dx / dist) * force * 5 * star.depth;
          star.vy += (dy / dist) * force * 5 * star.depth;
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
      cancelAnimationFrame(animationRef.current);
    };
  }, []);

  return <canvas ref={canvasRef} className="absolute inset-0 w-full h-full pointer-events-none" />;
}
