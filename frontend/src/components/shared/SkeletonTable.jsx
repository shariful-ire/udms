import { cn } from "@/lib/utils";

/**
 * Skeleton pulse block — reusable primitive.
 */
export function Skeleton({ className }) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-md bg-muted",
        className
      )}
    />
  );
}

/**
 * SkeletonTable
 *
 * Renders a shimmer placeholder that mimics a data table.
 *
 * @param {number} [rows=5] — Number of skeleton rows
 * @param {number} [cols=5] — Number of columns
 * @param {boolean} [showHeader=true] — Whether to render the header row
 */
export function SkeletonTable({ rows = 5, cols = 5, showHeader = true }) {
  const colWidths = [
    "w-8",      // checkbox / index
    "w-32",     // name
    "w-24",     // ID / code
    "w-20",     // status badge
    "w-16",     // actions
  ];

  return (
    <div className="rounded-xl border bg-card overflow-hidden">
      <table className="w-full text-sm">
        {showHeader && (
          <thead>
            <tr className="border-b bg-muted/30">
              {Array.from({ length: cols }).map((_, i) => (
                <th key={i} className="h-10 px-4 text-left">
                  <Skeleton className={cn("h-4", colWidths[i] ?? "w-24")} />
                </th>
              ))}
            </tr>
          </thead>
        )}
        <tbody>
          {Array.from({ length: rows }).map((_, r) => (
            <tr key={r} className="border-b last:border-0">
              {Array.from({ length: cols }).map((_, c) => (
                <td key={c} className="px-4 py-3">
                  <Skeleton
                    className={cn(
                      "h-4",
                      c === 0 ? "w-8" : c === cols - 1 ? "w-16" : "w-full max-w-[120px]"
                    )}
                  />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/**
 * SkeletonCard — single card shimmer.
 */
export function SkeletonCard({ className }) {
  return (
    <div className={cn("rounded-xl border bg-card p-6 space-y-3", className)}>
      <Skeleton className="h-4 w-1/3" />
      <Skeleton className="h-8 w-1/2" />
      <Skeleton className="h-3 w-2/3" />
    </div>
  );
}

/**
 * SkeletonStatCards — row of 4 stat card shimmers.
 */
export function SkeletonStatCards({ count = 4 }) {
  return (
    <div className={`grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-${count}`}>
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}

export default SkeletonTable;
