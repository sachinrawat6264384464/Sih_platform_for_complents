"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import {
  History,
  ShieldAlert,
  Search,
  Filter,
  RefreshCw,
  Clock,
  User as UserIcon,
} from "lucide-react";

interface AuditLogEntry {
  id: string;
  action: string;
  entity_type: string;
  entity_id?: string;
  user_id?: string;
  username?: string;
  ip_address?: string;
  details?: Record<string, any>;
  created_at: string;
}

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState("");

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params: any = { limit: 100 };
      if (actionFilter) params.action = actionFilter;
      const res = await api.get("/audit/logs", { params });
      setLogs(res.data.items || res.data || []);
    } catch (err) {
      console.error("Failed to load audit logs", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [actionFilter]);

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            <History className="h-6 w-6 text-[#F28C28]" />
            Security & Immutable Audit Trail
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Chronological cryptographic record of all administrative, review, and status actions under IT compliance
          </p>
        </div>

        <button
          onClick={fetchLogs}
          className="flex items-center space-x-1.5 rounded-lg border border-slate-700 bg-[#14233D] px-3.5 py-2 text-xs font-semibold text-slate-200 hover:border-slate-600 shadow-sm"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh Trail</span>
        </button>
      </div>

      {/* Filter */}
      <div className="rounded-xl border border-slate-700/80 bg-[#14233D] p-4 shadow-lg flex items-center space-x-3">
        <Filter className="h-4 w-4 text-slate-400" />
        <select
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value)}
          className="rounded-lg border border-slate-700 bg-[#0B1730] py-2 px-3 text-xs text-slate-300 focus:border-[#F28C28] focus:outline-none"
        >
          <option value="">All Action Types</option>
          <option value="USER_LOGIN">USER_LOGIN</option>
          <option value="CREATE_INSTITUTION">CREATE_INSTITUTION</option>
          <option value="CREATE_COMPLAINT">CREATE_COMPLAINT</option>
          <option value="STATUS_TRANSITION">STATUS_TRANSITION</option>
          <option value="OVERLAP_SCAN">OVERLAP_SCAN</option>
          <option value="CONFIRM_LINK">CONFIRM_LINK</option>
          <option value="MCP_CALL">MCP_CALL</option>
        </select>
      </div>

      {/* Audit Log Table */}
      <div className="rounded-xl border border-slate-700/80 bg-[#14233D] shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-[#0B1730] uppercase text-[10px] tracking-wider text-slate-400 border-b border-slate-700">
              <tr>
                <th className="px-4 py-3">Timestamp (UTC)</th>
                <th className="px-4 py-3">Action Type</th>
                <th className="px-4 py-3">Entity</th>
                <th className="px-4 py-3">Officer / Actor</th>
                <th className="px-4 py-3">IP Address</th>
                <th className="px-4 py-3">Metadata & Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono text-[11px]">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-slate-500 font-sans">
                    Loading security log entries...
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-slate-500 font-sans">
                    No audit records matching query
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-[#1E355B]/40 transition-colors">
                    <td className="px-4 py-3 text-slate-400">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-[#1E355B] text-cyan-300 border border-cyan-800">
                        {log.action}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-300">
                      {log.entity_type} {log.entity_id ? `(${log.entity_id.slice(0, 8)})` : ""}
                    </td>
                    <td className="px-4 py-3 text-white font-sans font-medium">
                      {log.username || "System Worker"}
                    </td>
                    <td className="px-4 py-3 text-slate-400">
                      {log.ip_address || "127.0.0.1"}
                    </td>
                    <td className="px-4 py-3 text-slate-400 truncate max-w-xs">
                      {log.details ? JSON.stringify(log.details) : "-"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
