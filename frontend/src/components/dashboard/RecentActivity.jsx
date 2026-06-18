"use client";

import { formatRelative } from "@/lib/utils";
import { cn } from "@/lib/utils";
import Avatar from "@/components/shared/Avatar";

/**
 * RecentActivity
 *
 * @param {Array<{id, actor_name, action, detail, created_at}>} items
 * @param {boolean} [isLoading]
 */
export function RecentActivity({ items = [], isLoading = false, className }) {
  if (isLoading) {
    return (
      <div className={cn("rounded-xl border bg-card p-6", className)}>
        <h3 className="font-semibold mb-4">Recent Activity</h3>
        <div className="space-y-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex items-start gap-3 animate-pulse">
              <div className="h-8 w-8 rounded-full bg-muted shrink-0" />
              <div className="flex-1 space-y-1.5">
                <div className="h-3 w-3/4 rounded bg-muted" />
                <div className="h-3 w-1/2 rounded bg-muted" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!items.length) {
    return (
      <div className={cn("rounded-xl border bg-card p-6", className)}>
        <h3 className="font-semibold mb-4">Recent Activity</h3>
        <p className="text-sm text-muted-foreground text-center py-8">No recent activity.</p>
      </div>
    );
  }

  return (
    <div className={cn("rounded-xl border bg-card p-6", className)}>
      <h3 className="font-semibold mb-4">Recent Activity</h3>
      <div className="space-y-4">
        {items.map((item) => (
          <div key={item.id} className="flex items-start gap-3">
            <Avatar name={item.actor_name} size="sm" className="shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <p className="text-sm">
                <span className="font-medium">{item.actor_name}</span>{" "}
                <span className="text-muted-foreground">{item.action}</span>
                {item.detail && (
                  <span className="text-foreground"> — {item.detail}</span>
                )}
              </p>
              <p className="text-xs text-muted-foreground mt-0.5">
                {formatRelative(item.created_at)}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default RecentActivity;
