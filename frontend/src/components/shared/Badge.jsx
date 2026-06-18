"use client";

import { cn } from "@/lib/utils";
import {
  ROLE_LABELS,
  ROLE_COLORS,
  USER_STATUS_LABELS,
  USER_STATUS_COLORS,
  REQUEST_STATUS_LABELS,
  REQUEST_STATUS_COLORS,
} from "@/lib/constants";

/**
 * RoleBadge — displays a user role as a coloured pill.
 */
export function RoleBadge({ role, className }) {
  if (!role) return null;
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        ROLE_COLORS[role] ?? "bg-gray-100 text-gray-600",
        className
      )}
    >
      {ROLE_LABELS[role] ?? role}
    </span>
  );
}

/**
 * StatusBadge — displays user account status or request status as a coloured pill.
 * @param {"user"|"request"} type — which status set to use (default "user")
 */
export function StatusBadge({ status, type = "user", className }) {
  if (!status) return null;

  const labels = type === "request" ? REQUEST_STATUS_LABELS : USER_STATUS_LABELS;
  const colors = type === "request" ? REQUEST_STATUS_COLORS : USER_STATUS_COLORS;

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        colors[status] ?? "bg-gray-100 text-gray-600",
        className
      )}
    >
      {labels[status] ?? status}
    </span>
  );
}

/**
 * Generic Badge — fully customisable coloured pill.
 */
export function Badge({ children, variant = "default", className }) {
  const variants = {
    default:     "bg-primary/10 text-primary",
    success:     "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
    warning:     "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
    danger:      "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
    info:        "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
    muted:       "bg-muted text-muted-foreground",
    outline:     "border border-border text-foreground",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        variants[variant] ?? variants.default,
        className
      )}
    >
      {children}
    </span>
  );
}

export default Badge;
