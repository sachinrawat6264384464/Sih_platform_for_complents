"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import {
  FolderKanban,
  UserCheck,
  Send,
  CheckCircle2,
  AlertCircle,
  FileText,
  Clock,
  Shield,
  RefreshCw,
  Search,
} from "lucide-react";

export default function CasesPage() {
  const [complaints, setComplaints] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCase, setSelectedCase] = useState<any | null>(null);
  const [transferModal, setTransferModal] = useState(false);
  const [targetBureauId, setTargetBureauId] = useState("");
  const [transferReason, setTransferReason] = useState("");
  const [bureaus, setBureaus] = useState<any[]>([]);

  const fetchCases = async () => {
    setLoading(true);
    try {
      const [cRes, bRes] = await Promise.all([
        api.get("/complaints?limit=100"),
        api.get("/bureaus"),
      ]);
      setComplaints(cRes.data.items || cRes.data || []);
      setBureaus(bRes.data || []);
      if (bRes.data?.length > 0) setTargetBureauId(bRes.data[0].id);
    } catch (err) {
      console.error("Failed to load cases", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, []);

  const handleInitiateTransfer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCase) return;
    try {
      await api.post(`/cases/${selectedCase.id}/transfers`, {
        target_bureau_id: targetBureauId,
        reason: transferReason,
      });
      alert("Bureau transfer request initiated for review.");
      setTransferModal(false);
      setTransferReason("");
      fetchCases();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Transfer request failed");
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            <FolderKanban className="h-6 w-6 text-[#F28C28]" />
            Regulatory Case Management & Transfer Desk
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Officer assignments, cross-bureau jurisdictional transfers, and statutory progress tracking
          </p>
        </div>

        <button
          onClick={fetchCases}
          className="flex items-center space-x-1.5 rounded-lg border border-slate-700 bg-[#14233D] px-3.5 py-2 text-xs font-semibold text-slate-200 hover:border-slate-600 shadow-sm"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh Cases</span>
        </button>
      </div>

      {/* Cases Table */}
      <div className="rounded-xl border border-slate-700/80 bg-[#14233D] shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-[#0B1730] uppercase text-[10px] tracking-wider text-slate-400 border-b border-slate-700">
              <tr>
                <th className="px-4 py-3">Case ID</th>
                <th className="px-4 py-3">Title & Institution</th>
                <th className="px-4 py-3">Assigned Bureau</th>
                <th className="px-4 py-3">Current Status</th>
                <th className="px-4 py-3">Responsible Officer</th>
                <th className="px-4 py-3 text-right">Regulatory Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                    Loading regulatory caseload...
                  </td>
                </tr>
              ) : complaints.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                    No active cases in registry
                  </td>
                </tr>
              ) : (
                complaints.map((c) => (
                  <tr key={c.id} className="hover:bg-[#1E355B]/40 transition-colors">
                    <td className="px-4 py-3 font-mono font-bold text-white">
                      {c.complaint_number}
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-semibold text-white">{c.title}</div>
                      <div className="text-[11px] text-slate-400">
                        {c.institution_name || "Permanent ID: " + c.aicte_permanent_id}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="font-medium text-slate-200">{c.bureau_name || "PGRC"}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#1E355B] text-cyan-300 border border-cyan-800">
                        {c.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center space-x-1.5 text-slate-300">
                        <UserCheck className="h-3.5 w-3.5 text-emerald-400" />
                        <span>{c.assigned_officer_name || "Assigned Desk Officer"}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => {
                          setSelectedCase(c);
                          setTransferModal(true);
                        }}
                        className="inline-flex items-center rounded bg-[#0B1730] px-2.5 py-1 text-xs text-[#F28C28] hover:border-[#F28C28] border border-slate-700"
                      >
                        <Send className="h-3 w-3 mr-1" />
                        <span>Request Transfer</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Transfer Request Modal */}
      {transferModal && selectedCase && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-md overflow-hidden rounded-xl border border-slate-700 bg-[#14233D] shadow-2xl">
            <div className="border-b border-slate-700/80 px-6 py-4 bg-[#0B1730] flex justify-between items-center">
              <h2 className="text-sm font-bold text-white">
                Initiate Bureau Jurisdictional Transfer
              </h2>
              <button onClick={() => setTransferModal(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <form onSubmit={handleInitiateTransfer} className="p-6 space-y-4 text-xs">
              <div>
                Case: <strong className="text-white">{selectedCase.complaint_number}</strong>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Target AICTE Bureau *
                </label>
                <select
                  required
                  value={targetBureauId}
                  onChange={(e) => setTargetBureauId(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2 px-3 text-xs text-white focus:border-[#F28C28] focus:outline-none"
                >
                  {bureaus.map((b) => (
                    <option key={b.id} value={b.id}>{b.name} ({b.code})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Transfer Justification & Legal Basis *
                </label>
                <textarea
                  required
                  rows={3}
                  value={transferReason}
                  onChange={(e) => setTransferReason(e.target.value)}
                  placeholder="Specify jurisdiction rationale (e.g. relates to approval withdrawal requiring Regulation Bureau inspection)..."
                  className="w-full rounded-lg border border-slate-700 bg-[#0B1730] p-2.5 text-xs text-white focus:border-[#F28C28] focus:outline-none"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-3 border-t border-slate-700/80">
                <button
                  type="button"
                  onClick={() => setTransferModal(false)}
                  className="rounded-lg bg-slate-800 px-4 py-2 font-semibold text-slate-300 hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-lg bg-gradient-to-r from-[#F28C28] to-[#D97706] px-5 py-2 font-bold text-white shadow hover:from-[#FFA94D]"
                >
                  Submit Request
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

