"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { MCPServerInfo } from "@/lib/types";
import {
  Cpu,
  Layers,
  Terminal,
  Play,
  CheckCircle2,
  AlertCircle,
  Code2,
  RefreshCw,
  Box,
} from "lucide-react";

export default function MCPPage() {
  const [servers, setServers] = useState<MCPServerInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedServer, setSelectedServer] = useState<MCPServerInfo | null>(null);
  const [selectedTool, setSelectedTool] = useState<any | null>(null);
  const [toolArgs, setToolArgs] = useState("{}");
  const [invoking, setInvoking] = useState(false);
  const [toolResult, setToolResult] = useState<any | null>(null);

  const fetchServers = async () => {
    setLoading(true);
    try {
      const res = await api.get("/mcp/servers");
      const list = res.data || [];
      setServers(list);
      if (list.length > 0 && !selectedServer) {
        setSelectedServer(list[0]);
        if (list[0].tools?.length > 0) {
          setSelectedTool(list[0].tools[0]);
        }
      }
    } catch (err) {
      console.error("Failed to load MCP servers", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServers();
  }, []);

  const handleSelectServer = (srv: MCPServerInfo) => {
    setSelectedServer(srv);
    if (srv.tools?.length > 0) {
      setSelectedTool(srv.tools[0]);
    } else {
      setSelectedTool(null);
    }
    setToolResult(null);
  };

  const handleSelectTool = (tool: any) => {
    setSelectedTool(tool);
    // prefill default args template
    const template: Record<string, any> = {};
    const props = tool.parameters?.properties || {};
    Object.keys(props).forEach((k) => {
      template[k] = props[k].default || (props[k].type === "string" ? "" : 10);
    });
    setToolArgs(JSON.stringify(template, null, 2));
    setToolResult(null);
  };

  const handleInvoke = async () => {
    if (!selectedServer || !selectedTool) return;
    setInvoking(true);
    setToolResult(null);
    try {
      let parsedArgs = {};
      try {
        parsedArgs = JSON.parse(toolArgs);
      } catch {
        alert("Invalid JSON parameters");
        setInvoking(false);
        return;
      }

      const res = await api.post(`/mcp/servers/${selectedServer.server_id}/call`, {
        tool_name: selectedTool.name,
        arguments: parsedArgs,
      });
      setToolResult(res.data);
    } catch (err: any) {
      setToolResult({
        error: err.response?.data?.detail || "MCP invocation returned error",
      });
    } finally {
      setInvoking(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            <Cpu className="h-6 w-6 text-[#F28C28]" />
            Model Context Protocol (MCP) Runtime Console
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Official Python SDK 2.x MCP server endpoints exposing standardized tools for AI agents and bureaus
          </p>
        </div>

        <button
          onClick={fetchServers}
          className="flex items-center space-x-1.5 rounded-lg border border-slate-700 bg-[#14233D] px-3.5 py-2 text-xs font-semibold text-slate-200 hover:border-slate-600 shadow-sm"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh MCP Servers</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Server Directory */}
        <div className="rounded-xl border border-slate-700/80 bg-[#14233D] p-4 shadow-lg space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-700/80">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Registered MCP Servers ({servers.length})
            </span>
          </div>

          <div className="space-y-2">
            {servers.map((srv) => {
              const isSelected = selectedServer?.server_id === srv.server_id;
              return (
                <button
                  key={srv.server_id}
                  onClick={() => handleSelectServer(srv)}
                  className={`flex w-full flex-col rounded-lg p-3 text-left transition-all border ${
                    isSelected
                      ? "bg-[#0B1730] border-[#F28C28] shadow-md shadow-orange-500/10"
                      : "bg-[#14233D] border-slate-700/60 hover:border-slate-600"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-white flex items-center gap-1.5">
                      <Box className={`h-3.5 w-3.5 ${isSelected ? "text-[#F28C28]" : "text-slate-400"}`} />
                      {srv.name}
                    </span>
                    <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                      ONLINE
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-1">{srv.description}</p>
                  <div className="mt-2 flex items-center justify-between text-[10px] text-slate-500 font-mono">
                    <span>Tools: {srv.tools?.length || 0}</span>
                    <span>v{srv.version}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right 2 Columns: Tool Inspector & Live Runner */}
        <div className="lg:col-span-2 space-y-5">
          {selectedServer && (
            <div className="rounded-xl border border-slate-700/80 bg-[#14233D] p-5 shadow-lg space-y-4">
              <div className="flex items-center justify-between border-b border-slate-700/80 pb-3">
                <div>
                  <h2 className="text-sm font-bold text-white flex items-center gap-2">
                    <Terminal className="h-4 w-4 text-[#F28C28]" />
                    Server: {selectedServer.name}
                  </h2>
                  <p className="text-xs text-slate-400 mt-0.5">{selectedServer.description}</p>
                </div>
              </div>

              {/* Tools Selector Tabs */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Available MCP Tools:
                </label>
                <div className="flex flex-wrap gap-2">
                  {selectedServer.tools?.map((tool) => {
                    const isToolActive = selectedTool?.name === tool.name;
                    return (
                      <button
                        key={tool.name}
                        onClick={() => handleSelectTool(tool)}
                        className={`rounded-lg px-3 py-1.5 text-xs font-mono font-bold transition-all border ${
                          isToolActive
                            ? "bg-[#F28C28] text-white border-[#F28C28] shadow"
                            : "bg-[#0B1730] text-slate-300 border-slate-700 hover:border-slate-500"
                        }`}
                      >
                        {tool.name}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Selected Tool Details */}
              {selectedTool && (
                <div className="space-y-3 border-t border-slate-700/80 pt-4">
                  <div className="rounded-lg bg-[#0B1730] p-3 border border-slate-800">
                    <div className="text-xs font-bold text-cyan-400 font-mono">{selectedTool.name}</div>
                    <p className="text-xs text-slate-300 mt-1">{selectedTool.description}</p>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      JSON Input Arguments:
                    </label>
                    <textarea
                      rows={5}
                      value={toolArgs}
                      onChange={(e) => setToolArgs(e.target.value)}
                      className="w-full rounded-lg border border-slate-700 bg-[#0B1730] p-3 text-xs text-white font-mono focus:border-[#F28C28] focus:outline-none"
                    />
                  </div>

                  <div className="flex justify-end">
                    <button
                      onClick={handleInvoke}
                      disabled={invoking}
                      className="flex items-center space-x-1.5 rounded-lg bg-gradient-to-r from-[#F28C28] to-[#D97706] px-5 py-2 text-xs font-bold text-white shadow hover:from-[#FFA94D] disabled:opacity-50"
                    >
                      <Play className="h-3.5 w-3.5 fill-current" />
                      <span>{invoking ? "Invoking MCP Protocol..." : "Execute MCP Tool Call"}</span>
                    </button>
                  </div>

                  {/* Execution Response */}
                  {toolResult && (
                    <div className="space-y-2 border-t border-slate-700/80 pt-3">
                      <div className="flex items-center justify-between text-xs font-bold">
                        <span className="text-emerald-400 flex items-center gap-1.5">
                          <CheckCircle2 className="h-4 w-4" />
                          MCP Protocol Response
                        </span>
                        {toolResult.latency_ms && (
                          <span className="font-mono text-slate-400 text-[11px]">
                            {toolResult.latency_ms}ms
                          </span>
                        )}
                      </div>
                      <pre className="max-h-64 overflow-y-auto rounded-lg bg-[#0B1730] p-3 text-[11px] text-slate-200 font-mono border border-slate-800">
                        {JSON.stringify(toolResult, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
