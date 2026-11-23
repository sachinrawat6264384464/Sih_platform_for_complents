"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { DashboardMetrics } from "@/lib/types";
import { StatCard } from "@/components/ui/StatCard";
import {
  Building2,
  FileSpreadsheet,
  AlertTriangle,
  CheckCircle2,
  GitCompare,
  Clock,
  ShieldCheck,
  RefreshCw,
  Plus,
  ArrowUpRight,
  TrendingUp,
  Activity,
  Layers,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

const COLORS = ["#F28C28", "#1686CB", "#00E5FF", "#10B981", "#8B5CF6", "#EC4899"];

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get("/reports/dashboard");
      setMetrics(res.data);
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      const isConnError = !err.response || err.message === "Network Error" || err.code === "ERR_NETWORK";
      setError(
        detail ||
          (isConnError
            ? "Backend API is not running on http://localhost:8000. Please start it using 'start-backend.bat'."
            : "Failed to load dashboard metrics")
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="h-2.5 w-2.5 rounded-full bg-[#F28C28] animate-pulse"></span>
            <span className="text-xs font-bold uppercase tracking-wider text-[#F28C28]">
              Consolidated Monitoring & Redressal Desk
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-black tracking-tight text-slate-900 dark:text-white mt-1">
            Institutional Complaint Intelligence Overview
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Real-time multi-bureau telemetry, 8-stage duplicate detection & SLA compliance
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-3">
          <button
            onClick={fetchMetrics}
            className="flex items-center space-x-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-[#14233D] px-3.5 py-2 text-xs font-semibold text-slate-700 dark:text-slate-200 hover:border-slate-400 dark:hover:border-slate-600 transition-colors shadow-sm"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
            <span>Refresh Telemetry</span>
          </button>
          <Link
            href="/complaints"
            className="flex items-center space-x-1.5 rounded-lg bg-gradient-to-r from-[#F28C28] to-[#D97706] px-4 py-2 text-xs font-bold text-white shadow-md shadow-orange-500/20 hover:from-[#FFA94D] transition-all"
          >
            <Plus className="h-4 w-4" />
            <span>Register Complaint</span>
          </Link>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="rounded-xl border border-red-500/40 bg-red-950/30 p-4 text-sm text-red-300 flex items-center justify-between">
          <span>{error}</span>
          <button onClick={fetchMetrics} className="underline text-xs ml-4">
            Retry
          </button>
        </div>
      )}

      {/* Key Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Monitored Institutions"
          value={metrics ? metrics.total_institutions : "--"}
          subtitle="AICTE Approved & Technical Entities"
          icon={Building2}
          accentColor="blue"
        />
        <StatCard
          title="Consolidated Complaints"
          value={metrics ? metrics.total_complaints : "--"}
          subtitle="Across PGRC, RB & Regional Desks"
          icon={FileSpreadsheet}
          accentColor="saffron"
        />
        <StatCard
          title="Under Process / Active"
          value={metrics ? metrics.under_process_complaints : "--"}
          subtitle="Assigned to Bureau Officers"
          icon={Clock}
          accentColor="cyan"
        />
        <StatCard
          title="Disposed & Redressed"
          value={metrics ? metrics.disposed_complaints : "--"}
          subtitle="Verified Final Disposition"
          icon={CheckCircle2}
          accentColor="emerald"
        />
      </div>

      {/* Overlap & Regulatory Attention Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="rounded-xl border border-orange-200 dark:border-[#F28C28]/40 bg-white dark:bg-[#14233D] p-5 shadow-sm dark:shadow-lg relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-orange-600 dark:text-[#FFA94D]">
              Potential Overlaps Detected
            </span>
            <GitCompare className="h-5 w-5 text-[#F28C28]" />
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-black text-slate-900 dark:text-white font-mono">
              {metrics ? metrics.potential_overlapping_cases : "--"}
            </span>
            <Link
              href="/coordination"
              className="text-xs font-semibold text-orange-600 dark:text-[#FFA94D] hover:underline flex items-center"
            >
              Examine Sieve <ArrowUpRight className="h-3 w-3 ml-1" />
            </Link>
          </div>
          <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
            Detected via AI 8-stage sieve across institutions & bureaus
          </p>
        </div>

        <div className="rounded-xl border border-red-200 dark:border-red-500/40 bg-white dark:bg-[#14233D] p-5 shadow-sm dark:shadow-lg relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-red-600 dark:text-red-400">
              SLA Overdue Escalations
            </span>
            <AlertTriangle className="h-5 w-5 text-red-500 dark:text-red-400" />
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-black text-slate-900 dark:text-white font-mono">
              {metrics ? metrics.overdue_complaints : "--"}
            </span>
            <Link
              href="/complaints?filter=overdue"
              className="text-xs font-semibold text-red-600 dark:text-red-400 hover:underline flex items-center"
            >
              Review Overdue <ArrowUpRight className="h-3 w-3 ml-1" />
            </Link>
          </div>
          <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
            Past statutory citizen redressal deadline
          </p>
        </div>

        <div className="rounded-xl border border-emerald-200 dark:border-emerald-500/40 bg-white dark:bg-[#14233D] p-5 shadow-sm dark:shadow-lg relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
              Confirmed Linked Cases
            </span>
            <ShieldCheck className="h-5 w-5 text-emerald-500 dark:text-emerald-400" />
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-black text-slate-900 dark:text-white font-mono">
              {metrics ? metrics.confirmed_linked_cases : "--"}
            </span>
            <Link
              href="/coordination"
              className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:underline flex items-center"
            >
              Coordination Desk <ArrowUpRight className="h-3 w-3 ml-1" />
            </Link>
          </div>
          <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
            Officially verified multi-bureau investigation clusters
          </p>
        </div>
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bureau-wise Workload */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-700/80 bg-white dark:bg-[#14233D] p-5 shadow-sm dark:shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-slate-900 dark:text-white tracking-wide">
                Bureau-Wise Grievance Distribution
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                PGRC, Regulation Bureau & Approvals active caseload
              </p>
            </div>
            <Layers className="h-4 w-4 text-slate-400" />
          </div>
          <div className="h-64 w-full">
            {metrics?.bureau_workload && metrics.bureau_workload.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metrics.bureau_workload}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#94A3B8" opacity={0.2} />
                  <XAxis dataKey="bureau_name" stroke="#64748B" fontSize={11} />
                  <YAxis stroke="#64748B" fontSize={11} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0B1730",
                      borderColor: "#1E355B",
                      borderRadius: "8px",
                      color: "#FFFFFF",
                      fontSize: "12px",
                    }}
                  />
                  <Bar dataKey="total_complaints" fill="#F28C28" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-xs text-slate-400">
                No bureau workload records available yet
              </div>
            )}
          </div>
        </div>

        {/* Regional Office Workload */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-700/80 bg-white dark:bg-[#14233D] p-5 shadow-sm dark:shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-slate-900 dark:text-white tracking-wide">
                Regional Jurisdictional Spread
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                CRO, NRO, WRO, SRO, SWRO, ERO & NWRO volumes
              </p>
            </div>
            <Activity className="h-4 w-4 text-slate-400" />
          </div>
          <div className="h-64 w-full">
            {(metrics?.regional_workload || metrics?.region_workload) && ((metrics?.regional_workload || metrics?.region_workload)!.length > 0) ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metrics?.regional_workload || metrics?.region_workload}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#94A3B8" opacity={0.2} />
                  <XAxis dataKey="region_name" stroke="#64748B" fontSize={11} />
                  <YAxis stroke="#64748B" fontSize={11} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0B1730",
                      borderColor: "#1E355B",
                      borderRadius: "8px",
                      color: "#FFFFFF",
                      fontSize: "12px",
                    }}
                  />
                  <Bar dataKey="total_complaints" fill="#1686CB" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-xs text-slate-400">
                No regional distribution records available yet
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Integration Gateway Status Table */}
      <div className="rounded-xl border border-slate-200 dark:border-slate-700/80 bg-white dark:bg-[#14233D] p-5 shadow-sm dark:shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-bold text-slate-900 dark:text-white tracking-wide">
              External Integration Connectors & Sync Status
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              PGRC REST Gateway, Regulation Bureau Connector & SFTP Dossier Sync
            </p>
          </div>
          <Link
            href="/integrations"
            className="text-xs font-semibold text-blue-600 dark:text-cyan-400 hover:underline flex items-center"
          >
            Manage Connectors <ArrowUpRight className="h-3 w-3 ml-1" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700 dark:text-slate-300">
            <thead className="bg-slate-50 dark:bg-[#0B1730] uppercase text-[10px] tracking-wider text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th className="px-4 py-3">Connector Name</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Last Sync</th>
                <th className="px-4 py-3 text-right">Synced Records</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
              {metrics?.integration_health && metrics.integration_health.length > 0 ? (
                metrics.integration_health.map((conn) => (
                  <tr key={conn.connector_name} className="hover:bg-slate-50 dark:hover:bg-[#1E355B]/40 transition-colors">
                    <td className="px-4 py-3 font-semibold text-slate-900 dark:text-white">
                      {conn.connector_name}
                    </td>
                    <td className="px-4 py-3 text-slate-500 dark:text-slate-400">REST API / Webhook</td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300 dark:bg-emerald-950 dark:text-emerald-400 dark:border-emerald-800">
                        {conn.is_active ? "Operational" : "Offline"}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-500 dark:text-slate-400 font-mono">
                      {conn.last_sync_time ? new Date(conn.last_sync_time).toLocaleString() : "Never"}
                    </td>
                    <td className="px-4 py-3 text-right font-mono font-bold text-slate-900 dark:text-white">
                      {conn.records_synced_total}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-4 py-4 text-center text-slate-400">
                    No connectors configured
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

