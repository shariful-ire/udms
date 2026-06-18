import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { format, formatDistanceToNow, parseISO, isValid } from "date-fns";
import { CURRENCY_SYMBOL, DATE_FORMAT, DATETIME_FORMAT } from "@/lib/constants";

// ── Class merging ─────────────────────────────────────────────────────────────
/**
 * Merge Tailwind classes with clsx + tailwind-merge for conflict resolution.
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

// ── Currency ──────────────────────────────────────────────────────────────────
/**
 * Format a numeric value as currency with the app currency symbol.
 * @param {number|string} amount
 * @param {object} [options]
 * @param {number} [options.decimals=2]
 * @param {boolean} [options.compact=false] — abbreviate to K/M/B
 */
export function formatCurrency(amount, options = {}) {
  const { decimals = 2, compact = false } = options;
  const num = Number(amount);
  if (isNaN(num)) return `${CURRENCY_SYMBOL}0.00`;

  if (compact) {
    if (num >= 1_000_000) return `${CURRENCY_SYMBOL}${(num / 1_000_000).toFixed(1)}M`;
    if (num >= 1_000) return `${CURRENCY_SYMBOL}${(num / 1_000).toFixed(1)}K`;
  }

  return `${CURRENCY_SYMBOL}${num.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })}`;
}

// ── Dates ─────────────────────────────────────────────────────────────────────
/**
 * Parse a date string or Date object safely.
 */
function parseDate(value) {
  if (!value) return null;
  if (value instanceof Date) return isValid(value) ? value : null;
  const parsed = typeof value === "string" ? parseISO(value) : new Date(value);
  return isValid(parsed) ? parsed : null;
}

/**
 * Format a date to "MMM d, yyyy" (or custom format).
 */
export function formatDate(value, fmt = DATE_FORMAT) {
  const d = parseDate(value);
  return d ? format(d, fmt) : "—";
}

/**
 * Format a datetime to "MMM d, yyyy HH:mm".
 */
export function formatDatetime(value, fmt = DATETIME_FORMAT) {
  const d = parseDate(value);
  return d ? format(d, fmt) : "—";
}

/**
 * Format as relative time: "3 minutes ago", "2 days ago".
 */
export function formatRelative(value) {
  const d = parseDate(value);
  return d ? formatDistanceToNow(d, { addSuffix: true }) : "—";
}

/**
 * Format a time string "HH:mm:ss" to "HH:mm" (drop seconds).
 */
export function formatTime(timeStr) {
  if (!timeStr) return "—";
  const parts = String(timeStr).split(":");
  return parts.length >= 2 ? `${parts[0]}:${parts[1]}` : timeStr;
}

// ── Strings ───────────────────────────────────────────────────────────────────
/**
 * Generate initials from a full name for avatar fallback.
 * "John Doe" → "JD", "Alice" → "A"
 */
export function getInitials(name) {
  if (!name || typeof name !== "string") return "?";
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0][0].toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

/**
 * Truncate a string to maxLength with an ellipsis.
 */
export function truncate(str, maxLength = 60) {
  if (!str) return "";
  return str.length <= maxLength ? str : `${str.slice(0, maxLength)}…`;
}

/**
 * Title-case a string: "hello_world" → "Hello World"
 */
export function titleCase(str) {
  if (!str) return "";
  return str
    .toLowerCase()
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

// ── Numbers ───────────────────────────────────────────────────────────────────
/**
 * Format a large number with K / M / B suffix.
 */
export function formatCompact(num) {
  const n = Number(num);
  if (isNaN(n)) return "0";
  if (n >= 1_000_000_000) return `${(n / 1_000_000_000).toFixed(1)}B`;
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

/**
 * Clamp a value between min and max.
 */
export function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

// ── Misc ──────────────────────────────────────────────────────────────────────
/**
 * Build query string from params object, omitting null/undefined values.
 */
export function buildQueryString(params) {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== null && v !== undefined && v !== "") {
      qs.append(k, String(v));
    }
  });
  const str = qs.toString();
  return str ? `?${str}` : "";
}

/**
 * Sleep / artificial delay.
 */
export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/**
 * Extract error message from an Axios error response.
 */
export function getErrorMessage(error, fallback = "Something went wrong") {
  return (
    error?.response?.data?.message ||
    error?.response?.data?.detail ||
    error?.message ||
    fallback
  );
}

/**
 * Generate a readable file size string.
 */
export function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/**
 * Pluralize a word based on count.
 */
export function pluralize(count, singular, plural) {
  return count === 1 ? singular : (plural ?? `${singular}s`);
}

/**
 * Deep clone an object via JSON (fast & sufficient for plain data).
 */
export function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj));
}
