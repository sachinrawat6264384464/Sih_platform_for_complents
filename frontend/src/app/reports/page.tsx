"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import {
  FileBarChart,
  Download,
  Calendar,
  Layers,
  Activity,
  FileSpreadsheet,
  CheckCircle2,
  RefreshCw,
} from "lucide-react";

export default function ReportsPage() {
  const [metrics, setMetrics] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchMetrics = async () => {
    setLoading(true);
    try {
      const res = await api.get("/reports/dashboard");
      setMetrics(res.data);
    } catch (err) {
      console.error("Failed to load metrics", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  const handleDownloadCSV = async (type: "complaints" | "institutions") => {
    try {
      const res = await api.get(`/reports/export/${type}`, { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `aicte_${type}_${Date.now()}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch {
      alert(`Failed to export ${type} CSV`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            <FileBarChart className="h-6 w-6 text-[#F28C28]" />
            Executive Reports & Telemetry Exports
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Authoritative database-driven analytics, monthly disposal curves, and CSV/Excel exports
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => handleDownloadCSV("institutions")}
            className="flex items-center space-x-1.5 rounded-lg border border-slate-700 bg-[#14233D] px-3.5 py-2 text-xs font-semibold text-slate-200 hover:border-slate-600 shadow-sm"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Institutions CSV</span>
          </button>
          <button
            onClick={() => handleDownloadCSV("complaints")}
            className="flex items-center space-x-1.5 rounded-lg bg-gradient-to-r from-[#F28C28] to-[#D97706] px-4 py-2 text-xs font-bold text-white shadow hover:from-[#FFA94D]"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Complaints CSV</span>
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="rounded-xl border border-slate-700/80 bg-[#14233D] p-5 shadow">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Caseload</span>
          <div className="text-3xl font-black text-white font-mono mt-2">{metrics?.total_complaints || 0}</div>
          <p className="text-xs text-slate-400 mt-1">Across all AICTE Bureaus</p>
        </div>

        <div className="rounded-xl border border-slate-700/80 bg-[#14233D] p-5 shadow">
          <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">Total Redressed</span>
          <div className="text-3xl font-black text-white font-mono mt-2">{metrics?.disposed_complaints || 0}</div>
          <p className="text-xs text-slate-400 mt-1">Disposed under statutory procedure</p>
        </div>

        <div className="rounded-xl border border-slate-700/80 bg-[#14233D] p-5 shadow">
          <span className="text-xs font-bold uppercase tracking-wider text-cyan-400">SLA Compliance</span>
          <div className="text-3xl font-black text-white font-mono mt-2">
            {metrics?.sla_compliance?.compliance_percentage ? `${metrics.sla_compliance.compliance_percentage}%` : "100%"}
          </div>
          <p className="text-xs text-slate-400 mt-1">Disposed within target turnaround</p>
        </div>

        <div className="rounded-xl border border-slate-700/80 bg-[#14233D] p-5 shadow">
          <span className="text-xs font-bold uppercase tracking-wider text-[#FFA94D]">Potential Overlaps</span>
          <div className="text-3xl font-black text-white font-mono mt-2">{metrics?.potential_overlapping_cases || 0}</div>
          <p className="text-xs text-slate-400 mt-1">Detected via 8-stage sieve</p>
        </div>
      </div>

      {/* Ageing Breakdown */}
      <div className="rounded-xl border border-slate-700/80 bg-[#14233D] p-5 shadow-lg">
        <h2 className="text-sm font-bold text-white mb-4">Grievance Ageing Distribution</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div className="rounded-lg bg-[#0B1730] p-4 border border-slate-800">
            <span className="text-slate-400 uppercase text-[10px] font-bold">Under 7 Days</span>
            <div className="text-2xl font-black text-emerald-400 font-mono mt-1">
              {metrics?.complaint_ageing?.under_7_days || 0}
            </div>
            <p className="text-[11px] text-slate-500 mt-1">Freshly registered cases</p>
          </div>

          <div className="rounded-lg bg-[#0B1730] p-4 border border-slate-800">
            <span className="text-slate-400 uppercase text-[10px] font-bold">8 to 30 Days</span>
            <div className="text-2xl font-black text-cyan-400 font-mono mt-1">
              {metrics?.complaint_ageing?.days_8_to_30 || 0}
            </div>
            <p className="text-[11px] text-slate-500 mt-1">Active investigation window</p>
          </div>

          <div className="rounded-lg bg-[#0B1730] p-4 border border-slate-800">
            <span className="text-slate-400 uppercase text-[10px] font-bold">31 to 90 Days</span>
            <div className="text-2xl font-black text-yellow-400 font-mono mt-1">
              {metrics?.complaint_ageing?.days_31_to_90 || 0}
            </div>
            <p className="text-[11px] text-slate-500 mt-1">Approaching SLA target</p>
          </div>

          <div className="rounded-lg bg-[#0B1730] p-4 border border-slate-800">
            <span className="text-slate-400 uppercase text-[10px] font-bold">Over 90 Days</span>
            <div className="text-2xl font-black text-red-400 font-mono mt-1">
              {metrics?.complaint_ageing?.over_90_days || 0}
            </div>
            <p className="text-[11px] text-slate-500 mt-1">Critical escalation tier</p>
          </div>
        </div>
      </div>
    </div>
  );
}

