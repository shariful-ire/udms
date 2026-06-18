"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { mealsApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { PageContainer, SkeletonCard } from "@/components/shared/LoadingSpinner";
import { PageHeader } from "@/components/layout/PageHeader";
import { MealTrendChart } from "@/components/charts/ExpensePieChart";
import { MEAL_TYPES, MEAL_TYPE_LABELS, MEAL_TYPE_ICONS } from "@/lib/constants";
import { formatCurrency } from "@/lib/utils";

export default function MealSummaryPage() {
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.meals.summary({ year, month }),
    queryFn: () => mealsApi.summary({ year, month }).then((r) => r.data.data),
  });

  const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const YEARS = Array.from({ length: 5 }, (_, i) => now.getFullYear() - i);

  return (
    <PageContainer>
      <PageHeader title="Meal Summary" description="Monthly overview of your meal consumption" />

      <div className="flex gap-3">
        <select value={month} onChange={(e) => setMonth(Number(e.target.value))}
          className="rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring">
          {MONTHS.map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
        </select>
        <select value={year} onChange={(e) => setYear(Number(e.target.value))}
          className="rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring">
          {YEARS.map((y) => <option key={y} value={y}>{y}</option>)}
        </select>
      </div>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-3"><SkeletonCard /><SkeletonCard /><SkeletonCard /></div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            {MEAL_TYPES.map((type) => {
              const count = data?.by_type?.[type.toLowerCase()] ?? 0;
              return (
                <div key={type} className="rounded-xl border bg-card p-5 text-center">
                  <div className="text-3xl mb-2">{MEAL_TYPE_ICONS[type]}</div>
                  <p className="text-2xl font-bold">{count}</p>
                  <p className="text-sm text-muted-foreground mt-0.5">{MEAL_TYPE_LABELS[type]}</p>
                </div>
              );
            })}
          </div>

          <div className="rounded-xl border bg-card p-5">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold">Total meals this month</h3>
              <span className="text-2xl font-bold text-primary">{data?.total ?? 0}</span>
            </div>
            {data?.meal_rate && (
              <p className="text-sm text-muted-foreground">
                Estimated cost: <span className="font-semibold text-foreground">{formatCurrency(data.total * (data.meal_rate / 30))}</span>
              </p>
            )}
          </div>

          {data?.trend?.length > 0 && (
            <div className="rounded-xl border bg-card p-5">
              <h3 className="text-sm font-semibold mb-4">Daily breakdown</h3>
              <MealTrendChart data={data.trend} />
            </div>
          )}
        </>
      )}
    </PageContainer>
  );
}
