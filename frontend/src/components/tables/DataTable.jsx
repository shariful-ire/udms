"use client";

import { useState } from "react";
import { ChevronUp, ChevronDown, ChevronsUpDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { EmptyState } from "@/components/shared/EmptyState";
import { SkeletonTable } from "@/components/shared/SkeletonTable";

/**
 * DataTable
 *
 * @param {Array<{key, label, render?, sortable?, align?, className?}>} columns
 * @param {Array<object>} data
 * @param {string} [rowKey="id"] — Key used for React key prop
 * @param {boolean} [isLoading]
 * @param {string} [emptyTitle]
 * @param {string} [emptyDescription]
 * @param {React.ReactNode} [emptyAction]
 * @param {object} [sort] — { key, direction: "asc"|"desc" }
 * @param {function} [onSort] — Called with new sort { key, direction }
 * @param {string[]} [selectedIds] — Controlled selection
 * @param {function} [onSelectionChange]
 * @param {string} [className]
 */
export function DataTable({
  columns = [],
  data = [],
  rowKey = "id",
  isLoading = false,
  emptyTitle = "No results",
  emptyDescription = "Nothing to display yet.",
  emptyAction,
  sort,
  onSort,
  selectedIds = [],
  onSelectionChange,
  className,
}) {
  const selectable = !!onSelectionChange;

  const handleSort = (key) => {
    if (!onSort) return;
    if (sort?.key === key) {
      onSort({ key, direction: sort.direction === "asc" ? "desc" : "asc" });
    } else {
      onSort({ key, direction: "asc" });
    }
  };

  const toggleAll = (e) => {
    if (!onSelectionChange) return;
    onSelectionChange(e.target.checked ? data.map((r) => r[rowKey]) : []);
  };

  const toggleRow = (id) => {
    if (!onSelectionChange) return;
    onSelectionChange(
      selectedIds.includes(id)
        ? selectedIds.filter((s) => s !== id)
        : [...selectedIds, id]
    );
  };

  if (isLoading) return <SkeletonTable rows={5} cols={columns.length + (selectable ? 1 : 0)} />;

  return (
    <div className={cn("rounded-xl border bg-card overflow-hidden", className)}>
      {data.length === 0 ? (
        <EmptyState
          className="border-none rounded-none"
          title={emptyTitle}
          description={emptyDescription}
          action={emptyAction}
        />
      ) : (
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                {selectable && (
                  <th className="w-10 px-4">
                    <input
                      type="checkbox"
                      checked={selectedIds.length === data.length && data.length > 0}
                      onChange={toggleAll}
                      className="h-4 w-4 rounded border-input accent-primary"
                      aria-label="Select all"
                    />
                  </th>
                )}
                {columns.map((col) => (
                  <th
                    key={col.key}
                    className={cn(
                      col.align === "right" && "text-right",
                      col.align === "center" && "text-center",
                      col.sortable && onSort && "cursor-pointer select-none hover:text-foreground",
                      col.className
                    )}
                    onClick={col.sortable ? () => handleSort(col.key) : undefined}
                  >
                    <span className="inline-flex items-center gap-1">
                      {col.label}
                      {col.sortable && onSort && (
                        <span className="text-muted-foreground/50">
                          {sort?.key === col.key ? (
                            sort.direction === "asc" ? (
                              <ChevronUp className="h-3.5 w-3.5" />
                            ) : (
                              <ChevronDown className="h-3.5 w-3.5" />
                            )
                          ) : (
                            <ChevronsUpDown className="h-3.5 w-3.5" />
                          )}
                        </span>
                      )}
                    </span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row) => {
                const id = row[rowKey];
                const isSelected = selectedIds.includes(id);

                return (
                  <tr
                    key={id}
                    className={cn(isSelected && "bg-primary/5")}
                  >
                    {selectable && (
                      <td className="w-10 px-4">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleRow(id)}
                          className="h-4 w-4 rounded border-input accent-primary"
                          aria-label={`Select row ${id}`}
                        />
                      </td>
                    )}
                    {columns.map((col) => (
                      <td
                        key={col.key}
                        className={cn(
                          col.align === "right" && "text-right",
                          col.align === "center" && "text-center",
                          col.className
                        )}
                      >
                        {col.render
                          ? col.render(row)
                          : (row[col.key] ?? "—")}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default DataTable;
