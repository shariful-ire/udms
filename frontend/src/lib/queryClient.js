import { QueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { getErrorMessage } from "@/lib/utils";

// ── Global error handler ──────────────────────────────────────────────────────
const onError = (error) => {
  // Ignore 401 — handled by Axios interceptor (token refresh / redirect)
  if (error?.response?.status === 401) return;
  // Ignore 404 — components handle empty states themselves
  if (error?.response?.status === 404) return;

  const message = getErrorMessage(error);
  toast.error(message, { duration: 5000 });
};

// ── Query client ──────────────────────────────────────────────────────────────
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // 30-second stale time — data considered fresh for 30 s
      staleTime: 30 * 1000,
      // 5-minute cache time — data kept in memory for 5 m after component unmounts
      gcTime: 5 * 60 * 1000,
      // Retry once (not 3 times) to avoid hammering a down API
      retry: (failureCount, error) => {
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false; // Never retry client errors (400-499)
        }
        return failureCount < 1; // Retry server errors once
      },
      refetchOnWindowFocus: false, // Don't refetch on window focus (reduces noise)
      refetchOnMount: true,
      onError,
    },
    mutations: {
      retry: 0,
      onError,
    },
  },
});

// ── Query key factories ────────────────────────────────────────────────────────
// Centralised keys prevent typos and make cache invalidation predictable.

export const queryKeys = {
  // Auth
  me: ["me"],

  // Users
  users: {
    all: ["users"],
    list: (params) => ["users", "list", params],
    detail: (id) => ["users", "detail", id],
    stats: ["users", "stats"],
    recent: (params) => ["users", "recent", params],
  },

  // Profile
  profile: ["profile"],

  // Dining schedules & menus
  dining: {
    schedules: ["dining", "schedules"],
    menus: (params) => ["dining", "menus", params],
    menuForDate: (date) => ["dining", "menus", "date", date],
  },

  // Customers
  customers: {
    list: (params) => ["customers", "list", params],
  },

  // Meals
  meals: {
    today: ["meals", "today"],
    history: (params) => ["meals", "history", params],
    summary: (params) => ["meals", "summary", params],
  },

  // Requests
  requests: {
    list: (params) => ["requests", "list", params],
    detail: (id) => ["requests", "detail", id],
  },

  // Expenses
  expenses: {
    list: (params) => ["expenses", "list", params],
    detail: (id) => ["expenses", "detail", id],
  },

  // Reports
  reports: {
    daily: (params) => ["reports", "daily", params],
    weekly: (params) => ["reports", "weekly", params],
    monthly: (params) => ["reports", "monthly", params],
    yearly: (params) => ["reports", "yearly", params],
  },

  // Audit
  audit: {
    list: (params) => ["audit", "list", params],
    detail: (id) => ["audit", "detail", id],
  },

  // Settings
  settings: ["settings"],
};

export default queryClient;
