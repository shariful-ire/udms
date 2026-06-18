"use client";

import { AlertTriangle, Loader2, X } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * ConfirmModal
 *
 * @param {boolean} open
 * @param {function} onClose
 * @param {function} onConfirm — async function called when user confirms
 * @param {string} title
 * @param {string} [description]
 * @param {string} [confirmLabel="Confirm"]
 * @param {"danger"|"warning"|"primary"} [variant="danger"]
 * @param {boolean} [isLoading]
 */
export function ConfirmModal({
  open,
  onClose,
  onConfirm,
  title,
  description,
  confirmLabel = "Confirm",
  variant = "danger",
  isLoading = false,
}) {
  if (!open) return null;

  const confirmClass =
    variant === "danger"
      ? "bg-destructive text-destructive-foreground hover:bg-destructive/90"
      : variant === "warning"
      ? "bg-amber-500 text-white hover:bg-amber-600"
      : "bg-primary text-primary-foreground hover:bg-primary/90";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={!isLoading ? onClose : undefined}
      />

      {/* Dialog */}
      <div
        className="relative z-10 w-full max-w-md rounded-2xl border bg-card shadow-xl mx-4 p-6 space-y-4"
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-title"
      >
        {/* Close button */}
        <button
          onClick={onClose}
          disabled={isLoading}
          className="absolute right-4 top-4 text-muted-foreground hover:text-foreground disabled:opacity-50"
          aria-label="Close"
        >
          <X className="h-4 w-4" />
        </button>

        {/* Icon + Title */}
        <div className="flex items-start gap-4">
          <div
            className={cn(
              "flex h-10 w-10 shrink-0 items-center justify-center rounded-full",
              variant === "danger" ? "bg-destructive/10" : "bg-amber-500/10"
            )}
          >
            <AlertTriangle
              className={cn(
                "h-5 w-5",
                variant === "danger" ? "text-destructive" : "text-amber-500"
              )}
            />
          </div>
          <div className="space-y-1 min-w-0">
            <h2 id="confirm-title" className="font-semibold text-foreground">
              {title}
            </h2>
            {description && (
              <p className="text-sm text-muted-foreground">{description}</p>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 justify-end pt-2">
          <button
            onClick={onClose}
            disabled={isLoading}
            className="rounded-lg border border-input px-4 py-2 text-sm font-medium hover:bg-muted transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={isLoading}
            className={cn(
              "flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors disabled:opacity-60",
              confirmClass
            )}
          >
            {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmModal;
