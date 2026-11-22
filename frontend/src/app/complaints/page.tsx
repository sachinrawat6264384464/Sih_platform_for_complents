"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Complaint, Bureau, ComplaintCategory } from "@/lib/types";
import {
  FileSpreadsheet,
  Search,
  Plus,
  Clock,
  AlertCircle,
  CheckCircle2,
  GitBranch,
  Eye,
  Bot,
  X,
  ArrowRight,
  ShieldAlert,
} from "lucide-react";

const VALID_STATUSES = [
  "Received",
  "Acknowledged",
  "Under Review",
  "Assigned",
  "Under Process",
  "Investigation",
  "Pending Information",
  "Transferred",
  "Escalated",
  "Disposed",
  "Closed",
  "Reopened",
];

export default function ComplaintsPage() {
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [bureaus, setBureaus] = useState<Bureau[]>([]);
  const [categories, setCategories] = useState<ComplaintCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");

  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showTransitionModal, setShowTransitionModal] = useState(false);
  const [selectedComplaint, setSelectedComplaint] = useState<Complaint | null>(null);
  const [triageLoading, setTriageLoading] = useState(false);
  const [triageResult, setTriageResult] = useState<any | null>(null);

  // Create form
  const [createForm, setCreateForm] = useState({
    institution_id: "",
    bureau_id: "",
    category_id: "",
    title: "",
    description: "",
    priority: "Medium",
  });
  const [institutionsList, setInstitutionsList] = useState<any[]>([]);

  // Transition form
  const [newStatus, setNewStatus] = useState("");
  const [transitionRemarks, setTransitionRemarks] = useState("");
  const [transitionError, setTransitionError] = useState<string | null>(null);

  const fetchComplaints = async () => {
    setLoading(true);
    try {
      const params: any = { limit: 100 };
      if (search) params.search = search;
      if (statusFilter) params.status = statusFilter;
      if (priorityFilter) params.priority = priorityFilter;

      const res = await api.get("/complaints", { params });
      setComplaints(res.data.items || res.data || []);
    } catch (err) {
      console.error("Failed to load complaints", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAuxiliary = async () => {
    try {
      const [bRes, cRes, iRes] = await Promise.all([
        api.get("/bureaus"),
        api.get("/complaints/categories"),
        api.get("/institutions?limit=100"),
      ]);
      setBureaus(bRes.data || []);
      setCategories(cRes.data || []);
      setInstitutionsList(iRes.data.items || iRes.data || []);
      if (bRes.data?.length > 0) setCreateForm((prev) => ({ ...prev, bureau_id: bRes.data[0].id }));
      if (cRes.data?.length > 0) setCreateForm((prev) => ({ ...prev, category_id: cRes.data[0].id }));
      if (iRes.data?.items?.length > 0) setCreateForm((prev) => ({ ...prev, institution_id: iRes.data.items[0].id }));
    } catch (err) {
      console.error("Auxiliary fetch failed", err);
    }
  };

  useEffect(() => {
    fetchComplaints();
    fetchAuxiliary();
  }, [statusFilter, priorityFilter]);

  const handleRegisterComplaint = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/complaints", createForm);
      setShowCreateModal(false);
      setCreateForm({
        institution_id: institutionsList[0]?.id || "",
        bureau_id: bureaus[0]?.id || "",
        category_id: categories[0]?.id || "",
        title: "",
        description: "",
        priority: "Medium",
      });
      fetchComplaints();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Registration failed");
    }
  };

  const handleTransition = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedComplaint) return;
    setTransitionError(null);
    try {
      await api.post(`/complaints/${selectedComplaint.id}/transition`, {
        new_status: newStatus,
        remarks: transitionRemarks,
      });
      setShowTransitionModal(false);
      setSelectedComplaint(null);
      setTransitionRemarks("");
      fetchComplaints();
    } catch (err: any) {
      setTransitionError(err.response?.data?.detail || "Invalid state transition under workflow rules");
    }
  };

  const handleRunTriage = async (complaintId: string) => {
    setTriageLoading(true);
    setTriageResult(null);
    try {
      const res = await api.post(`/complaints/${complaintId}/triage`);
      setTriageResult(res.data);
    } catch (err: any) {
      alert(err.response?.data?.detail || "Triage execution failed");
    } finally {
      setTriageLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title & Actions */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            <FileSpreadsheet className="h-6 w-6 text-[#F28C28]" />
            Grievances & Complaints Redressal Desk
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Standardized 12-state case workflow, multi-bureau assignment, and automated triage
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center space-x-1.5 rounded-lg bg-gradient-to-r from-[#F28C28] to-[#D97706] px-4 py-2 text-xs font-bold text-white shadow-md shadow-orange-500/20 hover:from-[#FFA94D]"
          >
            <Plus className="h-4 w-4" />
            <span>Register Grievance</span>
          </button>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="rounded-xl border border-slate-700/80 bg-[#14233D] p-4 shadow-lg">
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
          <div className="sm:col-span-2 relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search by Complaint Number (AICTE-2026-XXXXXX) or Title..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && fetchComplaints()}
              className="w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2 pl-9 pr-3 text-xs text-white placeholder-slate-500 focus:border-[#F28C28] focus:outline-none"
            />
          </div>

          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2 px-3 text-xs text-slate-300 focus:border-[#F28C28] focus:outline-none"
            >
              <option value="">All Statuses (12 States)</option>
              {VALID_STATUSES.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          <div>
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2 px-3 text-xs text-slate-300 focus:border-[#F28C28] focus:outline-none"
            >
              <option value="">All Priorities</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>
        </div>
      </div>

      {/* Complaints Table */}
      <div className="rounded-xl border border-slate-700/80 bg-[#14233D] shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-[#0B1730] uppercase text-[10px] tracking-wider text-slate-400 border-b border-slate-700">
              <tr>
                <th className="px-4 py-3">Case ID</th>
                <th className="px-4 py-3">Institution & Title</th>
                <th className="px-4 py-3">Bureau</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Priority</th>
                <th className="px-4 py-3">SLA Target</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-slate-500">
                    Loading grievance dossier...
                  </td>
                </tr>
              ) : complaints.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-slate-500">
                    No complaints found matching criteria
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
                      <div className="text-[11px] text-slate-400 truncate max-w-sm">
                        {c.institution_name || "Institution ID: " + c.institution_id}
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
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold ${
                          c.priority === "Critical"
                            ? "bg-red-950 text-red-400 border border-red-800"
                            : c.priority === "High"
                            ? "bg-orange-950 text-[#FFA94D] border border-orange-800"
                            : "bg-slate-800 text-slate-300"
                        }`}
                      >
                        {c.priority}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-400 font-mono">
                      {c.sla_target_date ? new Date(c.sla_target_date).toLocaleDateString() : "30 Days"}
                    </td>
                    <td className="px-4 py-3 text-right space-x-1.5">
                      <button
                        onClick={() => {
                          setSelectedComplaint(c);
                          setNewStatus(c.status);
                          setShowTransitionModal(true);
                        }}
                        className="inline-flex items-center rounded bg-[#0B1730] px-2.5 py-1 text-slate-300 hover:text-[#F28C28] border border-slate-700"
                        title="Transition state"
                      >
                        <GitBranch className="h-3 w-3 mr-1" />
                        <span>Move</span>
                      </button>
                      <button
                        onClick={() => handleRunTriage(c.id)}
                        className="inline-flex items-center rounded bg-indigo-950/60 px-2.5 py-1 text-indigo-300 hover:text-indigo-100 border border-indigo-700"
                        title="AI Multi-Agent Triage"
                      >
                        <Bot className="h-3 w-3 mr-1" />
                        <span>Triage</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* AI Triage Result Banner */}
      {triageResult && (
        <div className="rounded-xl border border-indigo-500/50 bg-[#14233D] p-5 shadow-2xl space-y-3">
          <div className="flex items-center justify-between border-b border-indigo-900/60 pb-3">
            <div className="flex items-center space-x-2 text-indigo-400 font-bold text-sm">
              <Bot className="h-5 w-5" />
              <span>LangGraph Multi-Agent Triage Verdict & Evidence</span>
            </div>
            <button onClick={() => setTriageResult(null)} className="text-slate-400 hover:text-white">
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
            <div className="rounded-lg bg-[#0B1730] p-3 border border-slate-800">
              <span className="text-[10px] uppercase font-bold text-slate-500">Predicted Severity</span>
              <div className="text-sm font-bold text-[#FFA94D] mt-1">{triageResult.state?.classification?.severity || "High"}</div>
            </div>
            <div className="rounded-lg bg-[#0B1730] p-3 border border-slate-800">
              <span className="text-[10px] uppercase font-bold text-slate-500">Recommended Bureau</span>
              <div className="text-sm font-bold text-cyan-400 mt-1">{triageResult.state?.bureau_routing?.recommended_bureau || "PGRC"}</div>
            </div>
            <div className="rounded-lg bg-[#0B1730] p-3 border border-slate-800">
              <span className="text-[10px] uppercase font-bold text-slate-500">Sieve Overlap Detected</span>
              <div className="text-sm font-bold text-emerald-400 mt-1">{triageResult.state?.duplicate_detection?.potential_duplicates_count || 0} Related</div>
            </div>
          </div>

          <div className="rounded-lg bg-[#0B1730] p-3 border border-slate-800 text-xs">
            <span className="text-[10px] uppercase font-bold text-slate-500">Executive Summary & Next Actions</span>
            <p className="text-slate-300 mt-1">{triageResult.state?.summary?.actionable_summary || "Triage workflow completed across 5 stages with full trace audit."}</p>
          </div>
        </div>
      )}

      {/* State Transition Modal */}
      {showTransitionModal && selectedComplaint && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-md overflow-hidden rounded-xl border border-slate-700 bg-[#14233D] shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-700/80 px-6 py-4 bg-[#0B1730]">
              <div className="flex items-center space-x-2">
                <GitBranch className="h-5 w-5 text-[#F28C28]" />
                <h2 className="text-sm font-bold text-white tracking-wide">
                  Transition Status: {selectedComplaint.complaint_number}
                </h2>
              </div>
              <button onClick={() => setShowTransitionModal(false)} className="text-slate-400 hover:text-white">
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={handleTransition} className="p-6 space-y-4">
              {transitionError && (
                <div className="rounded-lg border border-red-500/40 bg-red-950/40 p-3 text-xs text-red-300 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-2 flex-shrink-0 text-red-400" />
                  <span>{transitionError}</span>
                </div>
              )}

              <div className="text-xs text-slate-300">
                Current Status: <span className="font-bold text-[#F28C28]">{selectedComplaint.status}</span>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300">Select Target Status *</label>
                <select
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value)}
                  required
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2 px-3 text-xs text-slate-300 focus:border-[#F28C28] focus:outline-none"
                >
                  {VALID_STATUSES.map((st) => (
                    <option key={st} value={st}>{st}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300">Statutory Officer Remarks *</label>
                <textarea
                  required
                  rows={3}
                  value={transitionRemarks}
                  onChange={(e) => setTransitionRemarks(e.target.value)}
                  placeholder="Record justification for status progression under AICTE Redressal Rules..."
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-[#0B1730] p-2 text-xs text-white focus:border-[#F28C28] focus:outline-none"
                />
              </div>

              <div className="flex justify-end space-x-3 border-t border-slate-700/80 pt-4">
                <button
                  type="button"
                  onClick={() => setShowTransitionModal(false)}
                  className="rounded-lg bg-slate-800 px-4 py-2 text-xs font-semibold text-slate-300 hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-lg bg-gradient-to-r from-[#F28C28] to-[#D97706] px-5 py-2 text-xs font-bold text-white shadow hover:from-[#FFA94D]"
                >
                  Confirm Transition
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Register Complaint Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-xl overflow-hidden rounded-xl border border-slate-700 bg-[#14233D] shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-700/80 px-6 py-4 bg-[#0B1730]">
              <div className="flex items-center space-x-2">
                <Plus className="h-5 w-5 text-[#F28C28]" />
                <h2 className="text-sm font-bold text-white tracking-wide">
                  Register Official Grievance Dossier
                </h2>
              </div>
              <button onClick={() => setShowCreateModal(false)} className="text-slate-400 hover:text-white">
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={handleRegisterComplaint} className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300">Target Educational Institution *</label>
                <select
                  required
                  value={createForm.institution_id}
                  onChange={(e) => setCreateForm({ ...createForm, institution_id: e.target.value })}
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2 px-3 text-xs text-slate-300 focus:border-[#F28C28] focus:outline-none"
                >
                  {institutionsList.map((inst) => (
                    <option key={inst.id} value={inst.id}>
                      {inst.name} ({inst.aicte_permanent_id})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300">Jurisdictional Bureau *</label>
                  <select
                    required
                    value={createForm.bureau_id}
                    onChange={(e) => setCreateForm({ ...createForm, bureau_id: e.target.value })}
                    className="mt-1 w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2 px-3 text-xs text-slate-300 focus:border-[#F28C28] focus:outline-none"
                  >
                    {bureaus.map((b) => (
                      <option key={b.id} value={b.id}>{b.name} ({b.code})</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300">Grievance Category *</label>
                  <select
                    required
                    value={createForm.category_id}
                    onChange={(e) => setCreateForm({ ...createForm, category_id: e.target.value })}
                    className="mt-1 w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2 px-3 text-xs text-slate-300 focus:border-[#F28C28] focus:outline-none"
                  >
                    {categories.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300">Subject / Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Unlawful collection of capitation fees and withholding certificates"
                  value={createForm.title}
                  onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2 px-3 text-xs text-white focus:border-[#F28C28] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300">Detailed Complaint Narrative *</label>
                <textarea
                  required
                  rows={4}
                  placeholder="State the facts, dates, affected students, financial demands, and statutory violations..."
                  value={createForm.description}
                  onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-[#0B1730] p-2.5 text-xs text-white focus:border-[#F28C28] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300">Statutory Priority</label>
                <select
                  value={createForm.priority}
                  onChange={(e) => setCreateForm({ ...createForm, priority: e.target.value })}
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2 px-3 text-xs text-slate-300 focus:border-[#F28C28] focus:outline-none"
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Critical">Critical</option>
                </select>
              </div>

              <div className="flex justify-end space-x-3 border-t border-slate-700/80 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="rounded-lg bg-slate-800 px-4 py-2 text-xs font-semibold text-slate-300 hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-lg bg-gradient-to-r from-[#F28C28] to-[#D97706] px-5 py-2 text-xs font-bold text-white shadow hover:from-[#FFA94D]"
                >
                  Submit Grievance
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

