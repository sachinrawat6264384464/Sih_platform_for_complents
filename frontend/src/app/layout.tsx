"use client";

import React from "react";
import "./globals.css";
import { ThemeProvider } from "@/lib/theme";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { WaterCursor } from "@/components/ui/WaterCursor";
import { CloudBackground } from "@/components/ui/CloudBackground";
import { CommandPalette } from "@/components/ui/CommandPalette";
import { Sidebar } from "@/components/ui/Sidebar";
import { Header } from "@/components/ui/Header";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 30,
      retry: 1,
    },
  },
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body
        suppressHydrationWarning
        className="min-h-screen bg-[#0B1730] text-slate-100 antialiased selection:bg-[#F28C28] selection:text-white"
      >
        <QueryClientProvider client={queryClient}>
          <ThemeProvider>
            <CloudBackground />
            <WaterCursor />
            <CommandPalette />
            <div className="relative z-10 flex min-h-screen">
              <Sidebar />
              <div className="flex flex-1 flex-col overflow-x-hidden">
                <Header />
                <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto">
                  {children}
                </main>
              </div>
            </div>
          </ThemeProvider>
        </QueryClientProvider>
      </body>
    </html>
  );
}

