"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import {
  Bot,
  Search,
  Sparkles,
  GitBranch,
  FileText,
  Building2,
  CheckCircle2,
  AlertCircle,
  Play,
  ArrowRight,
} from "lucide-react";

export default function AIAssistantPage() {
  const [activeTab, setActiveTab] = useState<"rag" | "triage">("rag");

  // Hybrid RAG states
  const [query, setQuery] = useState("capitation fee and withheld hall tickets");
  const [topK, setTopK] = useState(5);
  const [searching, setSearching] = useState(false);
  const [ragResults, setRagResults] = useState<any | null>(null);

  // AI Triage states
  const [complaintId, setComplaintId] = useState("");
  const [complaintsList, setComplaintsList] = useState<any[]>([]);
  const [triaging, setTriaging] = useState(false);
  const [triageOutput, setTriageOutput] = useState<any | null>(null);

  useEffect(() => {
    // load complaints list for triage selector
    api.get("/complaints?limit=30").then((res) => {
      const items = res.data.items || res.data || [];
      setComplaintsList(items);
      if (items.length > 0) {
        setComplaintId(items[0].id);
      }
    }).catch(console.error);
  }, []);

  const handleRunRAG = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setSearching(true);
    setRagResults(null);
    try {
      const res = await api.post("/rag/query", {
        query: query.trim(),
        top_k: topK,
      });
      setRagResults(res.data);
    } catch (err: any) {
      alert(err.response?.data?.detail || "RAG retrieval query failed");
    } finally {
      setSearching(false);
    }
  };

  const handleRunTriage = async () => {
    if (!complaintId) return;
    setTriaging(true);
    setTriageOutput(null);
    try {
      const res = await api.post(`/complaints/${complaintId}/triage`);
      setTriageOutput(res.data);
    } catch (err: any) {
      alert(err.response?.data?.detail || "Multi-agent triage execution failed");
    } finally {
      setTriaging(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            <Bot className="h-6 w-6 text-[#F28C28]" />
            AI Intelligence & Hybrid RAG Assistant Studio
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Evidence-grounded hybrid BM25 + dense vector cosine retrieval and LangGraph multi-agent triage
          </p>
        </div>

        {/* Mode Switcher Tabs */}
        <div className="flex rounded-lg bg-[#14233D] p-1 border border-slate-700">
          <button
            onClick={() => setActiveTab("rag")}
            className={`rounded-md px-4 py-1.5 text-xs font-bold transition-all ${
              activeTab === "rag"
                ? "bg-[#F28C28] text-white shadow"
                : "text-slate-300 hover:text-white"
            }`}
          >
            Hybrid RAG Retrieval
          </button>
          <button
            onClick={() => setActiveTab("triage")}
            className={`rounded-md px-4 py-1.5 text-xs font-bold transition-all ${
              activeTab === "triage"
                ? "bg-[#F28C28] text-white shadow"
                : "text-slate-300 hover:text-white"
            }`}
          >
            LangGraph Multi-Agent Triage
          </button>
        </div>
      </div>

      {/* Mode 1: Hybrid RAG Search */}
      {activeTab === "rag" && (
        <div className="space-y-5">
          <div className="rounded-xl border border-slate-700/80 bg-[#14233D] p-5 shadow-lg">
            <form onSubmit={handleRunRAG} className="space-y-3">
              <label className="block text-xs font-semibold text-slate-300">
                Natural Language Grievance Query / Statutory Topic
              </label>
              <div className="flex gap-3">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                  <input
                    type="text"
                    required
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="e.g. Mandatory donation for admission or non-refund of caution deposit"
                    className="w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2.5 pl-10 pr-4 text-xs text-white focus:border-[#F28C28] focus:outline-none"
                  />
                </div>
                <div className="w-24">
                  <select
                    value={topK}
                    onChange={(e) => setTopK(Number(e.target.value))}
                    className="w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2.5 px-3 text-xs text-slate-300 focus:border-[#F28C28] focus:outline-none"
                  >
                    <option value={3}>Top 3</option>
                    <option value={5}>Top 5</option>
                    <option value={10}>Top 10</option>
                  </select>
                </div>
                <button
                  type="submit"
                  disabled={searching}
                  className="flex items-center space-x-1.5 rounded-lg bg-gradient-to-r from-[#F28C28] to-[#D97706] px-5 py-2.5 text-xs font-bold text-white shadow hover:from-[#FFA94D] disabled:opacity-50"
                >
                  <Sparkles className="h-4 w-4" />
                  <span>{searching ? "Searching..." : "Retrieve Evidence"}</span>
                </button>
              </div>
            </form>
          </div>

          {/* RAG Results Display */}
          {ragResults && (
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs text-slate-400 px-1">
                <span>
                  Found <strong className="text-white">{ragResults.results?.length || 0}</strong> relevant dossiers across candidate corpus
                </span>
                <span className="font-mono text-cyan-400">
                  Latency: {ragResults.latency_ms}ms (Hybrid Reciprocal Fusion)
                </span>
              </div>

              {ragResults.results?.length === 0 ? (
                <div className="rounded-xl border border-slate-700/80 bg-[#14233D] p-8 text-center text-xs text-slate-400">
                  No grievances matched the specified hybrid query threshold
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-4">
                  {ragResults.results.map((item: any, idx: number) => (
                    <div
                      key={item.complaint_id || idx}
                      className="rounded-xl border border-slate-700/80 bg-[#14233D] p-5 shadow-lg space-y-3 hover:border-slate-600 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className="font-mono font-bold text-sm text-white">
                              {item.complaint_number}
                            </span>
                            <span className="text-xs text-slate-400">|</span>
                            <span className="text-xs font-semibold text-[#FFA94D]">
                              {item.institution_name}
                            </span>
                            <span className="text-[10px] font-mono text-slate-500">
                              ({item.aicte_permanent_id})
                            </span>
                          </div>
                          <h2 className="text-sm font-bold text-slate-100 mt-1">{item.title}</h2>
                        </div>

                        {/* Scores Pill */}
                        <div className="flex items-center space-x-2 text-right">
                          <div className="rounded-lg bg-[#0B1730] px-3 py-1.5 border border-slate-800">
                            <div className="text-[9px] uppercase font-bold text-slate-400">Hybrid Score</div>
                            <div className="font-mono font-black text-cyan-400 text-xs">
                              {Math.round(item.hybrid_score * 100)}%
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Snippet */}
                      <p className="text-xs text-slate-300 leading-relaxed bg-[#0B1730] p-3 rounded-lg border border-slate-800">
                        {item.snippet}
                      </p>

                      <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800">
                        <span>Bureau: <strong className="text-slate-200">{item.bureau_name}</strong></span>
                        <span>Category: <strong className="text-slate-200">{item.category}</strong></span>
                        <span>Status: <strong className="text-slate-200">{item.status}</strong></span>
                        <span className="font-mono text-slate-500">BM25: {item.bm25_score} | Dense: {item.vector_score}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Mode 2: LangGraph Multi-Agent Triage Simulator */}
      {activeTab === "triage" && (
        <div className="space-y-5">
          <div className="rounded-xl border border-slate-700/80 bg-[#14233D] p-5 shadow-lg space-y-4">
            <h2 className="text-sm font-bold text-white tracking-wide">
              Execute Autonomous Multi-Agent Triage Pipeline
            </h2>
            <p className="text-xs text-slate-400">
              Dispatches the 5-node LangGraph orchestration graph: Ingestion -&gt; Classification -&gt; Bureau Routing -&gt; Overlap Detection -&gt; Actionable Summary.
            </p>

            <div className="flex gap-3">
              <select
                value={complaintId}
                onChange={(e) => setComplaintId(e.target.value)}
                className="flex-1 rounded-lg border border-slate-700 bg-[#0B1730] py-2.5 px-3 text-xs text-white focus:border-[#F28C28] focus:outline-none"
              >
                {complaintsList.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.complaint_number} — {c.title} ({c.bureau_name || "PGRC"})
                  </option>
                ))}
              </select>

              <button
                onClick={handleRunTriage}
                disabled={triaging || !complaintId}
                className="flex items-center space-x-1.5 rounded-lg bg-gradient-to-r from-indigo-600 to-indigo-700 px-5 py-2.5 text-xs font-bold text-white shadow hover:from-indigo-500 disabled:opacity-50"
              >
                <Play className="h-3.5 w-3.5 fill-current" />
                <span>{triaging ? "Agents Running..." : "Execute Agentic Triage"}</span>
              </button>
            </div>
          </div>

          {/* Triage Output & Execution Trace */}
          {triageOutput && (
            <div className="space-y-4">
              {/* Verdict Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="rounded-xl border border-slate-700/80 bg-[#14233D] p-4 shadow">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Classification</span>
                  <div className="text-base font-bold text-[#FFA94D] mt-1">
                    {triageOutput.state?.classification?.severity} Severity
                  </div>
                  <div className="text-xs text-slate-400 mt-0.5">
                    Category: {triageOutput.state?.classification?.category}
                  </div>
                </div>

                <div className="rounded-xl border border-slate-700/80 bg-[#14233D] p-4 shadow">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Bureau Routing</span>
                  <div className="text-base font-bold text-cyan-400 mt-1">
                    {triageOutput.state?.bureau_routing?.recommended_bureau}
                  </div>
                  <div className="text-xs text-slate-400 mt-0.5">
                    SLA: {triageOutput.state?.bureau_routing?.target_sla_days} Days
                  </div>
                </div>

                <div className="rounded-xl border border-slate-700/80 bg-[#14233D] p-4 shadow">
                  <span className="text-[10px] uppercase font-bold text-slate-400">8-Stage Sieve Result</span>
                  <div className="text-base font-bold text-emerald-400 mt-1">
                    {triageOutput.state?.duplicate_detection?.potential_duplicates_count || 0} Related Cases
                  </div>
                  <div className="text-xs text-slate-400 mt-0.5">
                    Highest Match: {Math.round((triageOutput.state?.duplicate_detection?.highest_similarity_score || 0) * 100)}%
                  </div>
                </div>
              </div>

              {/* Actionable Summary */}
              <div className="rounded-xl border border-slate-700/80 bg-[#14233D] p-5 shadow-lg space-y-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                  Formulated Action Plan & Investigation Recommendation
                </h3>
                <p className="text-xs text-slate-200 leading-relaxed bg-[#0B1730] p-4 rounded-lg border border-slate-800">
                  {triageOutput.state?.summary?.actionable_summary}
                </p>
              </div>

              {/* Step-by-Step Graph Trace */}
              <div className="rounded-xl border border-slate-700/80 bg-[#14233D] p-5 shadow-lg space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                  <GitBranch className="h-4 w-4 text-[#F28C28]" />
                  LangGraph Orchestration Trace ({triageOutput.state?.trace?.length || 0} Steps)
                </h3>
                <div className="space-y-2">
                  {triageOutput.state?.trace?.map((step: any, idx: number) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between rounded-lg bg-[#0B1730] px-4 py-2 text-xs border border-slate-800"
                    >
                      <div className="flex items-center space-x-2">
                        <CheckCircle2 className="h-4 w-4 text-emerald-400 flex-shrink-0" />
                        <span className="font-bold text-white capitalize">{step.agent?.replace(/_/g, " ")} Agent</span>
                        <span className="text-slate-400">— {step.action}</span>
                      </div>
                      <span className="font-mono text-[10px] text-slate-500">
                        {step.timestamp ? new Date(step.timestamp).toLocaleTimeString() : ""}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

