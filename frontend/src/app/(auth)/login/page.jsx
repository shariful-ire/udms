"use client";

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { authApi, clearTokens } from "@/lib/axios";
import { useAuthStore } from "@/store/authStore";
import { getErrorMessage } from "@/lib/utils";

const loginSchema = z.object({
  identifier: z
    .string()
    .min(1, "Username or email is required")
    .max(255, "Too long"),
  password: z.string().min(1, "Password is required"),
  remember: z.boolean().optional(),
});

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { loginSuccess } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const redirect = searchParams.get("redirect") ?? "/dashboard";
  const sessionExpired = searchParams.get("session") === "expired";

  useEffect(() => {
    document.cookie = "udms_session=; path=/; max-age=0";
    clearTokens();
  }, []);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: { identifier: "", password: "", remember: false },
  });

  const onSubmit = async (values) => {
    setIsLoading(true);
    try {
      const res = await authApi.login({
        identifier: values.identifier,
        password: values.password,
      });
      const { access_token, user } = res.data.data;
      loginSuccess(access_token, user);

      // Set session presence flag for middleware
      document.cookie = "udms_session=1; path=/; max-age=604800; SameSite=Strict";

      toast.success(`Welcome back, ${user.full_name.split(" ")[0]}!`);
      router.replace(redirect);
    } catch (err) {
      const status = err?.response?.status;
      const message = getErrorMessage(err);
      const errorCode = err?.response?.data?.error_code;

      if (status === 403 && errorCode === "ACCOUNT_INACTIVE") {
        toast.error("Your email is not verified.", {
          description: "Check your inbox or request a new verification code.",
          action: {
            label: "Resend code",
            onClick: () => router.push("/verify-email"),
          },
        });
      } else if (status === 403 && errorCode === "ACCOUNT_SUSPENDED") {
        toast.error("Account suspended", {
          description: "Your account has been suspended. Contact administration.",
        });
      } else if (status === 423) {
        toast.error("Account locked", {
          description: message || "Too many failed attempts. Try again in 15 minutes.",
        });
      } else if (status === 401) {
        setError("password", { message: "Invalid username/email or password" });
      } else {
        toast.error(message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-1.5">
        <h1 className="text-2xl font-semibold tracking-tight">Sign in</h1>
        <p className="text-sm text-muted-foreground">
          Enter your credentials to access your account
        </p>
      </div>

      {sessionExpired && (
        <div className="rounded-lg border border-warning/30 bg-warning/10 px-4 py-3 text-sm text-warning-foreground">
          Your session expired. Please sign in again.
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        {/* Identifier */}
        <div className="space-y-1.5">
          <label htmlFor="identifier" className="text-sm font-medium">
            Username or Email
          </label>
          <input
            id="identifier"
            type="text"
            autoComplete="username"
            autoFocus
            placeholder="Enter your username or email"
            className={`w-full rounded-lg border bg-background px-3 py-2 text-sm outline-none placeholder:text-muted-foreground
              focus:ring-2 focus:ring-ring transition-shadow
              ${errors.identifier ? "border-destructive focus:ring-destructive/30" : "border-input"}`}
            {...register("identifier")}
          />
          {errors.identifier && (
            <p className="text-xs text-destructive">{errors.identifier.message}</p>
          )}
        </div>

        {/* Password */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <label htmlFor="password" className="text-sm font-medium">
              Password
            </label>
            <Link
              href="/forgot-password"
              className="text-xs text-primary hover:underline underline-offset-4"
            >
              Forgot password?
            </Link>
          </div>
          <div className="relative">
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              autoComplete="current-password"
              placeholder="Enter your password"
              className={`w-full rounded-lg border bg-background px-3 py-2 pr-10 text-sm outline-none placeholder:text-muted-foreground
                focus:ring-2 focus:ring-ring transition-shadow
                ${errors.password ? "border-destructive focus:ring-destructive/30" : "border-input"}`}
              {...register("password")}
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </button>
          </div>
          {errors.password && (
            <p className="text-xs text-destructive">{errors.password.message}</p>
          )}
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground
            hover:bg-primary/90 disabled:opacity-60 disabled:cursor-not-allowed
            transition-colors flex items-center justify-center gap-2"
        >
          {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
          {isLoading ? "Signing in…" : "Sign in"}
        </button>
      </form>

      {/* Register link */}
      <p className="text-center text-sm text-muted-foreground">
        Don&apos;t have an account?{" "}
        <Link
          href="/register"
          className="font-medium text-primary hover:underline underline-offset-4"
        >
          Create account
        </Link>
      </p>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense>
      <LoginForm />
    </Suspense>
  );
}
