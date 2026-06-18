"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { diningApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { MEAL_TYPES, MEAL_TYPE_LABELS, MEAL_TYPE_ICONS } from "@/lib/constants";
import { formatTime, getErrorMessage } from "@/lib/utils";
import { PageContainer, PageLoader } from "@/components/shared/LoadingSpinner";
import { PageHeader } from "@/components/layout/PageHeader";
import { Loader2, Clock } from "lucide-react";

const inputCls = "w-full rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring transition-shadow [color-scheme:light] dark:[color-scheme:dark]";

function ScheduleCard({ schedule, mealType, onSave }) {
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({
    start_time: schedule?.start_time ?? "",
    end_time: schedule?.end_time ?? "",
    cancel_deadline: schedule?.cancel_deadline ?? "",
    is_active: schedule?.is_active ?? true,
  });
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try { await onSave(mealType, form); setEditing(false); }
    finally { setSaving(false); }
  };

  return (
    <div className="rounded-xl border bg-card p-5 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <span className="text-2xl">{MEAL_TYPE_ICONS[mealType]}</span>
          <h3 className="font-semibold">{MEAL_TYPE_LABELS[mealType]}</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className={`h-2 w-2 rounded-full ${schedule?.is_active ? "bg-green-500" : "bg-muted-foreground"}`} />
          <span className="text-xs text-muted-foreground">{schedule?.is_active ? "Active" : "Inactive"}</span>
        </div>
      </div>

      {!editing ? (
        <>
          <div className="space-y-2 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground flex items-center gap-1.5"><Clock className="h-3.5 w-3.5" />Serving hours</span>
              <span className="font-medium">{formatTime(schedule?.start_time)} — {formatTime(schedule?.end_time)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Add/cancel deadline</span>
              <span className="font-medium text-amber-600">{formatTime(schedule?.cancel_deadline)}</span>
            </div>
          </div>
          <button onClick={() => setEditing(true)}
            className="w-full rounded-lg border border-input px-3 py-2 text-sm font-medium hover:bg-accent transition-colors">
            Edit schedule
          </button>
        </>
      ) : (
        <div className="space-y-3">
          {[
            { label: "Start time", key: "start_time" },
            { label: "End time", key: "end_time" },
            { label: "Deadline", key: "cancel_deadline" },
          ].map(({ label, key }) => (
            <div key={key} className="space-y-1">
              <label className="text-xs font-medium text-muted-foreground">{label}</label>
              <input type="time" value={form[key]} onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
                className={inputCls} />
            </div>
          ))}
          <div className="flex items-center gap-2">
            <input type="checkbox" id={`active-${mealType}`} checked={form.is_active}
              onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))}
              className="rounded" />
            <label htmlFor={`active-${mealType}`} className="text-sm">Active</label>
          </div>
          <div className="flex gap-2">
            <button onClick={handleSave} disabled={saving}
              className="flex-1 rounded-lg bg-primary px-3 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-60 flex items-center justify-center gap-1.5 transition-colors">
              {saving && <Loader2 className="h-3.5 w-3.5 animate-spin" />} Save
            </button>
            <button onClick={() => setEditing(false)}
              className="rounded-lg border border-input px-3 py-2 text-sm font-medium hover:bg-accent transition-colors">
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function DiningPage() {
  const qc = useQueryClient();

  const { data: schedules, isLoading } = useQuery({
    queryKey: queryKeys.dining.schedules,
    queryFn: () => diningApi.getSchedules().then((r) => r.data.data),
  });

  const updateMutation = useMutation({
    mutationFn: ({ mealType, data }) => diningApi.updateSchedule(mealType, data),
    onSuccess: () => { toast.success("Schedule updated"); qc.invalidateQueries({ queryKey: queryKeys.dining.schedules }); },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  if (isLoading) return <PageLoader />;

  const scheduleMap = {};
  schedules?.forEach((s) => { scheduleMap[s.meal_type] = s; });

  return (
    <PageContainer>
      <PageHeader title="Dining Management" description="Configure meal schedules and deadlines" />
      <div className="grid gap-4 sm:grid-cols-3">
        {MEAL_TYPES.map((mealType) => (
          <ScheduleCard
            key={mealType}
            mealType={mealType}
            schedule={scheduleMap[mealType]}
            onSave={(type, data) => updateMutation.mutateAsync({ mealType: type, data })}
          />
        ))}
      </div>
    </PageContainer>
  );
}
