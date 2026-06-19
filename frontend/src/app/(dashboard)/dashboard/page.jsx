"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Users, UtensilsCrossed, CreditCard, ClipboardList,
  TrendingUp, UserCheck, Wallet, Calculator, Calendar,
} from "lucide-react";
import Link from "next/link";
import { usersApi, mealsApi, requestsApi, reportsApi, auditApi, dashboardApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { useAuthStore } from "@/store/authStore";
import { usePermissions } from "@/lib/hooks/usePermissions";
import { PageContainer, SkeletonCard } from "@/components/shared/LoadingSpinner";
import { StatCard } from "@/components/dashboard/StatCard";
import { WelcomeBanner } from "@/components/dashboard/WelcomeBanner";
import { RecentActivity } from "@/components/dashboard/RecentActivity";
import { MealTrendChart } from "@/components/charts/ExpensePieChart";
import { formatCurrency, formatDate, formatTime, titleCase } from "@/lib/utils";
import { MEAL_TYPE_LABELS, MEAL_TYPE_ICONS, REQUEST_STATUS_LABELS, REQUEST_STATUS_COLORS } from "@/lib/constants";

// ── Provost / Dining Manager Dashboard ────────────────────────────────────────
function ManagerDashboard() {
  const now = new Date();

  const { data: userStats, isLoading: loadingStats } = useQuery({
    queryKey: queryKeys.users.stats,
    queryFn: () => usersApi.stats().then((r) => r.data.data),
  });

  const { data: report, isLoading: loadingReport } = useQuery({
    queryKey: queryKeys.reports.monthly({ year: now.getFullYear(), month: now.getMonth() + 1 }),
    queryFn: () =>
      reportsApi.monthly({ year: now.getFullYear(), month: now.getMonth() + 1 }).then((r) => r.data.data),
  });

  const { data: dashStats, isLoading: loadingDash } = useQuery({
    queryKey: queryKeys.dashboard.stats,
    queryFn: () => dashboardApi.stats().then((r) => r.data.data),
  });

  const { data: auditData, isLoading: loadingAudit } = useQuery({
    queryKey: ["audit", "recent"],
    queryFn: () => auditApi.list({ per_page: 8 }).then((r) => r.data),
  });

  const totalEarnings = dashStats?.total_earnings ?? report?.total_income ?? 0;
  const totalExpenses = dashStats?.total_expenses ?? report?.total_expense ?? 0;

  const stats = [
    {
      title: "Total Users",
      value: userStats?.total_users ?? 0,
      href: "/users",
      icon: <Users className="h-5 w-5" />,
      iconColor: "bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400",
    },
    {
      title: "Active Customers",
      value: dashStats?.active_customers ?? userStats?.total_customers ?? 0,
      href: "/payments",
      icon: <UserCheck className="h-5 w-5" />,
      iconColor: "bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400",
    },
    {
      title: "Total Earnings",
      formatted: formatCurrency(totalEarnings),
      value: Math.round(Number(totalEarnings)),
      href: "/earnings",
      icon: <TrendingUp className="h-5 w-5" />,
      iconColor: "bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400",
    },
    {
      title: "Total Expenses",
      formatted: formatCurrency(totalExpenses),
      value: Math.round(Number(totalExpenses)),
      href: "/expenses",
      icon: <CreditCard className="h-5 w-5" />,
      iconColor: "bg-rose-100 text-rose-600 dark:bg-rose-900/30 dark:text-rose-400",
    },
  ];

  const activityItems = (auditData?.data ?? []).map((log) => ({
    id: log.id,
    actor_name: log.actor_name ?? "System",
    action: titleCase(log.action),
    detail: log.entity_type,
    created_at: log.created_at,
  }));

  const session = dashStats?.session;
  const netBalance = dashStats?.net_balance ?? (totalEarnings - totalExpenses);

  return (
    <div className="space-y-6">
      <WelcomeBanner />

      {/* Stat cards */}
      {loadingStats && loadingReport && loadingDash ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((s) => <StatCard key={s.title} {...s} />)}
        </div>
      )}

      {/* Net Balance + Meal Session */}
      {(dashStats || report) && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Link href="/reports" className="rounded-xl border bg-card p-5 hover:border-primary/30 transition-colors block">
            <div className="flex items-center gap-2 mb-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-100 text-violet-600 dark:bg-violet-900/30 dark:text-violet-400">
                <Wallet className="h-4 w-4" />
              </div>
              <p className="text-sm font-medium text-muted-foreground">Net Balance</p>
            </div>
            <p className={`text-2xl font-bold ${netBalance >= 0 ? "text-green-600" : "text-red-600"}`}>
              {formatCurrency(netBalance)}
            </p>
            <p className="text-xs text-muted-foreground mt-0.5">earnings - expenses</p>
          </Link>

          <Link href="/reports" className="rounded-xl border bg-card p-5 hover:border-primary/30 transition-colors block">
            <div className="flex items-center gap-2 mb-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400">
                <Calculator className="h-4 w-4" />
              </div>
              <p className="text-sm font-medium text-muted-foreground">Per Meal Cost</p>
            </div>
            <p className="text-2xl font-bold">
              {formatCurrency(session?.per_meal_cost ?? report?.per_meal_cost ?? 0)}
            </p>
            <p className="text-xs text-muted-foreground mt-0.5">this week&apos;s session</p>
          </Link>

          <Link href="/meals" className="rounded-xl border bg-card p-5 hover:border-primary/30 transition-colors block">
            <div className="flex items-center gap-2 mb-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-cyan-100 text-cyan-600 dark:bg-cyan-900/30 dark:text-cyan-400">
                <UtensilsCrossed className="h-4 w-4" />
              </div>
              <p className="text-sm font-medium text-muted-foreground">Meals Consumed</p>
            </div>
            <p className="text-2xl font-bold">
              {session?.consumed_meals ?? report?.total_meals ?? 0}
              {session && (
                <span className="text-sm font-normal text-muted-foreground ml-1">
                  / {session.total_possible_meals}
                </span>
              )}
            </p>
            <p className="text-xs text-muted-foreground mt-0.5">
              {session ? `${session.remaining_meals} remaining` : "this month"}
            </p>
          </Link>

          <Link href="/reports" className="rounded-xl border bg-card p-5 hover:border-primary/30 transition-colors block">
            <div className="flex items-center gap-2 mb-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-pink-100 text-pink-600 dark:bg-pink-900/30 dark:text-pink-400">
                <Calendar className="h-4 w-4" />
              </div>
              <p className="text-sm font-medium text-muted-foreground">Remaining Cost</p>
            </div>
            <p className="text-2xl font-bold">
              {formatCurrency(session?.remaining_cost ?? 0)}
            </p>
            <p className="text-xs text-muted-foreground mt-0.5">
              {session ? `${session.start_date} — ${session.end_date}` : "current period"}
            </p>
          </Link>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Meal trend */}
        <div className="lg:col-span-2 rounded-xl border bg-card p-5">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-sm font-semibold">Meals This Month</h3>
            <Link href="/reports" className="text-xs text-primary hover:underline underline-offset-4">
              Full report →
            </Link>
          </div>
          {loadingReport ? (
            <div className="h-64 flex items-center justify-center text-sm text-muted-foreground">Loading…</div>
          ) : (
            <MealTrendChart data={report?.daily_breakdown ?? []} />
          )}
        </div>

        {/* Recent activity */}
        <RecentActivity items={activityItems} isLoading={loadingAudit} />
      </div>

      {/* Quick links */}
      <div className="grid gap-3 sm:grid-cols-4">
        {[
          { href: "/users", label: "Manage Users", icon: <Users className="h-4 w-4" /> },
          { href: "/requests", label: "Review Requests", icon: <ClipboardList className="h-4 w-4" /> },
          { href: "/expenses", label: "Log Expenses", icon: <CreditCard className="h-4 w-4" /> },
          { href: "/earnings", label: "Log Earnings", icon: <TrendingUp className="h-4 w-4" /> },
        ].map((link) => (
          <Link key={link.href} href={link.href}
            className="flex items-center gap-3 rounded-xl border bg-card px-4 py-3.5 text-sm font-medium
              hover:bg-accent transition-colors">
            <span className="text-muted-foreground">{link.icon}</span>
            {link.label}
          </Link>
        ))}
      </div>
    </div>
  );
}

