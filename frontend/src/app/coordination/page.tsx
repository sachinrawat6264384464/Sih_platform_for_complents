"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { OverlapCandidate } from "@/lib/types";
import {
  GitCompare,
  CheckCircle2,
  XCircle,
  RefreshCw,
  AlertTriangle,
  Layers,
  ArrowRight,
  ShieldCheck,
  Search,
  Sliders,
  X,
} from "lucide-react";

export default function CoordinationPage() {
  const [candidates, setCandidates] = useState<OverlapCandidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [reviewing, setReviewing] = useState<OverlapCandidate | null>(null);
  const [remarks, setRemarks] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [scanning, setScanning] = useState(false);

  const fetchCandidates = async () => {
    setLoading(true);
    try {
      const res = await api.get("/overlap/candidates");
      setCandidates(res.data.items || res.data || []);
    } catch (err) {
      console.error("Failed to load overlap candidates", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidates();
  }, []);

  const handleScanNow = async () => {
    setScanning(true);
    try {
      const res = await api.post("/overlap/scan");
      alert(`Sieve scan completed. Analyzed ${res.data.pairs_analyzed} pairs, generated ${res.data.candidates_generated} overlap candidates.`);
      fetchCandidates();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Scan execution failed");
    } finally {
      setScanning(false);
    }
  };

  const handleReviewAction = async (status: "Confirmed" | "Rejected") => {
    if (!reviewing) return;
    setSubmitting(true);
    try {
      await api.post(`/overlap/candidates/${reviewing.id}/review`, {
        action: status,
        remarks: remarks || `Officer reviewed and marked as ${status} under coordination protocol.`,
      });
      setReviewing(null);
      setRemarks("");
      fetchCandidates();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Review submission failed");
    } finally {
      setSubmitting(false);
    }
  };

  const getScoreBadgeColor = (score: number) => {
    if (score >= 0.8) return "bg-red-950 text-red-400 border-red-800";
    if (score >= 0.6) return "bg-orange-950 text-[#FFA94D] border-orange-800";
    return "bg-cyan-950 text-cyan-300 border-cyan-800";
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            <GitCompare className="h-6 w-6 text-[#F28C28]" />
            Multi-Bureau Overlap Sieve & Coordination Workspace
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Algorithmic 8-stage sieve cross-referencing PGRC, Regulation Bureau & Regional cases for duplicate prevention
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchCandidates}
            className="flex items-center space-x-1.5 rounded-lg border border-slate-700 bg-[#14233D] px-3.5 py-2 text-xs font-semibold text-slate-200 hover:border-slate-600 shadow-sm"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={handleScanNow}
            disabled={scanning}
            className="flex items-center space-x-1.5 rounded-lg bg-gradient-to-r from-[#F28C28] to-[#D97706] px-4 py-2 text-xs font-bold text-white shadow-md shadow-orange-500/20 hover:from-[#FFA94D] disabled:opacity-50"
          >
            <Sliders className="h-4 w-4" />
            <span>{scanning ? "Sieve Scanning..." : "Run 8-Stage Sieve Scan"}</span>
          </button>
        </div>
      </div>

      {/* Sieve Explainer Card */}
      <div className="rounded-xl border border-slate-700/80 bg-[#14233D] p-5 shadow-lg">
        <h2 className="text-xs font-bold uppercase tracking-wider text-cyan-400 mb-2">
          The 8-Stage Deterministic & Probabilistic Sieve Framework
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] text-slate-300">
          <div className="rounded bg-[#0B1730] p-2 border border-slate-800">
            <span className="font-bold text-[#F28C28]">Stage 1:</span> Exact AICTE Permanent ID
          </div>
          <div className="rounded bg-[#0B1730] p-2 border border-slate-800">
            <span className="font-bold text-[#F28C28]">Stage 2:</span> Trigram Name Similarity
          </div>
          <div className="rounded bg-[#0B1730] p-2 border border-slate-800">
            <span className="font-bold text-[#F28C28]">Stage 3:</span> Category Matching
          </div>
          <div className="rounded bg-[#0B1730] p-2 border border-slate-800">
            <span className="font-bold text-[#F28C28]">Stage 4:</span> 180-Day Window Sieve
          </div>
          <div className="rounded bg-[#0B1730] p-2 border border-slate-800">
            <span className="font-bold text-cyan-400">Stage 5:</span> Complainant Phone/Aadhaar Sieve
          </div>
          <div className="rounded bg-[#0B1730] p-2 border border-slate-800">
            <span className="font-bold text-cyan-400">Stage 6:</span> Geographic & District Bounds
          </div>
          <div className="rounded bg-[#0B1730] p-2 border border-slate-800">
            <span className="font-bold text-cyan-400">Stage 7:</span> Hybrid BM25 & Dense Cosine
          </div>
          <div className="rounded bg-[#0B1730] p-2 border border-slate-800">
            <span className="font-bold text-emerald-400">Stage 8:</span> Regulatory Multiplier
          </div>
        </div>
      </div>

      {/* Candidates List */}
      <div className="rounded-xl border border-slate-700/80 bg-[#14233D] shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-[#0B1730] uppercase text-[10px] tracking-wider text-slate-400 border-b border-slate-700">
              <tr>
                <th className="px-4 py-3">Overlap Score</th>
                <th className="px-4 py-3">Source Case</th>
                <th className="px-4 py-3">Target Case</th>
                <th className="px-4 py-3">Common Institution</th>
                <th className="px-4 py-3">Review Status</th>
                <th className="px-4 py-3 text-right">Coordination Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                    Evaluating potential overlaps...
                  </td>
                </tr>
              ) : candidates.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                    No active overlap candidates requiring review. Click &quot;Run 8-Stage Sieve Scan&quot; to test active database records.
                  </td>
                </tr>
              ) : (
                candidates.map((cand) => (
                  <tr key={cand.id} className="hover:bg-[#1E355B]/40 transition-colors">
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono font-black border ${getScoreBadgeColor(
                          cand.overall_score
                        )}`}
                      >
                        {Math.round(cand.overall_score * 100)}% Match
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-mono font-bold text-white">
                        {cand.source_complaint_number || cand.source_complaint_id.slice(0, 8)}
                      </div>
                      <div className="text-[10px] text-slate-400">
                        Bureau: {cand.source_bureau_name || "PGRC"}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-mono font-bold text-white">
                        {cand.target_complaint_number || cand.target_complaint_id.slice(0, 8)}
                      </div>
                      <div className="text-[10px] text-slate-400">
                        Bureau: {cand.target_bureau_name || "Regulation Bureau"}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="font-semibold text-slate-200">
                        {cand.institution_name || "Identical Entity Sieve"}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold ${
                          cand.review_status === "Confirmed"
                            ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                            : cand.review_status === "Rejected"
                            ? "bg-red-950 text-red-400 border border-red-800"
                            : "bg-yellow-950 text-yellow-300 border border-yellow-800"
                        }`}
                      >
                        {cand.review_status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => {
                          setReviewing(cand);
                          setRemarks("");
                        }}
                        className="inline-flex items-center space-x-1 rounded bg-[#0B1730] px-3 py-1.5 text-xs font-semibold text-[#F28C28] hover:border-[#F28C28] border border-slate-700 transition-colors"
                      >
                        <span>Examine Evidence</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Review & Side-by-Side Sieve Breakdown Modal */}
      {reviewing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-3xl overflow-hidden rounded-xl border border-slate-700 bg-[#14233D] shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-700/80 px-6 py-4 bg-[#0B1730]">
              <div className="flex items-center space-x-2">
                <GitCompare className="h-5 w-5 text-[#F28C28]" />
                <h2 className="text-sm font-bold text-white tracking-wide">
                  Side-By-Side Overlap Examination & Multi-Bureau Linkage
                </h2>
              </div>
              <button onClick={() => setReviewing(null)} className="text-slate-400 hover:text-white">
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="p-6 space-y-4 max-h-[75vh] overflow-y-auto text-xs">
              {/* Overall Sieve Score */}
              <div className="flex items-center justify-between rounded-lg bg-[#0B1730] p-4 border border-slate-800">
                <div>
                  <div className="text-xs text-slate-400 uppercase font-bold tracking-wider">
                    Computed Sieve Confidence Score
                  </div>
                  <div className="text-xl font-black text-white font-mono mt-1">
                    {Math.round(reviewing.overall_score * 100)}% Cross-Case Probability
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-[11px] text-slate-400">Strict Human Oversight:</span>
                  <div className="text-xs text-emerald-400 font-semibold mt-0.5">
                    No automatic merging or regulatory closures
                  </div>
                </div>
              </div>

              {/* Side-by-side Case Header */}
              <div className="grid grid-cols-2 gap-4">
                <div className="rounded-lg bg-[#0B1730] p-4 border border-slate-800">
                  <div className="text-[10px] uppercase font-bold text-[#F28C28]">
                    Source Grievance Dossier
                  </div>
                  <div className="text-sm font-bold text-white mt-1">
                    {reviewing.source_complaint_number || reviewing.source_complaint_id}
                  </div>
                  <div className="text-xs text-slate-400 mt-1">Bureau: {reviewing.source_bureau_name || "PGRC"}</div>
                </div>

                <div className="rounded-lg bg-[#0B1730] p-4 border border-slate-800">
                  <div className="text-[10px] uppercase font-bold text-cyan-400">
                    Target Grievance Dossier
                  </div>
                  <div className="text-sm font-bold text-white mt-1">
                    {reviewing.target_complaint_number || reviewing.target_complaint_id}
                  </div>
                  <div className="text-xs text-slate-400 mt-1">Bureau: {reviewing.target_bureau_name || "Regulation Bureau"}</div>
                </div>
              </div>

              {/* 8-Stage Detailed Breakdown */}
              <div className="border-t border-slate-700/80 pt-4">
                <h3 className="font-bold text-white text-xs uppercase tracking-wider mb-2">
                  Individual Stage Scores
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {Object.entries(reviewing.stage_scores || {}).map(([stage, score]) => (
                    <div key={stage} className="rounded bg-[#0B1730] p-2 border border-slate-800">
                      <div className="text-[10px] text-slate-400 truncate capitalize">
                        {stage.replace(/_/g, " ")}
                      </div>
                      <div className="font-mono font-bold text-white mt-0.5">
                        {typeof score === "number" ? `${Math.round(score * 100)}%` : String(score)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Officer Decision Remarks */}
              <div className="border-t border-slate-700/80 pt-4">
                <label className="block text-xs font-semibold text-slate-300">
                  Officer Statutory Coordination Remarks *
                </label>
                <textarea
                  rows={2}
                  value={remarks}
                  onChange={(e) => setRemarks(e.target.value)}
                  placeholder="Record findings of overlap examination. Confirmed links create joint coordination monitoring without merging original citizen complaints."
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-[#0B1730] p-2.5 text-xs text-white focus:border-[#F28C28] focus:outline-none"
                />
              </div>
            </div>

            {/* Decision Buttons */}
            <div className="flex items-center justify-between border-t border-slate-700/80 bg-[#0B1730] px-6 py-3">
              <button
                type="button"
                onClick={() => setReviewing(null)}
                className="rounded-lg bg-slate-800 px-4 py-2 text-xs font-semibold text-slate-300 hover:bg-slate-700"
              >
                Close
              </button>

              <div className="flex space-x-3">
                <button
                  type="button"
                  disabled={submitting}
                  onClick={() => handleReviewAction("Rejected")}
                  className="flex items-center rounded-lg bg-red-950/80 border border-red-800 px-4 py-2 text-xs font-bold text-red-300 hover:bg-red-900"
                >
                  <XCircle className="h-4 w-4 mr-1.5" />
                  <span>Mark False Positive</span>
                </button>
                <button
                  type="button"
                  disabled={submitting}
                  onClick={() => handleReviewAction("Confirmed")}
                  className="flex items-center rounded-lg bg-gradient-to-r from-emerald-600 to-emerald-700 px-5 py-2 text-xs font-bold text-white shadow hover:from-emerald-500"
                >
                  <CheckCircle2 className="h-4 w-4 mr-1.5" />
                  <span>Confirm Coordination Link</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

