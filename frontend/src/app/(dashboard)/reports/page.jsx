"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Download } from "lucide-react";
import { reportsApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { formatCurrency } from "@/lib/utils";
import { EXPENSE_CATEGORIES } from "@/lib/constants";
import { PageContainer, SkeletonCard } from "@/components/shared/LoadingSpinner";
import { PageHeader } from "@/components/layout/PageHeader";
import { IncomeExpenseChart } from "@/components/charts/ExpensePieChart";
import { ExpensePieChart } from "@/components/charts/ExpensePieChart";

const PERIODS = ["daily","weekly","monthly","yearly"];

export default function ReportsPage() {
  const now = new Date();
  const [period, setPeriod] = useState("monthly");
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);

  const queryFn = {
    daily: () => reportsApi.daily({ report_date: `${year}-${String(month).padStart(2,"0")}-01` }),
    weekly: () => reportsApi.weekly({ year, month }),
    monthly: () => reportsApi.monthly({ year, month }),
    yearly: () => reportsApi.yearly({ year }),
  }[period];

  const queryKey = {
    daily: queryKeys.reports.daily({ year, month }),
    weekly: queryKeys.reports.weekly({ year, month }),
    monthly: queryKeys.reports.monthly({ year, month }),
    yearly: queryKeys.reports.yearly({ year }),
  }[period];

  const { data, isLoading } = useQuery({
    queryKey,
    queryFn: () => queryFn().then((r) => r.data.data),
  });

  const handleExport = async () => {
    try {
      const res = await reportsApi.export({ period, year, month });
      const url = URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `report_${period}_${year}_${month}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch { /* silent */ }
  };

  const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const YEARS = Array.from({ length: 5 }, (_, i) => now.getFullYear() - i);

  const stats = [
    { label: "Total Income", value: formatCurrency(data?.total_income ?? 0) },
    { label: "Total Expenses", value: formatCurrency(data?.total_expense ?? 0) },
    { label: "Net Balance", value: formatCurrency((data?.total_income ?? 0) - (data?.total_expense ?? 0)) },
    { label: "Total Meals", value: data?.total_meals ?? 0 },
  ];

  return (
    <PageContainer>
      <PageHeader
        title="Reports"
        description="Financial and operational reports"
        action={
          <button onClick={handleExport}
            className="flex items-center gap-1.5 rounded-lg border border-input px-4 py-2 text-sm font-medium hover:bg-accent transition-colors">
            <Download className="h-4 w-4" /> Export CSV
          </button>
        }
      />

      {/* Controls */}
      <div className="flex flex-wrap gap-3">
        <div className="flex rounded-lg border overflow-hidden">
          {PERIODS.map((p) => (
            <button key={p} onClick={() => setPeriod(p)}
              className={`px-4 py-2 text-sm font-medium capitalize transition-colors ${period === p ? "bg-primary text-primary-foreground" : "hover:bg-accent"}`}>
              {p}
            </button>
          ))}
        </div>
        {period !== "daily" && (
          <select value={month} onChange={(e) => setMonth(Number(e.target.value))}
            className="rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring">
            {MONTHS.map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
          </select>
        )}
        <select value={year} onChange={(e) => setYear(Number(e.target.value))}
          className="rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring">
          {YEARS.map((y) => <option key={y} value={y}>{y}</option>)}
        </select>
      </div>

      {/* Summary cards */}
      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-4">{Array.from({length:4}).map((_,i) => <SkeletonCard key={i} />)}</div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map(({ label, value }) => (
            <div key={label} className="rounded-xl border bg-card p-5">
              <p className="text-xs text-muted-foreground">{label}</p>
              <p className="text-xl font-bold mt-1">{value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border bg-card p-5">
          <h3 className="text-sm font-semibold mb-4">Income vs Expenses</h3>
          <IncomeExpenseChart data={data?.breakdown ?? []} />
        </div>
        <div className="rounded-xl border bg-card p-5">
          <h3 className="text-sm font-semibold mb-4">Expenses by Category</h3>
          <ExpensePieChart data={data?.expense_by_category ?? []} />
        </div>
      </div>
    </PageContainer>
  );
}
