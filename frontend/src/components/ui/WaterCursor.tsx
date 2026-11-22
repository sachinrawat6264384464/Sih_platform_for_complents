"use client";

import React, { useEffect, useRef } from "react";
import { useTheme } from "@/lib/theme";

interface Particle {
  x: number;
  y: number;
  radius: number;
  maxRadius: number;
  alpha: number;
  color: string;
}

export function WaterCursor() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const { theme } = useTheme();

  useEffect(() => {
    // Only run on devices with a mouse/pointer (not touch)
    if (typeof window === "undefined" || window.matchMedia("(pointer: coarse)").matches) {
      return;
    }

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    let particles: Particle[] = [];
    let lastTime = 0;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    const onPointerMove = (e: MouseEvent) => {
      const now = performance.now();
      // Throttle creation to 25ms
      if (now - lastTime < 25) return;
      lastTime = now;

      const isDark = theme === "dark";
      const color = isDark ? "rgba(0, 229, 255," : "rgba(22, 134, 203,";

      particles.push({
        x: e.clientX,
        y: e.clientY,
        radius: 3,
        maxRadius: 28,
        alpha: 0.35,
        color,
      });

      // Keep array reasonable
      if (particles.length > 40) {
        particles.shift();
      }
    };

    window.addEventListener("mousemove", onPointerMove, { passive: true });

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        p.radius += 0.8;
        p.alpha -= 0.012;

        if (p.alpha > 0) {
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
          ctx.strokeStyle = `${p.color} ${p.alpha})`;
          ctx.lineWidth = 1.2;
          ctx.stroke();
        }
      }

      particles = particles.filter((p) => p.alpha > 0);
      animationFrameId = requestAnimationFrame(render);
    };

    animationFrameId = requestAnimationFrame(render);

    return () => {
      window.removeEventListener("resize", resize);
      window.removeEventListener("mousemove", onPointerMove);
      cancelAnimationFrame(animationFrameId);
    };
  }, [theme]);

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none fixed inset-0 z-50 h-full w-full"
      style={{ mixBlendMode: theme === "dark" ? "screen" : "multiply" }}
    />
  );
}

