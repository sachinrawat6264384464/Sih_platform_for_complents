"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import {
  Network,
  Activity,
  RefreshCw,
  Upload,
  CheckCircle2,
  AlertCircle,
  FileSpreadsheet,
  Cpu,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";

interface Connector {
  id: string;
  name: string;
  system_type: string;
  is_active: boolean;
  last_sync_time?: string;
  records_synced_total: number;
}

export default function IntegrationsPage() {
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [loading, setLoading] = useState(true);
  const [testingId, setTestingId] = useState<string | null>(null);
  const [syncingId, setSyncingId] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<any | null>(null);

  // CSV Dossier upload
  const [csvContent, setCsvContent] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any | null>(null);

  const fetchConnectors = async () => {
    setLoading(true);
    try {
      const res = await api.get("/integrations/connectors");
      setConnectors(res.data || []);
    } catch (err) {
      console.error("Failed to load connectors", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConnectors();
  }, []);

  const handleTestConnectivity = async (systemType: string) => {
    setTestingId(systemType);
    setTestResult(null);
    try {
      const res = await api.post(`/integrations/connectors/${systemType}/test`);
      setTestResult(res.data);
    } catch (err: any) {
      setTestResult({
        status: "FAILED",
        error: err.response?.data?.detail || "Connection check timed out",
      });
    } finally {
      setTestingId(null);
    }
  };

  const handleTriggerSync = async (systemType: string) => {
    setSyncingId(systemType);
    try {
      const res = await api.post(`/integrations/connectors/${systemType}/sync`);
      alert(`Sync triggered successfully. Run ID: ${res.data.sync_run_id}. Processed: ${res.data.records_processed}, Inserted: ${res.data.records_inserted}.`);
      fetchConnectors();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Sync failed");
    } finally {
      setSyncingId(null);
    }
  };

  const handleUploadDossier = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!csvContent.trim()) return;
    setUploading(true);
    setUploadResult(null);
    try {
      const res = await api.post("/integrations/connectors/csv-sftp/upload-dossier", {
        raw_csv: csvContent,
      });
      setUploadResult(res.data);
      setCsvContent("");
      fetchConnectors();
    } catch (err: any) {
      setUploadResult({
        status: "FAILED",
        error: err.response?.data?.detail || "Upload rejected by schema validator",
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            <Network className="h-6 w-6 text-[#F28C28]" />
            External Integration Gateways & Connectors
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Standardized interfaces connecting PGRC, Regulation Bureau, Regional Offices, and CSV/SFTP portals
          </p>
        </div>

        <button
          onClick={fetchConnectors}
          className="flex items-center space-x-1.5 rounded-lg border border-slate-700 bg-[#14233D] px-3.5 py-2 text-xs font-semibold text-slate-200 hover:border-slate-600 shadow-sm"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh Connectors</span>
        </button>
      </div>

      {/* Connectivity Test Alert */}
      {testResult && (
        <div
          className={`rounded-xl border p-4 text-xs flex items-start justify-between ${
            testResult.status === "HEALTHY" || testResult.status === "OK"
              ? "border-emerald-500/40 bg-emerald-950/40 text-emerald-300"
              : "border-red-500/40 bg-red-950/40 text-red-300"
          }`}
        >
          <div className="flex items-start space-x-2">
            {testResult.status === "HEALTHY" || testResult.status === "OK" ? (
              <CheckCircle2 className="h-4 w-4 text-emerald-400 mt-0.5" />
            ) : (
              <AlertCircle className="h-4 w-4 text-red-400 mt-0.5" />
            )}
            <div>
              <div className="font-bold">
                Connector Health Probe: {testResult.connector || "Gateway"} — {testResult.status}
              </div>
              <p className="mt-0.5 text-slate-300">{testResult.message || testResult.error}</p>
              {testResult.latency_ms && (
                <div className="mt-1 font-mono text-[11px] text-slate-400">
                  Round-trip latency: {testResult.latency_ms}ms
                </div>
              )}
            </div>
          </div>
          <button onClick={() => setTestResult(null)} className="text-slate-400 hover:text-white">
            Dismiss
          </button>
        </div>
      )}

      {/* Connector Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {connectors.map((conn) => (
          <div
            key={conn.id}
            className="rounded-xl border border-slate-700/80 bg-[#14233D] p-5 shadow-lg flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                  {conn.is_active ? "OPERATIONAL" : "INACTIVE"}
                </span>
                <span className="text-[10px] text-slate-400 font-mono">
                  {conn.system_type}
                </span>
              </div>

              <h2 className="text-base font-bold text-white mt-3">{conn.name}</h2>
              <p className="text-xs text-slate-400 mt-1">
                Automated bidirectional synchronization for authorized complaint dossiers
              </p>

              <div className="mt-4 space-y-1.5 border-t border-slate-700/80 pt-3 text-xs">
                <div className="flex justify-between text-slate-400">
                  <span>Last Synchronized:</span>
                  <span className="font-mono text-slate-200">
                    {conn.last_sync_time ? new Date(conn.last_sync_time).toLocaleString() : "Never"}
                  </span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Dossiers Synced:</span>
                  <span className="font-mono font-bold text-white">{conn.records_synced_total}</span>
                </div>
              </div>
            </div>

            <div className="mt-5 grid grid-cols-2 gap-2 pt-3 border-t border-slate-700/80">
              <button
                onClick={() => handleTestConnectivity(conn.system_type)}
                disabled={testingId === conn.system_type}
                className="rounded-lg bg-[#0B1730] px-3 py-1.5 text-xs font-semibold text-cyan-400 hover:border-cyan-500 border border-slate-700 transition-colors"
              >
                {testingId === conn.system_type ? "Probing..." : "Ping Health"}
              </button>
              <button
                onClick={() => handleTriggerSync(conn.system_type)}
                disabled={syncingId === conn.system_type}
                className="rounded-lg bg-gradient-to-r from-[#F28C28] to-[#D97706] px-3 py-1.5 text-xs font-bold text-white shadow hover:from-[#FFA94D] transition-all"
              >
                {syncingId === conn.system_type ? "Syncing..." : "Sync Now"}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Manual CSV Dossier Batch Ingestion */}
      <div className="rounded-xl border border-slate-700/80 bg-[#14233D] p-6 shadow-lg">
        <div className="flex items-center space-x-2 text-[#F28C28] font-bold text-sm mb-1">
          <Upload className="h-5 w-5" />
          <h2>Institutional Complaint CSV / SFTP Batch Ingestion Gateway</h2>
        </div>
        <p className="text-xs text-slate-400 mb-4">
          For offline or air-gapped Regional Desks without direct API access. Paste CSV dossier lines with headers:
          <span className="font-mono text-cyan-300 ml-1">
            complaint_number, aicte_permanent_id, institution_name, category, title, description, priority
          </span>
        </p>

        {uploadResult && (
          <div
            className={`rounded-lg p-3 text-xs mb-4 border ${
              uploadResult.status === "SUCCESS"
                ? "border-emerald-500/40 bg-emerald-950/40 text-emerald-300"
                : "border-red-500/40 bg-red-950/40 text-red-300"
            }`}
          >
            <div className="font-bold">Ingestion Status: {uploadResult.status}</div>
            <p className="mt-0.5">{uploadResult.message || uploadResult.error}</p>
            {uploadResult.records_ingested !== undefined && (
              <div className="mt-1 font-mono text-[11px]">
                Valid Records Ingested: {uploadResult.records_ingested}
              </div>
            )}
          </div>
        )}

        <form onSubmit={handleUploadDossier} className="space-y-4">
          <textarea
            rows={5}
            required
            placeholder={`complaint_number,aicte_permanent_id,institution_name,category,title,description,priority\nPGRC-2026-9901,1-43289012,Delhi Institute of Technology,Fee Issues,Unreasonable laboratory fee demand,Students forced to deposit INR 15000 before exams,High`}
            value={csvContent}
            onChange={(e) => setCsvContent(e.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-[#0B1730] p-3 text-xs text-white font-mono placeholder:text-slate-600 focus:border-[#F28C28] focus:outline-none"
          />

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={uploading}
              className="flex items-center space-x-2 rounded-lg bg-gradient-to-r from-[#F28C28] to-[#D97706] px-5 py-2.5 text-xs font-bold text-white shadow hover:from-[#FFA94D] disabled:opacity-50"
            >
              <Upload className="h-4 w-4" />
              <span>{uploading ? "Ingesting Dossier..." : "Ingest & Run Overlap Sieve"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
