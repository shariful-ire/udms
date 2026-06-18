"use client";

import { useState, useEffect, useRef, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2, CheckCircle2, Mail } from "lucide-react";
import { toast } from "sonner";
import { authApi } from "@/lib/axios";
import { getErrorMessage } from "@/lib/utils";

const RESEND_COOLDOWN = 60; // seconds

function VerifyEmailForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const email = searchParams.get("email") ?? "";

  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [cooldown, setCooldown] = useState(0);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");
  const inputRefs = useRef([]);

  // Countdown timer
  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = setTimeout(() => setCooldown((c) => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [cooldown]);

  const otpValue = otp.join("");

  const handleOtpChange = (index, value) => {
    const cleaned = value.replace(/\D/g, "").slice(-1);
    const newOtp = [...otp];
    newOtp[index] = cleaned;
    setOtp(newOtp);
    setError("");

    // Auto-advance
    if (cleaned && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    const newOtp = [...otp];
    for (let i = 0; i < 6; i++) {
      newOtp[i] = pasted[i] ?? "";
    }
    setOtp(newOtp);
    if (pasted.length === 6) inputRefs.current[5]?.focus();
  };

  const handleVerify = async () => {
    if (otpValue.length !== 6) {
      setError("Please enter all 6 digits.");
      return;
    }
    setIsLoading(true);
    setError("");
    try {
      await authApi.verifyEmail({ email, otp: otpValue });
      setDone(true);
      toast.success("Email verified! You can now sign in.");
    } catch (err) {
      const errorCode = err?.response?.data?.error_code;
      if (errorCode === "INVALID_OTP") {
        setError("Invalid or expired code. Please try again.");
        setOtp(["", "", "", "", "", ""]);
        inputRefs.current[0]?.focus();
      } else {
        setError(getErrorMessage(err));
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    if (cooldown > 0 || !email) return;
    setIsResending(true);
    try {
      await authApi.resendVerification({ email });
      setCooldown(RESEND_COOLDOWN);
      toast.success("Verification code sent!");
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setIsResending(false);
    }
  };

  if (done) {
    return (
      <div className="space-y-6 text-center">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30">
          <CheckCircle2 className="h-7 w-7 text-green-600 dark:text-green-400" />
        </div>
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold">Email verified!</h1>
          <p className="text-sm text-muted-foreground">
            Your account is now active. Sign in to get started.
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
      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
        <Mail className="h-6 w-6 text-primary" />
      </div>

      <div className="space-y-1.5 text-center">
        <h1 className="text-2xl font-semibold tracking-tight">Verify your email</h1>
        <p className="text-sm text-muted-foreground">
          We sent a 6-digit code to{" "}
          {email ? (
            <span className="font-medium text-foreground">{email}</span>
          ) : (
            "your email address"
          )}
        </p>
      </div>

      {/* OTP inputs */}
      <div className="flex justify-center gap-2">
        {otp.map((digit, i) => (
          <input
            key={i}
            ref={(el) => (inputRefs.current[i] = el)}
            type="text"
            inputMode="numeric"
            maxLength={1}
            value={digit}
            onChange={(e) => handleOtpChange(i, e.target.value)}
            onKeyDown={(e) => handleKeyDown(i, e)}
            onPaste={i === 0 ? handlePaste : undefined}
            className={`w-11 h-12 rounded-lg border text-center text-lg font-semibold outline-none
              focus:ring-2 focus:ring-ring transition-shadow font-mono
              ${error ? "border-destructive" : digit ? "border-primary" : "border-input"}`}
            aria-label={`Digit ${i + 1}`}
          />
        ))}
      </div>

      {error && (
        <p className="text-center text-sm text-destructive">{error}</p>
      )}

      {/* Verify button */}
      <button
        onClick={handleVerify}
        disabled={isLoading || otpValue.length !== 6}
        className="w-full rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground
          hover:bg-primary/90 disabled:opacity-60 disabled:cursor-not-allowed
          transition-colors flex items-center justify-center gap-2"
      >
        {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
        {isLoading ? "Verifying…" : "Verify email"}
      </button>

      {/* Resend */}
      <div className="text-center space-y-2">
        <p className="text-sm text-muted-foreground">
          Didn&apos;t receive the code?{" "}
          {cooldown > 0 ? (
            <span className="text-muted-foreground">
              Resend in {cooldown}s
            </span>
          ) : (
            <button
              onClick={handleResend}
              disabled={isResending}
              className="font-medium text-primary hover:underline underline-offset-4 disabled:opacity-60"
            >
              {isResending ? "Sending…" : "Resend code"}
            </button>
          )}
        </p>
        <Link
          href="/login"
          className="block text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          Back to sign in
        </Link>
      </div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense>
      <VerifyEmailForm />
    </Suspense>
  );
}
