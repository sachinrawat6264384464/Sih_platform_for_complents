"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Building2,
  FileSpreadsheet,
  GitCompare,
  FolderKanban,
  Network,
  Cpu,
  Bot,
  FileBarChart,
  History,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
} from "lucide-react";

const navigationItems = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Institutions", href: "/institutions", icon: Building2 },
  { name: "Complaints", href: "/complaints", icon: FileSpreadsheet },
  { name: "Coordination", href: "/coordination", icon: GitCompare, badge: "AI" },
  { name: "Regulatory Cases", href: "/cases", icon: FolderKanban },
  { name: "Integrations", href: "/integrations", icon: Network },
  { name: "MCP Servers", href: "/mcp", icon: Cpu },
  { name: "AI Assistant", href: "/ai-assistant", icon: Bot, badge: "RAG" },
  { name: "Reports", href: "/reports", icon: FileBarChart },
  { name: "Audit Trail", href: "/audit-logs", icon: History },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  if (pathname === "/login") return null;

  return (
    <aside
      className={`relative z-20 flex flex-col border-r transition-all duration-300 ease-in-out ${
        collapsed ? "w-20" : "w-64"
      } bg-white dark:bg-[#0B1730]/95 border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 shadow-sm dark:shadow-none`}
    >
      {/* Brand & Crest Header */}
      <div className="flex h-16 items-center justify-between px-4 border-b border-slate-200 dark:border-slate-800">
        {!collapsed && (
          <div className="flex items-center space-x-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-[#F28C28] via-[#EA580C] to-[#D97706] text-white shadow-lg shadow-orange-500/25 p-2">
              <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 4v16l8-10 8 10V4" />
                <circle cx="4" cy="4" r="2" fill="white" stroke="none" />
                <circle cx="20" cy="4" r="2" fill="white" stroke="none" />
                <circle cx="12" cy="10" r="2" fill="white" stroke="none" />
                <circle cx="4" cy="20" r="2" fill="white" stroke="none" />
                <circle cx="20" cy="20" r="2" fill="white" stroke="none" />
              </svg>
            </div>
            <div>
              <div className="text-sm font-bold tracking-wide text-slate-900 dark:text-white flex items-center gap-1.5">
                NEXUS
                <span className="text-[10px] bg-orange-100 text-orange-700 dark:bg-[#1E355B] dark:text-cyan-400 px-1.5 py-0.2 rounded font-mono font-medium">v1.0</span>
              </div>
              <div className="text-[10px] text-slate-500 dark:text-slate-400 font-medium tracking-tight">Coordination Platform</div>
            </div>
          </div>
        )}
        {collapsed && (
          <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-[#F28C28] via-[#EA580C] to-[#D97706] text-white shadow-md p-2">
            <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 4v16l8-10 8 10V4" />
              <circle cx="4" cy="4" r="2" fill="white" stroke="none" />
              <circle cx="20" cy="4" r="2" fill="white" stroke="none" />
              <circle cx="12" cy="10" r="2" fill="white" stroke="none" />
              <circle cx="4" cy="20" r="2" fill="white" stroke="none" />
              <circle cx="20" cy="20" r="2" fill="white" stroke="none" />
            </svg>
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="rounded-lg p-1.5 text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-[#14233D] hover:text-slate-900 dark:hover:text-white transition-colors"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
        {navigationItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`group flex items-center rounded-lg px-3 py-2.5 text-sm font-medium transition-all ${
                isActive
                  ? "bg-orange-50 text-[#D97706] border-l-4 border-[#F28C28] shadow-sm dark:bg-[#14233D] dark:text-[#F28C28] dark:shadow-inner"
                  : "text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#14233D]/60 hover:text-slate-900 dark:hover:text-white"
              }`}
              title={collapsed ? item.name : undefined}
            >
              <Icon
                className={`h-5 w-5 flex-shrink-0 transition-colors ${
                  isActive ? "text-[#F28C28]" : "text-slate-400 group-hover:text-blue-600 dark:group-hover:text-cyan-400"
                } ${collapsed ? "mx-auto" : "mr-3"}`}
              />
              {!collapsed && (
                <div className="flex flex-1 items-center justify-between">
                  <span>{item.name}</span>
                  {item.badge && (
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-orange-100 text-[#D97706] border border-orange-200 dark:bg-[#F28C28]/20 dark:text-[#FFA94D] dark:border-[#F28C28]/40">
                      {item.badge}
                    </span>
                  )}
                </div>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Security & Bureau Trust Seal */}
      {!collapsed && (
        <div className="p-4 border-t border-slate-200 dark:border-slate-800/80 bg-slate-50 dark:bg-[#0B1730] transition-colors">
          <div className="flex items-center space-x-2 text-[11px] text-slate-600 dark:text-slate-400">
            <ShieldCheck className="h-4 w-4 text-emerald-500 dark:text-emerald-400 flex-shrink-0" />
            <span>Regulation & PGRC Bureau Verified</span>
          </div>
          <div className="text-[10px] text-slate-400 dark:text-slate-500 mt-1">SIH26264 Government Redressal</div>
        </div>
      )}
    </aside>
  );
}

