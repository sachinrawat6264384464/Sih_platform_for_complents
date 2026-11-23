import React from "react";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: string;
  trendDirection?: "up" | "down" | "neutral";
  accentColor?: "saffron" | "cyan" | "emerald" | "crimson" | "blue";
}

export function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  trendDirection = "neutral",
  accentColor = "saffron",
}: StatCardProps) {
  const accentClasses = {
    saffron: "from-[#F28C28]/20 to-transparent border-[#F28C28]/40 text-[#F28C28]",
    cyan: "from-cyan-500/20 to-transparent border-cyan-500/40 text-cyan-400",
    emerald: "from-emerald-500/20 to-transparent border-emerald-500/40 text-emerald-400",
    crimson: "from-red-500/20 to-transparent border-red-500/40 text-red-400",
    blue: "from-blue-500/20 to-transparent border-blue-500/40 text-blue-400",
  }[accentColor];

  const iconBgClasses = {
    saffron: "bg-[#F28C28]/15 text-[#F28C28]",
    cyan: "bg-cyan-500/15 text-cyan-400",
    emerald: "bg-emerald-500/15 text-emerald-400",
    crimson: "bg-red-500/15 text-red-400",
    blue: "bg-blue-500/15 text-blue-400",
  }[accentColor];

  return (
    <div className="relative overflow-hidden rounded-xl border border-slate-200 dark:border-slate-700/80 bg-white dark:bg-[#14233D] p-5 shadow-sm dark:shadow-lg transition-all hover:border-slate-300 dark:hover:border-slate-600 hover:shadow-md">
      <div className={`absolute top-0 right-0 h-24 w-24 bg-gradient-to-bl ${accentClasses} blur-xl pointer-events-none`} />

      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          {title}
        </span>
        <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${iconBgClasses}`}>
          <Icon className="h-5 w-5" />
        </div>
      </div>

      <div className="mt-3 flex items-baseline space-x-2">
        <span className="text-2xl font-black tracking-tight text-slate-900 dark:text-white font-mono">
          {value}
        </span>
        {trend && (
          <span
            className={`text-xs font-semibold ${
              trendDirection === "up"
                ? "text-emerald-600 dark:text-emerald-400"
                : trendDirection === "down"
                ? "text-red-600 dark:text-red-400"
                : "text-slate-500 dark:text-slate-400"
            }`}
          >
            {trend}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="mt-1.5 text-xs text-slate-500 dark:text-slate-400">{subtitle}</p>
      )}
    </div>
  );
}

