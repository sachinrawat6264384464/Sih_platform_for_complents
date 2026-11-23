"use client";

import React, { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useTheme } from "@/lib/theme";
import {
  Sun,
  Moon,
  Search,
  Bell,
  User as UserIcon,
  LogOut,
  ShieldAlert,
  Activity,
  Layers,
} from "lucide-react";

export function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const { theme, toggleTheme } = useTheme();
  const [userName, setUserName] = useState("AICTE Official");
  const [userRole, setUserRole] = useState("Super Administrator");
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("aicte_nexus_user");
      if (stored) {
        try {
          const u = JSON.parse(stored);
          setUserName(u.full_name || u.username);
          setUserRole(u.is_superuser ? "Super Administrator" : "Bureau Officer");
        } catch {
          // ignore
        }
      }
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("aicte_nexus_token");
    localStorage.removeItem("aicte_nexus_user");
    router.push("/login");
  };

  if (pathname === "/login") return null;

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-[#0B1730]/90 px-6 backdrop-blur-md transition-colors duration-200">
      {/* Bureau Hierarchy and National Council Tag */}
      <div className="flex items-center space-x-4">
        <div>
          <h1 className="text-sm font-bold tracking-wide text-slate-900 dark:text-white flex items-center gap-2">
            NEXUS
            <span className="hidden sm:inline-block text-xs font-normal text-slate-500 dark:text-slate-400 border-l border-slate-300 dark:border-slate-700 pl-2">
              National Coordination & Overlap Sieve Platform
            </span>
          </h1>
        </div>
      </div>

      {/* Center Command Palette Trigger Button */}
      <div className="hidden md:flex flex-1 max-w-md mx-6">
        <button
          onClick={() => {
            const event = new KeyboardEvent("keydown", {
              key: "k",
              ctrlKey: true,
              bubbles: true,
            });
            window.dispatchEvent(event);
          }}
          className="flex w-full items-center justify-between rounded-lg border border-slate-300 dark:border-slate-700/80 bg-slate-100 dark:bg-[#14233D] px-3.5 py-1.5 text-xs text-slate-600 dark:text-slate-400 hover:border-slate-400 dark:hover:border-slate-600 hover:text-slate-900 dark:hover:text-slate-200 transition-colors shadow-inner"
        >
          <div className="flex items-center space-x-2">
            <Search className="h-3.5 w-3.5 text-slate-500 dark:text-slate-400" />
            <span>Search complaints, institutions, RAG dossier...</span>
          </div>
          <kbd className="font-mono text-[10px] bg-slate-200 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 px-1.5 py-0.5 rounded text-slate-700 dark:text-slate-300">
            Ctrl+K
          </kbd>
        </button>
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-3">
        {/* Live System Status Pill */}
        <div className="hidden sm:flex items-center space-x-1.5 rounded-full bg-emerald-100 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-600/30 px-2.5 py-1 text-[11px] font-medium text-emerald-800 dark:text-emerald-400">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span>Online (Local Node)</span>
        </div>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-[#14233D] hover:text-[#F28C28] transition-colors"
          title={`Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`}
          aria-label="Toggle theme"
        >
          {theme === "dark" ? <Sun className="h-4 w-4 text-amber-400" /> : <Moon className="h-4 w-4 text-slate-700" />}
        </button>

        {/* User Profile */}
        <div className="relative">
          <button
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            className="flex items-center space-x-2 rounded-lg bg-slate-100 dark:bg-[#14233D] px-3 py-1.5 border border-slate-200 dark:border-slate-700/80 hover:border-slate-300 dark:hover:border-slate-600 text-left transition-colors"
          >
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-tr from-[#1686CB] to-cyan-400 text-white font-bold text-xs">
              {userName.charAt(0).toUpperCase()}
            </div>
            <div className="hidden md:block">
              <div className="text-xs font-semibold text-slate-800 dark:text-slate-200">{userName}</div>
              <div className="text-[10px] text-[#F28C28] font-medium">{userRole}</div>
            </div>
          </button>

          {/* Profile Dropdown */}
          {showProfileMenu && (
            <div className="absolute right-0 mt-2 w-48 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#14233D] py-1 shadow-2xl z-50">
              <div className="px-4 py-2 border-b border-slate-200 dark:border-slate-700/70">
                <div className="text-xs font-bold text-slate-900 dark:text-slate-100">{userName}</div>
                <div className="text-[11px] text-slate-500 dark:text-slate-400 truncate">{userRole}</div>
              </div>
              <button
                onClick={handleLogout}
                className="flex w-full items-center px-4 py-2 text-xs text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
              >
                <LogOut className="h-3.5 w-3.5 mr-2" />
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

