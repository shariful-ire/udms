"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { ArrowLeft, Loader2, Mail } from "lucide-react";
import { toast } from "sonner";
import { authApi } from "@/lib/axios";

const schema = z.object({
  email: z.string().email("Enter a valid email address"),
});

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [submittedEmail, setSubmittedEmail] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ resolver: zodResolver(schema) });

  const onSubmit = async ({ email }) => {
    setIsLoading(true);
    try {
      await authApi.forgotPassword({ email });
      setSubmittedEmail(email);
      setSubmitted(true);
    } catch {
      // Always show success to prevent email enumeration
      setSubmittedEmail(email);
      setSubmitted(true);
    } finally {
      setIsLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="space-y-6 text-center">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-primary/10">
          <Mail className="h-7 w-7 text-primary" />
        </div>
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold">Check your email</h1>
          <p className="text-sm text-muted-foreground">
            If an account exists for{" "}
            <span className="font-medium text-foreground">{submittedEmail}</span>,
            you&apos;ll receive a 6-digit reset code shortly.
          </p>
        </div>
        <button
          onClick={() =>
            router.push(`/reset-password?email=${encodeURIComponent(submittedEmail)}`)
          }
          className="w-full rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground
            hover:bg-primary/90 transition-colors"
        >
          Enter reset code
        </button>
        <button
          onClick={() => setSubmitted(false)}
          className="text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          Use a different email
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="space-y-1.5">
        <h1 className="text-2xl font-semibold tracking-tight">Forgot password</h1>
        <p className="text-sm text-muted-foreground">
          Enter your email and we&apos;ll send you a reset code
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        <div className="space-y-1.5">
          <label htmlFor="email" className="text-sm font-medium">
            Email Address
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            autoFocus
            placeholder="you@university.edu"
            className={`w-full rounded-lg border bg-background px-3 py-2 text-sm outline-none placeholder:text-muted-foreground
              focus:ring-2 focus:ring-ring transition-shadow
              ${errors.email ? "border-destructive focus:ring-destructive/30" : "border-input"}`}
            {...register("email")}
          />
          {errors.email && (
            <p className="text-xs text-destructive">{errors.email.message}</p>
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
          {isLoading ? "Sending code…" : "Send reset code"}
        </button>
      </form>

      <Link
        href="/login"
        className="flex items-center justify-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to sign in
      </Link>
    </div>
  );
}
