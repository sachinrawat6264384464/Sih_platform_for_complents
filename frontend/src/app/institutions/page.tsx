"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Institution } from "@/lib/types";
import {
  Building2,
  Search,
  Plus,
  Filter,
  Download,
  Eye,
  CheckCircle2,
  MapPin,
  FileText,
  X,
  AlertCircle,
  ExternalLink,
} from "lucide-react";

export default function InstitutionsPage() {
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [stateFilter, setStateFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [selectedInstitution, setSelectedInstitution] = useState<Institution | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Form state for new institution
  const [formData, setFormData] = useState({
    aicte_permanent_id: "",
    name: "",
    institution_type: "Engineering & Technology",
    address: "",
    city: "",
    district: "",
    state: "Delhi",
    pincode: "110001",
    approval_status: "Approved",
    contact_email: "",
    contact_phone: "",
  });
  const [formError, setFormError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  const fetchInstitutions = async () => {
    setLoading(true);
    try {
      const params: any = { limit: 100 };
      if (search) params.search = search;
      if (stateFilter) params.state = stateFilter;
      if (typeFilter) params.institution_type = typeFilter;

      const res = await api.get("/institutions", { params });
      setInstitutions(res.data.items || res.data || []);
    } catch (err) {
      console.error("Failed to load institutions", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInstitutions();
  }, [stateFilter, typeFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchInstitutions();
  };

  const handleCreateInstitution = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    setFormError(null);
    try {
      await api.post("/institutions", {
        ...formData,
        alternate_names: [],
      });
      setShowCreateModal(false);
      setFormData({
        aicte_permanent_id: "",
        name: "",
        institution_type: "Engineering & Technology",
        address: "",
        city: "",
        district: "",
        state: "Delhi",
        pincode: "110001",
        approval_status: "Approved",
        contact_email: "",
        contact_phone: "",
      });
      fetchInstitutions();
    } catch (err: any) {
      setFormError(err.response?.data?.detail || "Failed to register institution");
    } finally {
      setCreating(false);
    }
  };

  const handleExportCSV = async () => {
    try {
      const res = await api.get("/reports/export/institutions", { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `aicte_institutions_${Date.now()}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch {
      alert("Failed to export CSV");
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Title & Actions */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            <Building2 className="h-6 w-6 text-[#F28C28]" />
            Institutions Directory & Profiles
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Authoritative registry of technical education institutes, AICTE permanent IDs & complaint loads
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleExportCSV}
            className="flex items-center space-x-1.5 rounded-lg border border-slate-700 bg-[#14233D] px-3.5 py-2 text-xs font-semibold text-slate-200 hover:border-slate-600 shadow-sm"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center space-x-1.5 rounded-lg bg-gradient-to-r from-[#F28C28] to-[#D97706] px-4 py-2 text-xs font-bold text-white shadow-md shadow-orange-500/20 hover:from-[#FFA94D]"
          >
            <Plus className="h-4 w-4" />
            <span>Register Institution</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="rounded-xl border border-slate-700/80 bg-[#14233D] p-4 shadow-lg">
        <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 sm:grid-cols-4 gap-3">
          <div className="sm:col-span-2 relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search by Institution Name, AICTE Permanent ID (1-XXXXXXX)..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2 pl-9 pr-3 text-xs text-white placeholder-slate-500 focus:border-[#F28C28] focus:outline-none"
            />
          </div>

          <div>
            <select
              value={stateFilter}
              onChange={(e) => setStateFilter(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2 px-3 text-xs text-slate-300 focus:border-[#F28C28] focus:outline-none"
            >
              <option value="">All States / UTs</option>
              <option value="Delhi">Delhi</option>
              <option value="Maharashtra">Maharashtra</option>
              <option value="Karnataka">Karnataka</option>
              <option value="Tamil Nadu">Tamil Nadu</option>
              <option value="Uttar Pradesh">Uttar Pradesh</option>
            </select>
          </div>

          <div>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2 px-3 text-xs text-slate-300 focus:border-[#F28C28] focus:outline-none"
            >
              <option value="">All Institution Types</option>
              <option value="Engineering & Technology">Engineering & Technology</option>
              <option value="Management">Management</option>
              <option value="Pharmacy">Pharmacy</option>
              <option value="Autonomous">Autonomous</option>
              <option value="University Department">University Department</option>
            </select>
          </div>
        </form>
      </div>

      {/* Institutions Table */}
      <div className="rounded-xl border border-slate-700/80 bg-[#14233D] shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-[#0B1730] uppercase text-[10px] tracking-wider text-slate-400 border-b border-slate-700">
              <tr>
                <th className="px-4 py-3">Permanent ID</th>
                <th className="px-4 py-3">Institution Name</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">State / City</th>
                <th className="px-4 py-3">Approval Status</th>
                <th className="px-4 py-3 text-center">Complaints</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-slate-500">
                    Querying registered institutions...
                  </td>
                </tr>
              ) : institutions.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-slate-500">
                    No institutions found matching criteria
                  </td>
                </tr>
              ) : (
                institutions.map((inst) => (
                  <tr key={inst.id} className="hover:bg-[#1E355B]/40 transition-colors">
                    <td className="px-4 py-3 font-mono font-bold text-[#F28C28]">
                      {inst.aicte_permanent_id}
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-semibold text-white">{inst.name}</div>
                      <div className="text-[11px] text-slate-400 truncate max-w-xs">{inst.address}</div>
                    </td>
                    <td className="px-4 py-3 text-slate-300">{inst.institution_type}</td>
                    <td className="px-4 py-3 text-slate-300">
                      {inst.city}, {inst.state}
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                        {inst.approval_status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center font-mono font-bold text-slate-200">
                      {inst.complaint_count || 0}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => setSelectedInstitution(inst)}
                        className="inline-flex items-center space-x-1 rounded bg-[#0B1730] px-2.5 py-1 text-slate-300 hover:text-cyan-400 hover:border-cyan-500 border border-slate-700 transition-colors"
                      >
                        <Eye className="h-3 w-3" />
                        <span>Profile</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Institution Detail Profile Modal */}
      {selectedInstitution && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-2xl overflow-hidden rounded-xl border border-slate-700 bg-[#14233D] shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-700/80 px-6 py-4 bg-[#0B1730]">
              <div className="flex items-center space-x-2">
                <Building2 className="h-5 w-5 text-[#F28C28]" />
                <h2 className="text-sm font-bold text-white tracking-wide">
                  Institution Dossier: {selectedInstitution.aicte_permanent_id}
                </h2>
              </div>
              <button
                onClick={() => setSelectedInstitution(null)}
                className="text-slate-400 hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="p-6 space-y-4 max-h-[75vh] overflow-y-auto text-xs text-slate-300">
              <div>
                <h3 className="text-base font-black text-white">{selectedInstitution.name}</h3>
                <p className="text-slate-400 mt-0.5">{selectedInstitution.address}, {selectedInstitution.city}, {selectedInstitution.district}, {selectedInstitution.state} - {selectedInstitution.pincode}</p>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 border-t border-slate-700/80 pt-4">
                <div className="rounded-lg bg-[#0B1730] p-3 border border-slate-800">
                  <span className="text-[10px] uppercase font-bold text-slate-500">AICTE Permanent ID</span>
                  <div className="text-sm font-mono font-bold text-[#F28C28] mt-1">{selectedInstitution.aicte_permanent_id}</div>
                </div>
                <div className="rounded-lg bg-[#0B1730] p-3 border border-slate-800">
                  <span className="text-[10px] uppercase font-bold text-slate-500">Approval Status</span>
                  <div className="text-sm font-bold text-emerald-400 mt-1">{selectedInstitution.approval_status}</div>
                </div>
                <div className="rounded-lg bg-[#0B1730] p-3 border border-slate-800">
                  <span className="text-[10px] uppercase font-bold text-slate-500">Institution Type</span>
                  <div className="text-sm font-bold text-slate-200 mt-1">{selectedInstitution.institution_type}</div>
                </div>
              </div>

              <div className="border-t border-slate-700/80 pt-4">
                <h4 className="font-bold text-white mb-2">Connected Grievance Summary</h4>
                <p className="text-slate-400">
                  This institution has {selectedInstitution.complaint_count || 0} registered grievances in AICTE records. Multiple simultaneous grievances trigger automated multi-bureau overlap analysis.
                </p>
              </div>
            </div>

            <div className="flex justify-end border-t border-slate-700/80 bg-[#0B1730] px-6 py-3">
              <button
                onClick={() => setSelectedInstitution(null)}
                className="rounded-lg bg-slate-800 px-4 py-1.5 text-xs font-semibold text-slate-300 hover:bg-slate-700"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Register Institution Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-xl overflow-hidden rounded-xl border border-slate-700 bg-[#14233D] shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-700/80 px-6 py-4 bg-[#0B1730]">
              <div className="flex items-center space-x-2">
                <Plus className="h-5 w-5 text-[#F28C28]" />
                <h2 className="text-sm font-bold text-white tracking-wide">
                  Register Technical Institution
                </h2>
              </div>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={handleCreateInstitution} className="p-6 space-y-4">
              {formError && (
                <div className="rounded-lg border border-red-500/40 bg-red-950/40 p-3 text-xs text-red-300 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-2 flex-shrink-0 text-red-400" />
                  <span>{formError}</span>
                </div>
              )}

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300">AICTE Permanent ID *</label>
                  <input
                    type="text"
                    required
                    placeholder="1-XXXXXXXXXX"
                    value={formData.aicte_permanent_id}
                    onChange={(e) => setFormData({ ...formData, aicte_permanent_id: e.target.value })}
                    className="mt-1 w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2 px-3 text-xs text-white font-mono focus:border-[#F28C28] focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300">Approval Status</label>
                  <select
                    value={formData.approval_status}
                    onChange={(e) => setFormData({ ...formData, approval_status: e.target.value })}
                    className="mt-1 w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2 px-3 text-xs text-slate-300 focus:border-[#F28C28] focus:outline-none"
                  >
                    <option value="Approved">Approved</option>
                    <option value="Under Review">Under Review</option>
                    <option value="Suspended">Suspended</option>
                    <option value="Withdrawn">Withdrawn</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300">Institution Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. National Institute of Technology Delhi"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2 px-3 text-xs text-white focus:border-[#F28C28] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300">Campus Address *</label>
                <input
                  type="text"
                  required
                  placeholder="Street, Sector, Area"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  className="mt-1 w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2 px-3 text-xs text-white focus:border-[#F28C28] focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300">City *</label>
                  <input
                    type="text"
                    required
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                    className="mt-1 w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2 px-3 text-xs text-white focus:border-[#F28C28] focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300">State *</label>
                  <input
                    type="text"
                    required
                    value={formData.state}
                    onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                    className="mt-1 w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2 px-3 text-xs text-white focus:border-[#F28C28] focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300">Pincode *</label>
                  <input
                    type="text"
                    required
                    value={formData.pincode}
                    onChange={(e) => setFormData({ ...formData, pincode: e.target.value })}
                    className="mt-1 w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2 px-3 text-xs text-white font-mono focus:border-[#F28C28] focus:outline-none"
                  />
                </div>
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
                  disabled={creating}
                  className="rounded-lg bg-gradient-to-r from-[#F28C28] to-[#D97706] px-5 py-2 text-xs font-bold text-white shadow hover:from-[#FFA94D] disabled:opacity-50"
                >
                  {creating ? "Submitting..." : "Save Record"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

