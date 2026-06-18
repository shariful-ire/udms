"use client";
// Meal History Page
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { mealsApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { usePagination } from "@/lib/hooks/usePagination";
import { MEAL_TYPES, MEAL_TYPE_LABELS } from "@/lib/constants";
import { PageContainer, SkeletonTable } from "@/components/shared/LoadingSpinner";
import { PageHeader } from "@/components/layout/PageHeader";
import { MealHistoryTable } from "@/components/meals/TodayMealCard";
import { Pagination } from "@/components/tables/Pagination";
import { DateRangePicker } from "@/components/shared/SearchInput";

export default function MealHistoryPage() {
  const { page, perPage, params, setPage, setPerPage } = usePagination();
  const [mealType, setMealType] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const qParams = { ...params, meal_type: mealType, start_date: startDate, end_date: endDate };

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.meals.history(qParams),
    queryFn: () => mealsApi.history(qParams).then((r) => r.data),
  });

  return (
    <PageContainer>
      <PageHeader title="Meal History" description="All your past meal records" />
      <div className="flex flex-wrap gap-3">
        <select value={mealType} onChange={(e) => { setMealType(e.target.value); setPage(1); }}
          className="rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring">
          <option value="">All Meal Types</option>
          {MEAL_TYPES.map((t) => <option key={t} value={t}>{MEAL_TYPE_LABELS[t]}</option>)}
        </select>
        <DateRangePicker startDate={startDate} endDate={endDate} onStartChange={(v) => { setStartDate(v); setPage(1); }} onEndChange={(v) => { setEndDate(v); setPage(1); }} />
      </div>
      {isLoading ? <SkeletonTable rows={8} cols={5} /> : (
        <>
          <MealHistoryTable data={data?.data ?? []} />
          <Pagination meta={data?.meta} page={page} perPage={perPage} setPage={setPage} setPerPage={setPerPage} />
        </>
      )}
    </PageContainer>
  );
}