// ── Customer Dashboard ────────────────────────────────────────────────────────
function CustomerDashboard() {
  const now = new Date();

  const { data: todayMeals, isLoading: loadingToday } = useQuery({
    queryKey: queryKeys.meals.today,
    queryFn: () => mealsApi.today().then((r) => r.data.data),
  });

  const { data: summary, isLoading: loadingSummary } = useQuery({
    queryKey: queryKeys.meals.summary({ year: now.getFullYear(), month: now.getMonth() + 1 }),
    queryFn: () =>
      mealsApi.summary({ year: now.getFullYear(), month: now.getMonth() + 1 }).then((r) => r.data.data),
  });

  const totalMeals = summary
    ? (summary.breakdown?.BREAKFAST ?? 0) + (summary.breakdown?.LUNCH ?? 0) + (summary.breakdown?.DINNER ?? 0)
    : 0;

  return (
    <div className="space-y-6">
      <WelcomeBanner />

      {/* Monthly summary cards */}
      <div className="grid gap-4 sm:grid-cols-4">
        {loadingSummary ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
        ) : (
          <>
            {["BREAKFAST", "LUNCH", "DINNER"].map((t) => (
              <div key={t} className="rounded-xl border bg-card p-5">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-lg">{MEAL_TYPE_ICONS[t]}</span>
                  <p className="text-sm font-medium text-muted-foreground">{MEAL_TYPE_LABELS[t]}</p>
                </div>
                <p className="text-2xl font-semibold">{summary?.breakdown?.[t] ?? 0}</p>
                <p className="text-xs text-muted-foreground mt-0.5">meals this month</p>
              </div>
            ))}
            <div className="rounded-xl border bg-card p-5">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">📊</span>
                <p className="text-sm font-medium text-muted-foreground">Total</p>
              </div>
              <p className="text-2xl font-semibold">{totalMeals}</p>
              <p className="text-xs text-muted-foreground mt-0.5">meals this month</p>
            </div>
          </>
        )}
      </div>

      {/* Today's meals */}
      <div className="rounded-xl border bg-card p-5">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-sm font-semibold">Today&apos;s Meals</h3>
          <Link href="/meals" className="text-xs text-primary hover:underline underline-offset-4">
            Manage →
          </Link>
        </div>
        {loadingToday ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-16 rounded-lg bg-muted animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {(todayMeals ?? []).map((item) => (
              <div key={item.meal_type}
                className="flex items-center justify-between rounded-lg border px-4 py-3">
                <div className="flex items-center gap-3">
                  <span className="text-lg">{MEAL_TYPE_ICONS[item.meal_type]}</span>
                  <div>
                    <p className="text-sm font-medium">{MEAL_TYPE_LABELS[item.meal_type]}</p>
                    {item.schedule && (
                      <p className="text-xs text-muted-foreground">
                        {formatTime(item.schedule.start_time)} – {formatTime(item.schedule.end_time)}
                      </p>
                    )}
                  </div>
                </div>
                <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
                  item.meal?.status === "ACTIVE"
                    ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                    : item.is_cancelled_by_manager
                    ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                    : "bg-gray-100 text-gray-600 dark:bg-gray-900/30 dark:text-gray-400"
                }`}>
                  {item.meal?.status === "ACTIVE"
                    ? "Enrolled"
                    : item.is_cancelled_by_manager
                    ? "Cancelled"
                    : "Not enrolled"}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ── Non-Customer Dashboard ────────────────────────────────────────────────────
function NonCustomerDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: queryKeys.requests.list({}),
    queryFn: () => requestsApi.list({ per_page: 5 }).then((r) => r.data),
  });

  const requests = data?.data ?? [];

  return (
    <div className="space-y-6">
      <WelcomeBanner />

      <div className="rounded-xl border bg-card p-5">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-sm font-semibold">My Requests</h3>
          <Link href="/requests" className="text-xs text-primary hover:underline underline-offset-4">
            View all →
          </Link>
        </div>

        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-12 rounded-lg bg-muted animate-pulse" />
            ))}
          </div>
        ) : requests.length === 0 ? (
          <div className="py-8 text-center">
            <UtensilsCrossed className="mx-auto h-8 w-8 text-muted-foreground mb-3" />
            <p className="text-sm text-muted-foreground">No requests yet.</p>
            <Link href="/requests"
              className="mt-3 inline-flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors">
              Submit a request
            </Link>
          </div>
        ) : (
          <div className="space-y-2">
            {requests.map((r) => (
              <Link key={r.id} href={`/requests/${r.id}`}
                className="flex items-center justify-between rounded-lg border px-4 py-3 hover:bg-accent transition-colors">
                <div>
                  <p className="text-sm font-medium">
                    {MEAL_TYPE_LABELS[r.meal_type]} — {formatDate(r.date)}
                  </p>
                  <p className="text-xs text-muted-foreground">{formatDate(r.created_at)}</p>
                </div>
                <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${REQUEST_STATUS_COLORS[r.status] ?? ""}`}>
                  {REQUEST_STATUS_LABELS[r.status] ?? r.status}
                </span>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Info card */}
      <div className="rounded-xl border bg-muted/30 p-5 text-sm text-muted-foreground space-y-1.5">
        <p className="font-medium text-foreground">How to enroll in dining</p>
        <ol className="list-decimal list-inside space-y-1">
          <li>Submit a meal request for the date you need</li>
          <li>Complete the payment via the request details page</li>
          <li>Wait for the dining manager to approve your request</li>
          <li>Once approved, your meal will be enrolled for that date</li>
        </ol>
      </div>
    </div>
  );
}

// ── Root ──────────────────────────────────────────────────────────────────────
export default function DashboardPage() {
  const { isManager, isProvost, isCustomer } = usePermissions();

  if (isProvost || isManager) return <PageContainer><ManagerDashboard /></PageContainer>;
  if (isCustomer) return <PageContainer><CustomerDashboard /></PageContainer>;
  return <PageContainer><NonCustomerDashboard /></PageContainer>;
}
