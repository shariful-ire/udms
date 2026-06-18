"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { PER_PAGE_OPTIONS } from "@/lib/constants";

/**
 * Pagination
 *
 * @param {number} page — Current page (1-indexed)
 * @param {number} totalPages
 * @param {number} total — Total record count
 * @param {number} perPage
 * @param {function} onPageChange — (newPage: number) => void
 * @param {function} [onPerPageChange] — (newPerPage: number) => void
 * @param {string} [className]
 */
export function Pagination({
  // Modern API: pass meta object + setPage/setPerPage from usePagination
  meta,
  setPage,
  setPerPage,
  // Legacy / direct API
  page: pageProp,
  totalPages: totalPagesProp,
  total: totalProp,
  perPage: perPageProp,
  onPageChange,
  onPerPageChange,
  className,
}) {
  const page = pageProp;
  const totalPages = meta?.total_pages ?? totalPagesProp;
  const total = meta?.total ?? totalProp;
  const perPage = meta?.per_page ?? perPageProp;
  const handlePageChange = setPage ?? onPageChange;
  const handlePerPageChange = setPerPage ?? onPerPageChange;

  if (!totalPages || totalPages <= 0) return null;

  const from = (page - 1) * perPage + 1;
  const to = Math.min(page * perPage, total);

  // Build page numbers to show (window of 5 centered on current)
  const buildPages = () => {
    const pages = [];
    const delta = 2;
    const left = Math.max(1, page - delta);
    const right = Math.min(totalPages, page + delta);

    if (left > 1) { pages.push(1); if (left > 2) pages.push("…"); }
    for (let i = left; i <= right; i++) pages.push(i);
    if (right < totalPages) { if (right < totalPages - 1) pages.push("…"); pages.push(totalPages); }

    return pages;
  };

  const btnBase =
    "flex h-8 min-w-8 items-center justify-center rounded-md text-sm transition-colors disabled:pointer-events-none disabled:opacity-40";

  return (
    <div
      className={cn(
        "flex flex-col sm:flex-row items-center justify-between gap-4 pt-4",
        className
      )}
    >
      {/* Record count */}
      <p className="text-sm text-muted-foreground">
        Showing {from}–{to} of {total} results
      </p>

      <div className="flex items-center gap-4">
        {/* Per page selector */}
        {handlePerPageChange && (
          <div className="flex items-center gap-2 text-sm">
            <span className="text-muted-foreground">Rows:</span>
            <select
              value={perPage}
              onChange={(e) => handlePerPageChange(Number(e.target.value))}
              className="h-8 rounded-md border border-input bg-background px-2 text-sm outline-none focus:ring-2 focus:ring-ring"
            >
              {PER_PAGE_OPTIONS.map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </div>
        )}

        {/* Page buttons */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => handlePageChange(page - 1)}
            disabled={page <= 1}
            className={cn(btnBase, "border border-input hover:bg-muted px-2")}
            aria-label="Previous page"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>

          {buildPages().map((p, i) =>
            p === "…" ? (
              <span key={`ellipsis-${i}`} className="flex h-8 w-8 items-center justify-center text-muted-foreground text-sm">
                …
              </span>
            ) : (
              <button
                key={p}
                onClick={() => handlePageChange(p)}
                disabled={p === page}
                className={cn(
                  btnBase,
                  p === page
                    ? "bg-primary text-primary-foreground font-medium"
                    : "border border-input hover:bg-muted"
                )}
                aria-label={`Page ${p}`}
                aria-current={p === page ? "page" : undefined}
              >
                {p}
              </button>
            )
          )}

          <button
            onClick={() => handlePageChange(page + 1)}
            disabled={page >= totalPages}
            className={cn(btnBase, "border border-input hover:bg-muted px-2")}
            aria-label="Next page"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default Pagination;
