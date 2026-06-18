"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";
import { settingsApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { getErrorMessage } from "@/lib/utils";
import { PageContainer, PageLoader } from "@/components/shared/LoadingSpinner";
import { PageHeader } from "@/components/layout/PageHeader";
import { useEffect } from "react";

const schema = z.object({
  monthly_meal_rate:      z.coerce.number().positive("Must be positive"),
  breakfast_deadline:     z.string().min(1, "Required"),
  lunch_deadline:         z.string().min(1, "Required"),
  dinner_deadline:        z.string().min(1, "Required"),
  max_login_attempts:     z.coerce.number().int().min(3).max(20),
  lockout_duration_mins:  z.coerce.number().int().min(5).max(1440),
});

const inputCls = "w-full rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring transition-shadow";

export default function SettingsPage() {
  const qc = useQueryClient();
  const { data: settings, isLoading } = useQuery({
    queryKey: queryKeys.settings,
    queryFn: () => settingsApi.get().then((r) => r.data.data),
  });

  const { register, handleSubmit, reset, formState: { errors } } = useForm({ resolver: zodResolver(schema) });

  useEffect(() => {
    if (settings) reset({
      monthly_meal_rate: settings.monthly_meal_rate,
      breakfast_deadline: settings.breakfast_deadline,
      lunch_deadline: settings.lunch_deadline,
      dinner_deadline: settings.dinner_deadline,
      max_login_attempts: settings.max_login_attempts ?? 5,
      lockout_duration_mins: settings.lockout_duration_mins ?? 15,
    });
  }, [settings, reset]);

  const mutation = useMutation({
    mutationFn: (data) => settingsApi.update(data),
    onSuccess: () => { toast.success("Settings saved"); qc.invalidateQueries({ queryKey: queryKeys.settings }); },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  if (isLoading) return <PageLoader />;

  const Section = ({ title, children }) => (
    <div className="rounded-xl border bg-card p-6 space-y-4">
      <h3 className="font-semibold text-sm border-b pb-3">{title}</h3>
      {children}
    </div>
  );

  const Field = ({ label, name, type = "text", hint }) => (
    <div className="space-y-1.5">
      <label className="text-sm font-medium">{label}</label>
      <input type={type} {...register(name)} className={inputCls} />
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
      {errors[name] && <p className="text-xs text-destructive">{errors[name].message}</p>}
    </div>
  );

  return (
    <PageContainer>
      <PageHeader title="Settings" description="Configure system-wide dining parameters" />

      <form onSubmit={handleSubmit(mutation.mutate)} className="space-y-6 max-w-2xl">
        <Section title="Meal Rate">
          <Field label="Monthly Meal Rate (৳)" name="monthly_meal_rate" type="number"
            hint="The amount students pay per month for the dining program" />
        </Section>

        <Section title="Meal Deadlines">
          <p className="text-sm text-muted-foreground -mt-1">Students cannot add or cancel meals after these deadlines each day.</p>
          <div className="grid gap-4 sm:grid-cols-3">
            <Field label="Breakfast Deadline" name="breakfast_deadline" type="time" />
            <Field label="Lunch Deadline" name="lunch_deadline" type="time" />
            <Field label="Dinner Deadline" name="dinner_deadline" type="time" />
          </div>
        </Section>

        <Section title="Security">
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Max Login Attempts" name="max_login_attempts" type="number"
              hint="Account locks after this many failures" />
            <Field label="Lockout Duration (minutes)" name="lockout_duration_mins" type="number"
              hint="How long the account stays locked" />
          </div>
        </Section>

        <button type="submit" disabled={mutation.isPending}
          className="flex items-center gap-2 rounded-lg bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-60 transition-colors">
          {mutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
          {mutation.isPending ? "Saving…" : "Save settings"}
        </button>
      </form>
    </PageContainer>
  );
}
