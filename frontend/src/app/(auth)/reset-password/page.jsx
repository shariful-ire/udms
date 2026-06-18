"use client";

import { useState, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Eye, EyeOff, Loader2, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import { authApi } from "@/lib/axios";
import { getErrorMessage } from "@/lib/utils";

const schema = z
  .object({
    email: z.string().email("Valid email required"),
    otp: z
      .string()
      .length(6, "OTP must be exactly 6 digits")
      .regex(/^\d{6}$/, "OTP must be 6 digits"),
    new_password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .regex(/[A-Z]/, "Must contain uppercase letter")
      .regex(/[a-z]/, "Must contain lowercase letter")
      .regex(/[0-9]/, "Must contain a number")
      .regex(/[^a-zA-Z0-9]/, "Must contain a special character"),
    confirm_password: z.string(),
  })
  .refine((d) => d.new_password === d.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [showPw, setShowPw] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [done, setDone] = useState(false);

  const emailFromParams = searchParams.get("email") ?? "";

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { email: emailFromParams, otp: "", new_password: "", confirm_password: "" },
  });

  const onSubmit = async (values) => {
    setIsLoading(true);
    try {
      await authApi.resetPassword({
        email: values.email,
        otp: values.otp,
        new_password: values.new_password,
      });
      setDone(true);
      toast.success("Password reset successfully!");
    } catch (err) {
      const status = err?.response?.status;
      const errorCode = err?.response?.data?.error_code;

      if (status === 400 && errorCode === "INVALID_OTP") {
        setError("otp", { message: "Invalid or expired code. Request a new one." });
      } else {
        toast.error(getErrorMessage(err));
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (done) {
    return (
      <div className="space-y-6 text-center">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30">
          <CheckCircle2 className="h-7 w-7 text-green-600 dark:text-green-400" />
        </div>
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold">Password updated</h1>
          <p className="text-sm text-muted-foreground">
            Your password has been reset. You can now sign in with your new password.
          </p>
        </div>
        <Link
          href="/login"
          className="block w-full rounded-lg bg-primary px-4 py-2.5 text-center text-sm font-semibold text-primary-foreground
            hover:bg-primary/90 transition-colors"
        >
          Sign in
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="space-y-1.5">
        <h1 className="text-2xl font-semibold tracking-tight">Reset password</h1>
        <p className="text-sm text-muted-foreground">
          Enter the 6-digit code from your email and your new password
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        {/* Email */}
        <div className="space-y-1.5">
          <label htmlFor="email" className="text-sm font-medium">Email</label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            className={`w-full rounded-lg border bg-background px-3 py-2 text-sm outline-none placeholder:text-muted-foreground
              focus:ring-2 focus:ring-ring transition-shadow
              ${errors.email ? "border-destructive focus:ring-destructive/30" : "border-input"}`}
            {...register("email")}
          />
          {errors.email && (
            <p className="text-xs text-destructive">{errors.email.message}</p>
          )}
        </div>

        {/* OTP */}
        <div className="space-y-1.5">
          <label htmlFor="otp" className="text-sm font-medium">6-Digit Code</label>
          <input
            id="otp"
            type="text"
            inputMode="numeric"
            maxLength={6}
            autoFocus
            placeholder="000000"
            className={`w-full rounded-lg border bg-background px-3 py-2 text-sm text-center tracking-[0.5em] outline-none
              focus:ring-2 focus:ring-ring transition-shadow font-mono
              ${errors.otp ? "border-destructive focus:ring-destructive/30" : "border-input"}`}
            {...register("otp")}
          />
          {errors.otp && (
            <p className="text-xs text-destructive">{errors.otp.message}</p>
          )}
        </div>

        {/* New password */}
        <div className="space-y-1.5">
          <label htmlFor="new_password" className="text-sm font-medium">New Password</label>
          <div className="relative">
            <input
              id="new_password"
              type={showPw ? "text" : "password"}
              autoComplete="new-password"
              placeholder="Min 8 chars with uppercase, number & symbol"
              className={`w-full rounded-lg border bg-background px-3 py-2 pr-10 text-sm outline-none placeholder:text-muted-foreground
                focus:ring-2 focus:ring-ring transition-shadow
                ${errors.new_password ? "border-destructive focus:ring-destructive/30" : "border-input"}`}
              {...register("new_password")}
            />
            <button type="button" onClick={() => setShowPw((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
              {showPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          {errors.new_password && (
            <p className="text-xs text-destructive">{errors.new_password.message}</p>
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
              placeholder="Repeat new password"
              className={`w-full rounded-lg border bg-background px-3 py-2 pr-10 text-sm outline-none placeholder:text-muted-foreground
                focus:ring-2 focus:ring-ring transition-shadow
                ${errors.confirm_password ? "border-destructive focus:ring-destructive/30" : "border-input"}`}
              {...register("confirm_password")}
            />
            <button type="button" onClick={() => setShowConfirm((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
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
          {isLoading ? "Resetting…" : "Reset password"}
        </button>
      </form>

      <div className="text-center space-y-2">
        <p className="text-sm text-muted-foreground">
          Didn&apos;t receive the code?{" "}
          <Link href="/forgot-password" className="text-primary hover:underline underline-offset-4">
            Resend
          </Link>
        </p>
        <Link href="/login" className="block text-sm text-muted-foreground hover:text-foreground transition-colors">
          Back to sign in
        </Link>
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense>
      <ResetPasswordForm />
    </Suspense>
  );
}
