"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { useAuthStore } from "@/store/authStore";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";

export default function DashboardLayout({ children }) {
  const router = useRouter();
  const { isHydrated, user, accessToken } = useAuthStore();

  useEffect(() => {
    if (isHydrated && (!user || !accessToken)) {
      router.replace("/login");
    }
  }, [isHydrated, user, accessToken, router]);

  if (!isHydrated) {
    return (
      <div className="flex h-screen items-center justify-center">
        <LoadingSpinner size="lg" label="Loading…" />
      </div>
    );
  }

  if (!user || !accessToken) {
    return (
      <div className="flex h-screen items-center justify-center">
        <LoadingSpinner size="lg" label="Redirecting…" />
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Topbar />
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
