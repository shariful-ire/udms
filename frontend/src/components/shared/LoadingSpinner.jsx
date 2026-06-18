"use client";

import { Component } from "react";
import { Loader2, AlertCircle, SearchX, InboxIcon } from "lucide-react";
import { cn } from "@/lib/utils";

// ── LoadingSpinner ────────────────────────────────────────────────────────────
export function LoadingSpinner({ size = "md", className, label }) {
  const sizes = { sm: "h-4 w-4", md: "h-6 w-6", lg: "h-8 w-8", xl: "h-12 w-12" };
  return (
    <div className={cn("flex flex-col items-center justify-center gap-3", className)}>
      <Loader2 className={cn("animate-spin text-primary", sizes[size])} />
      {label && <p className="text-sm text-muted-foreground">{label}</p>}
    </div>
  );
}

export function PageLoader({ label = "Loading…" }) {
  return (
    <div className="flex h-[60vh] items-center justify-center">
      <LoadingSpinner size="lg" label={label} />
    </div>
  );
}

export function EmptyState({ icon: Icon = InboxIcon, title = "Nothing here", description, action, className }) {
  return (
    <div className={cn("flex flex-col items-center justify-center py-16 px-4 text-center", className)}>
      <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-muted">
        <Icon className="h-7 w-7 text-muted-foreground" />
      </div>
      <h3 className="mb-1 text-sm font-semibold">{title}</h3>
      {description && <p className="mb-4 max-w-xs text-sm text-muted-foreground">{description}</p>}
      {action}
    </div>
  );
}

export function NoResultsState({ query, onClear }) {
  return (
    <EmptyState
      icon={SearchX}
      title="No results found"
      description={query ? `No results for "${query}". Try a different search term.` : "No results match your filters."}
      action={onClear && (
        <button onClick={onClear} className="rounded-lg border border-input px-4 py-2 text-sm font-medium hover:bg-accent transition-colors">
          Clear filters
        </button>
      )}
    />
  );
}

export function SkeletonTable({ rows = 5, cols = 5 }) {
  return (
    <div className="rounded-xl border overflow-hidden">
      <div className="flex items-center gap-4 border-b bg-muted/40 px-4 py-3">
        {Array.from({ length: cols }).map((_, i) => (
          <div key={i} className="skeleton h-3 rounded flex-1" style={{ maxWidth: i === 0 ? 120 : undefined }} />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, row) => (
        <div key={row} className="flex items-center gap-4 border-b last:border-none px-4 py-3.5">
          {Array.from({ length: cols }).map((_, col) => (
            <div key={col} className="skeleton h-4 rounded flex-1" style={{ opacity: 1 - row * 0.12 }} />
          ))}
        </div>
      ))}
    </div>
  );
}

export function SkeletonCard({ className }) {
  return (
    <div className={cn("rounded-xl border p-5 space-y-3", className)}>
      <div className="skeleton h-4 w-1/3 rounded" />
      <div className="skeleton h-8 w-1/2 rounded" />
      <div className="skeleton h-3 w-2/3 rounded" />
    </div>
  );
}

export function PageContainer({ children, className }) {
  return (
    <main className={cn("flex flex-col gap-6 p-4 sm:p-6 lg:p-8 page-enter", className)}>
      {children}
    </main>
  );
}

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) { return { hasError: true, error }; }
  componentDidCatch(error, info) { console.error("[ErrorBoundary]", error, info); }
  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;
      return (
        <div className="flex flex-col items-center justify-center gap-4 py-16 px-4 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-destructive/10">
            <AlertCircle className="h-7 w-7 text-destructive" />
          </div>
          <div className="space-y-1">
            <h3 className="font-semibold">Something went wrong</h3>
            <p className="text-sm text-muted-foreground">{this.state.error?.message ?? "An unexpected error occurred."}</p>
          </div>
          <button onClick={() => this.setState({ hasError: false, error: null })} className="rounded-lg border border-input px-4 py-2 text-sm font-medium hover:bg-accent transition-colors">
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
