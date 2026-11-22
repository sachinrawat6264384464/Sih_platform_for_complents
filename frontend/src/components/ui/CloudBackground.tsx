"use client";

import React from "react";
import { useTheme } from "@/lib/theme";

export function CloudBackground() {
  const { theme } = useTheme();
  const isDark = theme === "dark";

  return (
    <div className="pointer-events-none fixed inset-0 overflow-hidden z-0 select-none">
      {/* Ambient Radial Gradient Mesh */}
      <div
        className="absolute -top-40 -left-40 h-[650px] w-[650px] rounded-full blur-[140px] transition-colors duration-1000"
        style={{
          background: isDark
            ? "radial-gradient(circle, rgba(242, 140, 40, 0.08) 0%, rgba(11, 23, 48, 0) 70%)"
            : "radial-gradient(circle, rgba(22, 134, 203, 0.12) 0%, rgba(241, 248, 255, 0) 70%)",
        }}
      />
      <div
        className="absolute top-1/3 -right-40 h-[700px] w-[700px] rounded-full blur-[150px] transition-colors duration-1000"
        style={{
          background: isDark
            ? "radial-gradient(circle, rgba(0, 229, 255, 0.06) 0%, rgba(11, 23, 48, 0) 70%)"
            : "radial-gradient(circle, rgba(217, 119, 6, 0.08) 0%, rgba(241, 248, 255, 0) 70%)",
        }}
      />

      {/* Atmospheric Cloud Layer 1 - Slow */}
      <div className="absolute top-16 left-0 w-[420px] h-[160px] animate-cloud-slow opacity-30 dark:opacity-20">
        <svg viewBox="0 0 200 100" fill="currentColor" className="w-full h-full text-blue-200 dark:text-slate-600">
          <path d="M 30,70 A 25,25 0 0,1 65,50 A 35,35 0 0,1 125,45 A 25,25 0 0,1 165,65 A 20,20 0 0,1 170,80 L 30,80 Z" />
        </svg>
      </div>

      {/* Atmospheric Cloud Layer 2 - Medium */}
      <div className="absolute top-2/3 left-0 w-[550px] h-[200px] animate-cloud-medium opacity-25 dark:opacity-15">
        <svg viewBox="0 0 200 100" fill="currentColor" className="w-full h-full text-indigo-200 dark:text-cyan-900">
          <path d="M 25,75 A 20,20 0 0,1 60,55 A 38,38 0 0,1 130,48 A 28,28 0 0,1 175,70 L 25,75 Z" />
        </svg>
      </div>
    </div>
  );
}
