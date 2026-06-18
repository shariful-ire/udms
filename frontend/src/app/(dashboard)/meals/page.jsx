"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { mealsApi, diningApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { getErrorMessage, formatDate } from "@/lib/utils";
import { MEAL_TYPES } from "@/lib/constants";
import { PageContainer, PageLoader } from "@/components/shared/LoadingSpinner";
import { PageHeader } from "@/components/layout/PageHeader";
import { TodayMealCard } from "@/components/meals/TodayMealCard";

export default function MealsPage() {
  const qc = useQueryClient();
  const today = new Date().toISOString().split("T")[0];

  const { data: todayData, isLoading } = useQuery({
    queryKey: queryKeys.meals.today,
    queryFn: () => mealsApi.today().then((r) => r.data.data),
  });

  const { data: schedulesData } = useQuery({
    queryKey: queryKeys.dining.schedules,
    queryFn: () => diningApi.getSchedules().then((r) => r.data.data),
  });

  const addMutation = useMutation({
    mutationFn: (meal_type) => mealsApi.add({ meal_type, date: today }),
    onSuccess: (_, meal_type) => {
      toast.success(`${meal_type.charAt(0) + meal_type.slice(1).toLowerCase()} added!`);
      qc.invalidateQueries({ queryKey: queryKeys.meals.today });
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const cancelMutation = useMutation({
    mutationFn: (id) => mealsApi.cancel(id),
    onSuccess: () => {
      toast.success("Meal cancelled");
      qc.invalidateQueries({ queryKey: queryKeys.meals.today });
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  if (isLoading) return <PageLoader />;

  // todayData is TodayMealStatus[] — flat array with schedule+meal embedded per type
  const statusMap = {};
  todayData?.forEach((item) => { statusMap[item.meal_type] = item; });

  // Fall back to separate schedules query if todayData doesn't have it
  const scheduleMap = {};
  schedulesData?.forEach((s) => { scheduleMap[s.meal_type] = s; });

  return (
    <PageContainer>
      <PageHeader
        title="Today's Meals"
        description={`${formatDate(today)} — Add or cancel your meals before the deadline`}
      />

      <div className="grid gap-4 sm:grid-cols-3">
        {MEAL_TYPES.map((mealType) => (
          <TodayMealCard
            key={mealType}
            mealType={mealType}
            schedule={statusMap[mealType]?.schedule ?? scheduleMap[mealType]}
            studentMeal={statusMap[mealType]?.meal ?? null}
            onAdd={(type) => addMutation.mutate(type)}
            onCancel={(id) => cancelMutation.mutate(id)}
            isAddLoading={addMutation.isPending && addMutation.variables === mealType}
            isCancelLoading={cancelMutation.isPending && cancelMutation.variables === statusMap[mealType]?.meal?.id}
          />
        ))}
      </div>

      {/* Monthly summary strip */}
      <div className="rounded-xl border bg-card p-5">
        <h3 className="text-sm font-semibold mb-3">This Month</h3>
        <div className="grid grid-cols-3 gap-4 text-center">
          {MEAL_TYPES.map((type) => (
            <div key={type}>
              <p className="text-2xl font-bold text-primary">
                {statusMap[type]?.meal?.status === "ACTIVE" ? "✓" : "—"}
              </p>
              <p className="text-xs text-muted-foreground mt-0.5">{type.charAt(0) + type.slice(1).toLowerCase()}</p>
            </div>
          ))}
        </div>
      </div>
    </PageContainer>
  );
}
