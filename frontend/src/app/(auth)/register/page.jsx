"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { authApi } from "@/lib/axios";
import { getErrorMessage } from "@/lib/utils";

const registerSchema = z
  .object({
    full_name: z.string().min(2, "Full name must be at least 2 characters").max(150),
    username: z
      .string()
      .min(3, "Username must be at least 3 characters")
      .max(50)
      .regex(/^[a-zA-Z0-9_]+$/, "Only letters, numbers, and underscores"),
    email: z.string().email("Enter a valid email address").max(255),
    student_id: z
      .string()
      .min(4, "Student ID must be at least 4 characters")
      .max(20),
    department: z.string().min(1, "Department is required").max(100),
    batch: z.string().min(1, "Batch is required").max(20),
    hall_name: z.string().min(1, "Hall name is required").max(100),
    phone: z
      .string()
      .regex(/^(\+880|0)?1[3-9]\d{8}$/, "Enter a valid Bangladeshi phone number")
      .optional()
      .or(z.literal("")),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
      .regex(/[a-z]/, "Password must contain at least one lowercase letter")
      .regex(/[0-9]/, "Password must contain at least one number")
      .regex(/[^a-zA-Z0-9]/, "Password must contain at least one special character"),
    confirm_password: z.string(),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

const DEPARTMENTS = [
  "Computer Science & Engineering",
  "Electrical & Electronic Engineering",
  "Mechanical Engineering",
  "Civil Engineering",
  "Business Administration",
  "Economics",
  "Mathematics",
  "Physics",
  "Chemistry",
  "English",
  "Other",
];

const HALLS = [
  "Sher-e-Bangla Hall",
  "Shahid Suhrawardy Hall",
  "Zia Hall",
  "Bangabandhu Hall",
  "Shah Amanat Hall",
  "Other",
];

export default function RegisterPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (values) => {
    setIsLoading(true);
    try {
      const payload = { ...values };
      delete payload.confirm_password;
      if (!payload.phone) delete payload.phone;

      const res = await authApi.register(payload);
      const { email } = res.data.data ?? {};

      toast.success("Account created!", {
        description: "Check your email for a verification code.",
      });
      router.push(`/verify-email?email=${encodeURIComponent(email ?? values.email)}`);
    } catch (err) {
      const status = err?.response?.status;
      const errors_list = err?.response?.data?.errors ?? [];

      if (status === 422 && errors_list.length) {
        errors_list.forEach(({ field, message }) => {
          setError(field, { message });
        });
      } else {
        toast.error(getErrorMessage(err));
      }
    } finally {
      setIsLoading(false);
    }
  };

  const Field = ({ label, name, type = "text", placeholder, children, autoComplete }) => (
    <div className="space-y-1.5">
      <label htmlFor={name} className="text-sm font-medium">
        {label}
      </label>
      {children ?? (
        <input
          id={name}
          type={type}
          autoComplete={autoComplete}
          placeholder={placeholder}
          className={`w-full rounded-lg border bg-background px-3 py-2 text-sm outline-none placeholder:text-muted-foreground
            focus:ring-2 focus:ring-ring transition-shadow
            ${errors[name] ? "border-destructive focus:ring-destructive/30" : "border-input"}`}
          {...register(name)}
        />
      )}
      {errors[name] && (
        <p className="text-xs text-destructive">{errors[name].message}</p>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="space-y-1.5">
        <h1 className="text-2xl font-semibold tracking-tight">Create account</h1>
        <p className="text-sm text-muted-foreground">
          Fill in your details to register for UDMS
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        {/* Full name */}
        <Field label="Full Name" name="full_name" placeholder="Your full name" autoComplete="name" />

        {/* Username + Student ID */}
        <div className="grid grid-cols-2 gap-3">
          <Field label="Username" name="username" placeholder="username_123" autoComplete="username" />
          <Field label="Student ID" name="student_id" placeholder="e.g. 2020331001" />
        </div>

        {/* Email */}
        <Field label="Email Address" name="email" type="email" placeholder="you@university.edu" autoComplete="email" />

        {/* Department + Batch */}
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <label htmlFor="department" className="text-sm font-medium">Department</label>
            <select
              id="department"
              className={`w-full rounded-lg border bg-background px-3 py-2 text-sm outline-none
                focus:ring-2 focus:ring-ring transition-shadow
                ${errors.department ? "border-destructive" : "border-input"}`}
              {...register("department")}
            >
              <option value="">Select…</option>
              {DEPARTMENTS.map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
            {errors.department && (
              <p className="text-xs text-destructive">{errors.department.message}</p>
            )}
          </div>

          <Field label="Batch" name="batch" placeholder="e.g. 2020" />
        </div>

        {/* Hall */}
        <div className="space-y-1.5">
          <label htmlFor="hall_name" className="text-sm font-medium">Hall Name</label>
          <select
            id="hall_name"
            className={`w-full rounded-lg border bg-background px-3 py-2 text-sm outline-none
              focus:ring-2 focus:ring-ring transition-shadow
              ${errors.hall_name ? "border-destructive" : "border-input"}`}
            {...register("hall_name")}
          >
            <option value="">Select your hall…</option>
            {HALLS.map((h) => (
              <option key={h} value={h}>{h}</option>
            ))}
          </select>
          {errors.hall_name && (
            <p className="text-xs text-destructive">{errors.hall_name.message}</p>
          )}
        </div>

        {/* Phone */}
        <Field label="Phone (optional)" name="phone" type="tel" placeholder="01XXXXXXXXX" autoComplete="tel" />

        {/* Password */}
        <div className="space-y-1.5">
          <label htmlFor="password" className="text-sm font-medium">Password</label>
          <div className="relative">
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              autoComplete="new-password"
              placeholder="Min 8 chars with uppercase, number & symbol"
              className={`w-full rounded-lg border bg-background px-3 py-2 pr-10 text-sm outline-none placeholder:text-muted-foreground
                focus:ring-2 focus:ring-ring transition-shadow
                ${errors.password ? "border-destructive focus:ring-destructive/30" : "border-input"}`}
              {...register("password")}
            />
            <button type="button" onClick={() => setShowPassword((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              aria-label={showPassword ? "Hide" : "Show"}>
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          {errors.password && (
            <p className="text-xs text-destructive">{errors.password.message}</p>
          )}
        </div>

        {/* Confirm password */}
        <div className="space-y-1.5">
          <label htmlFor="confirm_password" className="text-sm font-medium">Confirm Password</label>
          <div className="relative">
            <input
              id="confirm_password"
              type={showConfirm ? "text" : "password"}
              autoComplete="new-password"
              placeholder="Repeat your password"
              className={`w-full rounded-lg border bg-background px-3 py-2 pr-10 text-sm outline-none placeholder:text-muted-foreground
                focus:ring-2 focus:ring-ring transition-shadow
                ${errors.confirm_password ? "border-destructive focus:ring-destructive/30" : "border-input"}`}
              {...register("confirm_password")}
            />
            <button type="button" onClick={() => setShowConfirm((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              aria-label={showConfirm ? "Hide" : "Show"}>
              {showConfirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          {errors.confirm_password && (
            <p className="text-xs text-destructive">{errors.confirm_password.message}</p>
          )}
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground
            hover:bg-primary/90 disabled:opacity-60 disabled:cursor-not-allowed
            transition-colors flex items-center justify-center gap-2"
        >
          {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
          {isLoading ? "Creating account…" : "Create account"}
        </button>
      </form>

      <p className="text-center text-sm text-muted-foreground">
        Already have an account?{" "}
        <Link href="/login" className="font-medium text-primary hover:underline underline-offset-4">
          Sign in
        </Link>
      </p>
    </div>
  );
}
