"use client";

import { useState } from "react";
import { Clock, CheckCircle2, XCircle, Loader2, UtensilsCrossed } from "lucide-react";
import { cn, formatTime, formatDate } from "@/lib/utils";
import { MEAL_TYPE_LABELS, MEAL_TYPE_COLORS, MEAL_TYPE_ICONS } from "@/lib/constants";
import { StatusBadge } from "@/components/shared/Badge";
import { EmptyState } from "@/components/shared/LoadingSpinner";

// ── TodayMealCard ─────────────────────────────────────────────────────────────
export function TodayMealCard({
  mealType,
  schedule,
  studentMeal,
  onAdd,
  onCancel,
  isAddLoading,
  isCancelLoading,
}) {
  const label = MEAL_TYPE_LABELS[mealType];
  const icon = MEAL_TYPE_ICONS[mealType];
  const colorClass = MEAL_TYPE_COLORS[mealType];
  const isAdded = !!studentMeal;
  const now = new Date();

  // Compute deadline
  const isDeadlinePast = (() => {
    if (!schedule?.cancel_deadline) return false;
    const [h, m] = schedule.cancel_deadline.split(":").map(Number);
    const deadline = new Date();
    deadline.setHours(h, m, 0, 0);
    return now > deadline;
  })();

  const isAvailable = schedule?.is_active && !isDeadlinePast;

  return (
    <div className={cn("rounded-xl border p-5 space-y-4 transition-all", colorClass)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <span className="text-2xl" role="img" aria-label={label}>{icon}</span>
          <div>
            <h3 className="font-semibold text-sm">{label}</h3>
            {schedule && (
              <p className="text-xs text-muted-foreground">
                {formatTime(schedule.start_time)} — {formatTime(schedule.end_time)}
              </p>
            )}
          </div>
        </div>

        {/* Status indicator */}
        {isAdded ? (
          <span className="flex items-center gap-1 text-xs font-medium text-green-600 dark:text-green-400">
            <CheckCircle2 className="h-3.5 w-3.5" />
            Added
          </span>
        ) : isDeadlinePast ? (
          <span className="flex items-center gap-1 text-xs text-muted-foreground">
            <Clock className="h-3.5 w-3.5" />
            Closed
          </span>
        ) : (
          <span className="flex items-center gap-1 text-xs text-muted-foreground">
            <Clock className="h-3.5 w-3.5" />
            Deadline: {formatTime(schedule?.cancel_deadline)}
          </span>
        )}
      </div>

      {/* Menu items */}
      {schedule?.menu_items?.length > 0 && (
        <ul className="space-y-0.5">
          {schedule.menu_items.map((item, i) => (
            <li key={i} className="text-sm text-foreground/80 flex items-center gap-1.5">
              <span className="h-1 w-1 rounded-full bg-foreground/40 shrink-0" />
              {item}
            </li>
          ))}
        </ul>
      )}

      {/* Action button */}
      {isAdded ? (
        <button
          onClick={() => onCancel(studentMeal.id)}
          disabled={isCancelLoading || isDeadlinePast}
          className="w-full rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-xs font-medium text-destructive
            hover:bg-destructive/20 disabled:opacity-50 disabled:cursor-not-allowed
            flex items-center justify-center gap-1.5 transition-colors"
        >
          {isCancelLoading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <XCircle className="h-3.5 w-3.5" />}
          {isCancelLoading ? "Cancelling…" : "Cancel meal"}
        </button>
      ) : (
        <button
          onClick={() => onAdd(mealType)}
          disabled={isAddLoading || !isAvailable}
          className="w-full rounded-lg bg-primary px-3 py-2 text-xs font-medium text-primary-foreground
            hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed
            flex items-center justify-center gap-1.5 transition-colors"
        >
          {isAddLoading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : null}
          {isAddLoading
            ? "Adding…"
            : !isAvailable
            ? isDeadlinePast
              ? "Deadline passed"
              : "Not available"
            : "Add meal"}
        </button>
      )}
    </div>
  );
}

// ── MealHistoryTable ──────────────────────────────────────────────────────────
export function MealHistoryTable({ data = [], isLoading }) {
  if (!data.length && !isLoading) {
    return (
      <EmptyState
        icon={UtensilsCrossed}
        title="No meal history"
        description="Your meal records will appear here."
      />
    );
  }

  return (
    <div className="rounded-xl border overflow-hidden">
      <table className="data-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Meal Type</th>
            <th>Status</th>
            <th>Cancelled By</th>
            <th>Cancelled At</th>
          </tr>
        </thead>
        <tbody>
          {data.map((meal) => (
            <tr key={meal.id}>
              <td className="font-medium">{formatDate(meal.date)}</td>
              <td>
                <span className="flex items-center gap-1.5">
                  <span>{MEAL_TYPE_ICONS[meal.meal_type]}</span>
                  {MEAL_TYPE_LABELS[meal.meal_type]}
                </span>
              </td>
              <td>
                <span className={cn(
                  "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
                  meal.status === "ACTIVE"
                    ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                    : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                )}>
                  {meal.status === "ACTIVE" ? "Attended" : "Cancelled"}
                </span>
              </td>
              <td className="text-muted-foreground text-sm">
                {meal.cancelled_by_name ?? "—"}
              </td>
              <td className="text-muted-foreground text-sm">
                {meal.cancelled_at ? formatDate(meal.cancelled_at) : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TodayMealCard;
