"use client";

import { useMemo } from "react";
import { useAuthStore } from "@/store/authStore";
import { ROLE_LABELS } from "@/lib/constants";
import { cn } from "@/lib/utils";

function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

export function WelcomeBanner({ className }) {
  const user = useAuthStore((s) => s.user);
  const greeting = useMemo(getGreeting, []);
  const firstName = user?.full_name?.split(" ")[0] ?? "there";
  const roleLabel = ROLE_LABELS[user?.role] ?? "User";

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-xl border bg-gradient-to-r from-primary to-[hsl(var(--brand-secondary))] p-6 text-primary-foreground",
        className
      )}
    >
      {/* Background decoration */}
      <div className="pointer-events-none absolute right-0 top-0 h-full w-1/3 opacity-10">
        <div className="absolute right-[-20%] top-[-20%] h-64 w-64 rounded-full bg-white" />
        <div className="absolute right-[10%] bottom-[-30%] h-48 w-48 rounded-full bg-white" />
      </div>

      <div className="relative space-y-1">
        <p className="text-sm font-medium text-primary-foreground/80">{roleLabel}</p>
        <h2 className="text-xl font-semibold">
          {greeting}, {firstName}! 👋
        </h2>
        <p className="text-sm text-primary-foreground/70">
          {new Date().toLocaleDateString("en-US", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
          })}
        </p>
      </div>
    </div>
  );
}

export default WelcomeBanner;
