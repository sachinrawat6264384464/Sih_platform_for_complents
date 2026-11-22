"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Lock, User as UserIcon, Shield, AlertCircle, ArrowRight } from "lucide-react";

export default function LoginPage() {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("AicteNexus@2026SecureAdmin");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await api.post("/auth/login", {
        username_or_email: username,
        password: password,
      });

      const { access_token, user } = res.data;
      localStorage.setItem("aicte_nexus_token", access_token);
      localStorage.setItem("aicte_nexus_user", JSON.stringify(user));

      router.push("/");
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Authentication failed. Please verify credentials with Bureau Security Officer."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center p-4">
      <div className="relative z-10 w-full max-w-md overflow-hidden rounded-2xl border border-slate-700/80 bg-[#14233D]/95 p-8 shadow-2xl backdrop-blur-xl">
        {/* National Council Emblem & Title */}
        <div className="text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-tr from-[#F28C28] to-[#D97706] text-white shadow-xl shadow-orange-500/20">
            <Shield className="h-8 w-8 text-white" />
          </div>
          <h1 className="mt-4 text-2xl font-black tracking-tight text-white">
            AICTE NEXUS
          </h1>
          <p className="mt-1 text-xs text-slate-300">
            All India Council for Technical Education
          </p>
          <div className="mt-2 inline-flex items-center rounded-full bg-[#1E355B] px-3 py-1 text-[11px] font-medium text-cyan-400">
            Regulation Bureau & PGRC Secure Gateway
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mt-6 flex items-start rounded-lg border border-red-500/30 bg-red-950/40 p-3 text-xs text-red-300">
            <AlertCircle className="mr-2 h-4 w-4 flex-shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleLogin} className="mt-6 space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
              Official Username / Email
            </label>
            <div className="relative mt-1.5">
              <UserIcon className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2.5 pl-10 pr-4 text-sm text-white placeholder-slate-500 focus:border-[#F28C28] focus:outline-none focus:ring-1 focus:ring-[#F28C28]"
                placeholder="Enter AICTE officer ID"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
              Security Credential
            </label>
            <div className="relative mt-1.5">
              <Lock className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full rounded-lg border border-slate-700 bg-[#0B1730] py-2.5 pl-10 pr-4 text-sm text-white placeholder-slate-500 focus:border-[#F28C28] focus:outline-none focus:ring-1 focus:ring-[#F28C28]"
                placeholder="••••••••••••••••"
              />
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center rounded-lg bg-gradient-to-r from-[#F28C28] to-[#D97706] py-3 text-sm font-bold text-white shadow-lg shadow-orange-500/20 hover:from-[#FFA94D] hover:to-[#F28C28] transition-all disabled:opacity-50"
            >
              {loading ? (
                <span>Authenticating Officer...</span>
              ) : (
                <>
                  <span>Sign In To Bureau Nexus</span>
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </button>
          </div>
        </form>

        {/* Security Notice */}
        <div className="mt-8 border-t border-slate-800 pt-4 text-center text-[11px] text-slate-500">
          Authorized Government Personnel Only. All session activities and IP addresses are cryptographically logged for audit compliance under IT Redressal Standards.
        </div>
      </div>
    </div>
  );
}
