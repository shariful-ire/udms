"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Loader2, Plus, Trash2 } from "lucide-react";
import { useFieldArray } from "react-hook-form";
import { EXPENSE_CATEGORIES, PAYMENT_METHODS, MEAL_TYPES, MEAL_TYPE_LABELS } from "@/lib/constants";

const inputCls = (hasError) =>
  `w-full rounded-lg border bg-background px-3 py-2 text-sm outline-none placeholder:text-muted-foreground
   focus:ring-2 focus:ring-ring transition-shadow
   ${hasError ? "border-destructive focus:ring-destructive/30" : "border-input"}`;

const Field = ({ label, children, error, required }) => (
  <div className="space-y-1.5">
    <label className="text-sm font-medium">
      {label}{required && <span className="text-destructive ml-0.5">*</span>}
    </label>
    {children}
    {error && <p className="text-xs text-destructive">{error}</p>}
  </div>
);

const SubmitBtn = ({ isLoading, label }) => (
  <button type="submit" disabled={isLoading}
    className="w-full rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground
      hover:bg-primary/90 disabled:opacity-60 disabled:cursor-not-allowed
      flex items-center justify-center gap-2 transition-colors">
    {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
    {isLoading ? "Saving…" : label}
  </button>
);

// ── MenuForm ──────────────────────────────────────────────────────────────────
const menuSchema = z.object({
  date: z.string().min(1, "Date is required"),
  meal_type: z.enum(MEAL_TYPES, { required_error: "Meal type is required" }),
  items: z.array(z.object({ name: z.string().min(1, "Item name required") })).min(1, "At least one item required"),
  note: z.string().optional(),
});

export function MenuForm({ defaultValues, onSubmit, isLoading }) {
  const { register, handleSubmit, control, formState: { errors } } = useForm({
    resolver: zodResolver(menuSchema),
    defaultValues: defaultValues ?? { date: "", meal_type: "", items: [{ name: "" }], note: "" },
  });
  const { fields, append, remove } = useFieldArray({ control, name: "items" });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
      <div className="grid grid-cols-2 gap-4">
        <Field label="Date" error={errors.date?.message} required>
          <input type="date" {...register("date")}
            className={`${inputCls(errors.date)} [color-scheme:light] dark:[color-scheme:dark]`} />
        </Field>
        <Field label="Meal Type" error={errors.meal_type?.message} required>
          <select {...register("meal_type")} className={inputCls(errors.meal_type)}>
            <option value="">Select…</option>
            {MEAL_TYPES.map((t) => (
              <option key={t} value={t}>{MEAL_TYPE_LABELS[t]}</option>
            ))}
          </select>
        </Field>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Menu Items <span className="text-destructive">*</span></label>
        {fields.map((field, i) => (
          <div key={field.id} className="flex gap-2">
            <input {...register(`items.${i}.name`)} placeholder={`Item ${i + 1}`}
              className={inputCls(errors.items?.[i]?.name)} />
            {fields.length > 1 && (
              <button type="button" onClick={() => remove(i)}
                className="rounded-lg border border-input p-2 text-muted-foreground hover:text-destructive hover:border-destructive/50 transition-colors">
                <Trash2 className="h-4 w-4" />
              </button>
            )}
          </div>
        ))}
        {errors.items?.message && <p className="text-xs text-destructive">{errors.items.message}</p>}
        <button type="button" onClick={() => append({ name: "" })}
          className="flex items-center gap-1.5 text-sm text-primary hover:underline underline-offset-4">
          <Plus className="h-4 w-4" /> Add item
        </button>
      </div>

      <Field label="Note (optional)" error={errors.note?.message}>
        <textarea {...register("note")} rows={2} placeholder="Any special notes…"
          className={inputCls(errors.note)} />
      </Field>

      <SubmitBtn isLoading={isLoading} label={defaultValues ? "Save changes" : "Create menu"} />
    </form>
  );
}

// ── ExpenseForm ───────────────────────────────────────────────────────────────
const expenseSchema = z.object({
  date: z.string().min(1, "Date required"),
  category: z.string().min(1, "Category required"),
  amount: z.coerce.number().positive("Must be a positive number"),
  description: z.string().min(1, "Description required").max(500),
  receipt_number: z.string().optional(),
});

