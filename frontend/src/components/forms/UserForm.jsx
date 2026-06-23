"use client";

import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Loader2 } from "lucide-react";
import { ROLES } from "@/lib/constants";

const DEPARTMENTS = ["IRE", "CySE", "DSE", "EdTE", "SE"];
const HALLS = ["UFTB Boys Hall", "UFTB Girls Hall-1", "UFTB Girls Hall-2"];

const createSchema = z.object({
  full_name:   z.string().min(2).max(150),
  username:    z.string().min(3).max(50).regex(/^[a-zA-Z0-9_]+$/, "Letters, numbers and underscores only"),
  email:       z.string().email(),
  student_id:  z.string().min(4).max(20),
  department:  z.string().min(1, "Required"),
  batch:       z.string().min(1, "Required"),
  hall_name:   z.string().min(1, "Required"),
  phone:       z.string().optional().or(z.literal("")),
  role:        z.enum([ROLES.CUSTOMER, ROLES.NON_CUSTOMER, ROLES.DINING_MANAGER]),
  password:    z.string().min(8).regex(/[A-Z]/).regex(/[0-9]/).regex(/[^a-zA-Z0-9]/),
});

const editSchema = createSchema.omit({ password: true }).partial();

const Field = ({ label, children, error, required }) => (
  <div className="space-y-1.5">
    <label className="text-sm font-medium">
      {label}{required && <span className="text-destructive ml-0.5">*</span>}
    </label>
    {children}
    {error && <p className="text-xs text-destructive">{error}</p>}
  </div>
);

const inputCls = (hasError) =>
  `w-full rounded-lg border bg-background px-3 py-2 text-sm outline-none placeholder:text-muted-foreground
   focus:ring-2 focus:ring-ring transition-shadow
   ${hasError ? "border-destructive focus:ring-destructive/30" : "border-input"}`;

export function UserForm({ defaultValues, onSubmit, isLoading, isEdit = false }) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(isEdit ? editSchema : createSchema),
    defaultValues: defaultValues ?? {},
  });

  useEffect(() => {
    if (defaultValues) reset(defaultValues);
  }, [defaultValues, reset]);

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
      <div className="grid grid-cols-2 gap-4">
        <Field label="Full Name" error={errors.full_name?.message} required>
          <input {...register("full_name")} placeholder="Full name" className={inputCls(errors.full_name)} />
        </Field>
        <Field label="Username" error={errors.username?.message} required>
          <input {...register("username")} placeholder="username_123" className={inputCls(errors.username)} />
        </Field>
      </div>

      <Field label="Email" error={errors.email?.message} required>
        <input {...register("email")} type="email" placeholder="user@university.edu" className={inputCls(errors.email)} />
      </Field>

      <div className="grid grid-cols-2 gap-4">
        <Field label="Student ID" error={errors.student_id?.message} required>
          <input {...register("student_id")} placeholder="2020331001" className={inputCls(errors.student_id)} />
        </Field>
        <Field label="Batch" error={errors.batch?.message} required>
          <input {...register("batch")} placeholder="2020" className={inputCls(errors.batch)} />
        </Field>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Field label="Department" error={errors.department?.message} required>
          <select {...register("department")} className={inputCls(errors.department)}>
            <option value="">Select…</option>
            {DEPARTMENTS.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </Field>
        <Field label="Hall Name" error={errors.hall_name?.message} required>
          <select {...register("hall_name")} className={inputCls(errors.hall_name)}>
            <option value="">Select…</option>
            {HALLS.map((h) => (
              <option key={h} value={h}>{h}</option>
            ))}
          </select>
        </Field>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Field label="Phone" error={errors.phone?.message}>
          <input {...register("phone")} type="tel" placeholder="01XXXXXXXXX" className={inputCls(errors.phone)} />
        </Field>
        <Field label="Role" error={errors.role?.message} required>
          <select {...register("role")} className={inputCls(errors.role)}>
            <option value="">Select role…</option>
            <option value={ROLES.NON_CUSTOMER}>Student (Non-Customer)</option>
            <option value={ROLES.CUSTOMER}>Customer</option>
            <option value={ROLES.DINING_MANAGER}>Dining Manager</option>
          </select>
        </Field>
      </div>

      {!isEdit && (
        <Field label="Password" error={errors.password?.message} required>
          <input {...register("password")} type="password" placeholder="Min 8 chars, uppercase, number, symbol"
            className={inputCls(errors.password)} />
        </Field>
      )}

      <button
        type="submit"
        disabled={isLoading}
        className="w-full rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground
          hover:bg-primary/90 disabled:opacity-60 disabled:cursor-not-allowed
          flex items-center justify-center gap-2 transition-colors"
      >
        {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
        {isLoading ? "Saving…" : isEdit ? "Save changes" : "Create user"}
      </button>
    </form>
  );
}

export default UserForm;
