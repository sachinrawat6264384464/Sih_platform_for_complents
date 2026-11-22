"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
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
  Search,
  X,
  LogOut,
} from "lucide-react";

interface CommandItem {
  title: string;
  category: string;
  path: string;
  icon: React.ElementType;
}

const commands: CommandItem[] = [
  { title: "Dashboard & Realtime Analytics", category: "Navigation", path: "/", icon: LayoutDashboard },
  { title: "Institutions Directory & Profiles", category: "Navigation", path: "/institutions", icon: Building2 },
  { title: "Grievances & Complaints Lifecycle", category: "Navigation", path: "/complaints", icon: FileSpreadsheet },
  { title: "Overlap Sieve & Coordination Workspace", category: "Navigation", path: "/coordination", icon: GitCompare },
  { title: "Regulatory Case Actions & Assignments", category: "Navigation", path: "/cases", icon: FolderKanban },
  { title: "Integration Gateways & Sync Connectors", category: "Navigation", path: "/integrations", icon: Network },
  { title: "Model Context Protocol (MCP) Runtime", category: "Tools", path: "/mcp", icon: Cpu },
  { title: "Hybrid RAG & LangGraph AI Assistant", category: "AI Intelligence", path: "/ai-assistant", icon: Bot },
  { title: "Executive Reports & Audit Exports", category: "Reporting", path: "/reports", icon: FileBarChart },
  { title: "Security & Immutable Audit Trail", category: "Audit", path: "/audit-logs", icon: History },
];

export function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const router = useRouter();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      } else if (e.key === "Escape") {
        setIsOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const filteredCommands = commands.filter(
    (c) =>
      c.title.toLowerCase().includes(search.toLowerCase()) ||
      c.category.toLowerCase().includes(search.toLowerCase())
  );

  const handleSelect = (path: string) => {
    setIsOpen(false);
    setSearch("");
    router.push(path);
  };

  const handleLogout = () => {
    setIsOpen(false);
    localStorage.removeItem("aicte_nexus_token");
    localStorage.removeItem("aicte_nexus_user");
    router.push("/login");
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-xl overflow-hidden rounded-xl border border-slate-700 bg-[#14233D] shadow-2xl transition-all">
        {/* Search Input Bar */}
        <div className="flex items-center px-4 border-b border-slate-700/80">
          <Search className="h-5 w-5 text-slate-400 mr-3" />
          <input
            type="text"
            placeholder="Type a command or navigate... (e.g. overlap, RAG, institution)"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            autoFocus
            className="w-full bg-transparent py-4 text-sm text-slate-100 placeholder:text-slate-400 focus:outline-none"
          />
          <button
            onClick={() => setIsOpen(false)}
            className="p-1 text-slate-400 hover:text-slate-200"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Command List */}
        <div className="max-h-80 overflow-y-auto p-2">
          {filteredCommands.length === 0 ? (
            <div className="py-8 text-center text-sm text-slate-400">
              No results found matching &quot;{search}&quot;
            </div>
          ) : (
            filteredCommands.map((cmd) => {
              const Icon = cmd.icon;
              return (
                <button
                  key={cmd.path}
                  onClick={() => handleSelect(cmd.path)}
                  className="flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-left text-sm text-slate-200 transition-colors hover:bg-[#1E355B] hover:text-[#F28C28]"
                >
                  <div className="flex items-center space-x-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-md bg-[#0B1730] text-slate-300">
                      <Icon className="h-4 w-4" />
                    </div>
                    <div>
                      <div className="font-medium">{cmd.title}</div>
                      <div className="text-xs text-slate-400">{cmd.category}</div>
                    </div>
                  </div>
                  <span className="text-xs text-slate-500 font-mono">Jump</span>
                </button>
              );
            })
          )}

          {/* Logout Action */}
          <button
            onClick={handleLogout}
            className="flex w-full items-center space-x-3 rounded-lg px-3 py-2.5 mt-2 border-t border-slate-800 text-left text-sm text-red-400 transition-colors hover:bg-red-500/10"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-red-950/40 text-red-400">
              <LogOut className="h-4 w-4" />
            </div>
            <div className="font-medium">Sign Out Session</div>
          </button>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-slate-800 px-4 py-2 bg-[#0B1730]/70 text-xs text-slate-400">
          <span>Navigate with mouse or keyboard</span>
          <span className="font-mono bg-slate-800 px-1.5 py-0.5 rounded text-[10px]">ESC to close</span>
        </div>
      </div>
    </div>
  );
}