export function ExpenseForm({ defaultValues, onSubmit, isLoading }) {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(expenseSchema),
    defaultValues: defaultValues ?? {},
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
      <div className="grid grid-cols-2 gap-4">
        <Field label="Date" error={errors.date?.message} required>
          <input type="date" {...register("date")}
            className={`${inputCls(errors.date)} [color-scheme:light] dark:[color-scheme:dark]`} />
        </Field>
        <Field label="Category" error={errors.category?.message} required>
          <select {...register("category")} className={inputCls(errors.category)}>
            <option value="">Select…</option>
            {EXPENSE_CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>{c.label}</option>
            ))}
          </select>
        </Field>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Field label="Amount (৳)" error={errors.amount?.message} required>
          <input type="number" step="0.01" min="0" {...register("amount")} placeholder="0.00"
            className={inputCls(errors.amount)} />
        </Field>
        <Field label="Receipt Number" error={errors.receipt_number?.message}>
          <input {...register("receipt_number")} placeholder="Optional" className={inputCls(errors.receipt_number)} />
        </Field>
      </div>

      <Field label="Description" error={errors.description?.message} required>
        <textarea {...register("description")} rows={3} placeholder="Describe the expense…"
          className={inputCls(errors.description)} />
      </Field>

      <SubmitBtn isLoading={isLoading} label={defaultValues ? "Save changes" : "Add expense"} />
    </form>
  );
}

// ── RequestForm ───────────────────────────────────────────────────────────────
const requestSchema = z.object({
  requested_months: z.coerce.number().int().min(1).max(12, "Max 12 months"),
  note: z.string().optional(),
});

export function RequestForm({ onSubmit, isLoading, mealRate }) {
  const { register, handleSubmit, watch, formState: { errors } } = useForm({
    resolver: zodResolver(requestSchema),
    defaultValues: { requested_months: 1, note: "" },
  });
  const months = watch("requested_months");
  const total = (Number(months) || 0) * (mealRate ?? 0);

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
      <Field label="Number of Months" error={errors.requested_months?.message} required>
        <input type="number" min="1" max="12" {...register("requested_months")}
          className={inputCls(errors.requested_months)} />
      </Field>

      {mealRate > 0 && (
        <div className="rounded-lg bg-muted/50 px-4 py-3 text-sm">
          <div className="flex justify-between text-muted-foreground">
            <span>Monthly rate</span>
            <span>৳{mealRate.toLocaleString()}</span>
          </div>
          <div className="flex justify-between font-semibold mt-1">
            <span>Total payable</span>
            <span className="text-primary">৳{total.toLocaleString()}</span>
          </div>
        </div>
      )}

      <Field label="Note (optional)" error={errors.note?.message}>
        <textarea {...register("note")} rows={3} placeholder="Any additional information…"
          className={inputCls(errors.note)} />
      </Field>

      <SubmitBtn isLoading={isLoading} label="Submit request" />
    </form>
  );
}

// ── PaymentForm ───────────────────────────────────────────────────────────────
const paymentSchema = z.object({
  amount: z.coerce.number().positive("Amount must be positive"),
  payment_method: z.string().min(1, "Payment method required"),
  transaction_id: z.string().optional(),
  payment_date: z.string().min(1, "Payment date required"),
  note: z.string().optional(),
});

export function PaymentForm({ onSubmit, isLoading, expectedAmount }) {
  const { register, handleSubmit, watch, formState: { errors } } = useForm({
    resolver: zodResolver(paymentSchema),
    defaultValues: {
      amount: expectedAmount ?? "",
      payment_date: new Date().toISOString().split("T")[0],
    },
  });
  const method = watch("payment_method");

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
      <div className="grid grid-cols-2 gap-4">
        <Field label="Amount (৳)" error={errors.amount?.message} required>
          <input type="number" step="0.01" min="0" {...register("amount")} placeholder="0.00"
            className={inputCls(errors.amount)} />
        </Field>
        <Field label="Payment Date" error={errors.payment_date?.message} required>
          <input type="date" {...register("payment_date")}
            className={`${inputCls(errors.payment_date)} [color-scheme:light] dark:[color-scheme:dark]`} />
        </Field>
      </div>

      <Field label="Payment Method" error={errors.payment_method?.message} required>
        <select {...register("payment_method")} className={inputCls(errors.payment_method)}>
          <option value="">Select method…</option>
          {PAYMENT_METHODS.map((m) => (
            <option key={m.value} value={m.value}>{m.label}</option>
          ))}
        </select>
      </Field>

      {method && method !== "CASH" && (
        <Field label="Transaction ID" error={errors.transaction_id?.message}>
          <input {...register("transaction_id")} placeholder="Transaction reference number"
            className={inputCls(errors.transaction_id)} />
        </Field>
      )}

      <Field label="Note (optional)" error={errors.note?.message}>
        <textarea {...register("note")} rows={2} placeholder="Payment notes…"
          className={inputCls(errors.note)} />
      </Field>

      <SubmitBtn isLoading={isLoading} label="Submit payment" />
    </form>
  );
}
