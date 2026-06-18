"use client";

import { useEffect } from "react";
import { X, Loader2, CheckCircle2, XCircle } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { cn } from "@/lib/utils";
import { UserForm } from "@/components/forms/UserForm";

// ── Modal shell ───────────────────────────────────────────────────────────────
export function Modal({ open, onClose, title, children, maxWidth = "max-w-lg" }) {
  // Close on Escape
  useEffect(() => {
    if (!open) return;
    const handler = (e) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />
      {/* Panel */}
      <div className={cn(
        "relative z-10 w-full rounded-2xl bg-card border shadow-xl",
        "animate-in fade-in-0 zoom-in-95 duration-200",
        maxWidth
      )}>
        {/* Header */}
        <div className="flex items-center justify-between border-b px-6 py-4">
          <h2 className="text-base font-semibold">{title}</h2>
          <button onClick={onClose}
            className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
            aria-label="Close">
            <X className="h-4 w-4" />
          </button>
        </div>
        {/* Body */}
        <div className="px-6 py-5">{children}</div>
      </div>
    </div>
  );
}

// ── UserModal ─────────────────────────────────────────────────────────────────
export function UserModal({ open, onClose, user, onSubmit, isLoading }) {
  const isEdit = !!user;
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? "Edit User" : "Create User"}
      maxWidth="max-w-xl"
    >
      <UserForm
        defaultValues={user}
        onSubmit={async (data) => {
          await onSubmit(data);
          onClose();
        }}
        isLoading={isLoading}
        isEdit={isEdit}
      />
    </Modal>
  );
}

// ── RequestReviewModal ────────────────────────────────────────────────────────
const rejectSchema = z.object({
  reason: z.string().min(5, "Please provide a reason (min 5 characters)"),
});

export function RequestReviewModal({ open, onClose, request, onApprove, onReject, isLoading }) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({ resolver: zodResolver(rejectSchema) });

  useEffect(() => { if (!open) reset(); }, [open, reset]);

  if (!request) return null;

  return (
    <Modal open={open} onClose={onClose} title="Review Request" maxWidth="max-w-lg">
      <div className="space-y-4">
        {/* Request info */}
        <div className="rounded-lg bg-muted/50 p-4 space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Applicant</span>
            <span className="font-medium">{request.user?.full_name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Student ID</span>
            <span>{request.user?.student_id}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Months requested</span>
            <span className="font-medium">{request.requested_months}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Amount paid</span>
            <span className="font-semibold text-primary">৳{request.payment?.amount?.toLocaleString()}</span>
          </div>
          {request.note && (
            <div>
              <span className="text-muted-foreground">Note</span>
              <p className="mt-0.5">{request.note}</p>
            </div>
          )}
        </div>

        {/* Approve */}
        <button
          onClick={() => onApprove(request.id)}
          disabled={isLoading}
          className="w-full rounded-lg bg-green-600 px-4 py-2.5 text-sm font-semibold text-white
            hover:bg-green-700 disabled:opacity-60 disabled:cursor-not-allowed
            flex items-center justify-center gap-2 transition-colors"
        >
          {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
          Approve request
        </button>

        {/* Reject */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Reject with reason</label>
          <textarea
            {...register("reason")}
            rows={3}
            placeholder="Reason for rejection…"
            className={`w-full rounded-lg border bg-background px-3 py-2 text-sm outline-none
              placeholder:text-muted-foreground focus:ring-2 focus:ring-ring transition-shadow
              ${errors.reason ? "border-destructive focus:ring-destructive/30" : "border-input"}`}
          />
          {errors.reason && <p className="text-xs text-destructive">{errors.reason.message}</p>}
          <button
            onClick={handleSubmit((data) => onReject(request.id, data.reason))}
            disabled={isLoading}
            className="w-full rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-2.5 text-sm font-semibold text-destructive
              hover:bg-destructive/20 disabled:opacity-60 disabled:cursor-not-allowed
              flex items-center justify-center gap-2 transition-colors"
          >
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <XCircle className="h-4 w-4" />}
            Reject request
          </button>
        </div>
      </div>
    </Modal>
  );
}

export default Modal;
