"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, Pencil } from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";
import { expensesApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { useDebounce } from "@/lib/hooks/useDebounce";
import { usePagination } from "@/lib/hooks/usePagination";
import { formatDate, formatCurrency, getErrorMessage } from "@/lib/utils";
import { EXPENSE_CATEGORIES } from "@/lib/constants";
import { PageContainer, SkeletonTable, EmptyState } from "@/components/shared/LoadingSpinner";
import { PageHeader } from "@/components/layout/PageHeader";
import { SearchInput } from "@/components/shared/SearchInput";
import { DateRangePicker } from "@/components/shared/SearchInput";
import { DataTable } from "@/components/tables/DataTable";
import { Pagination } from "@/components/tables/Pagination";
import { ConfirmModal } from "@/components/modals/ConfirmModal";
import { ExpensePieChart } from "@/components/charts/ExpensePieChart";

export default function ExpensesPage() {
  const qc = useQueryClient();
  const { page, perPage, params, setPage, setPerPage } = usePagination();
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [deleteId, setDeleteId] = useState(null);
  const debouncedSearch = useDebounce(search, 400);

  const qParams = {
    ...params,
    search: debouncedSearch,
    category,
    ...(startDate && { start_date: startDate }),
    ...(endDate && { end_date: endDate }),
  };

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.expenses.list(qParams),
    queryFn: () => expensesApi.list(qParams).then((r) => r.data),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => expensesApi.delete(id),
    onSuccess: () => { toast.success("Expense deleted"); qc.invalidateQueries({ queryKey: ["expenses"] }); setDeleteId(null); },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const columns = [
    { key: "date", label: "Date", render: (e) => <span className="font-medium text-sm">{formatDate(e.date)}</span> },
    { key: "name", label: "Name", render: (e) => <span className="font-medium text-sm">{e.name}</span> },
    {
      key: "category", label: "Category",
      render: (e) => {
        const cat = EXPENSE_CATEGORIES.find((c) => c.value === e.category);
        return <span className="flex items-center gap-1.5 text-sm">{cat?.icon} {cat?.label ?? e.category}</span>;
      }
    },
    { key: "description", label: "Description", render: (e) => <span className="text-sm max-w-xs truncate block">{e.description ?? "—"}</span> },
    { key: "amount", label: "Amount", render: (e) => <span className="font-semibold text-sm">{formatCurrency(e.amount)}</span> },
    {
      key: "actions", label: "",
      render: (e) => (
        <div className="flex gap-1 justify-end">
          <Link href={`/expenses/${e.id}`}
            className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent transition-colors">
            <Pencil className="h-4 w-4" />
          </Link>
          <button onClick={() => setDeleteId(e.id)}
            className="rounded-lg p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors">
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      )
    },
  ];

  return (
    <PageContainer>
      <PageHeader
        title="Expenses"
        description="Track and manage dining hall expenses"
        action={
          <Link href="/expenses/create"
            className="flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors">
            <Plus className="h-4 w-4" /> Add Expense
          </Link>
        }
      />

      {/* Summary strip */}
      {data?.meta?.total_amount != null && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-xl border bg-card p-4">
            <p className="text-xs text-muted-foreground">Total Expenses</p>
            <p className="text-xl font-bold mt-1">{formatCurrency(data.meta.total_amount)}</p>
          </div>
          {data?.meta?.by_category?.slice(0, 3).map((c) => (
            <div key={c.category} className="rounded-xl border bg-card p-4">
              <p className="text-xs text-muted-foreground">{EXPENSE_CATEGORIES.find((ec) => ec.value === c.category)?.label ?? c.category}</p>
              <p className="text-xl font-bold mt-1">{formatCurrency(c.amount)}</p>
            </div>
          ))}
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <SearchInput value={search} onSearch={setSearch} placeholder="Search description…" className="w-56" />
        <select value={category} onChange={(e) => { setCategory(e.target.value); setPage(1); }}
          className="rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring">
          <option value="">All Categories</option>
          {EXPENSE_CATEGORIES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
        </select>
        <DateRangePicker startDate={startDate} endDate={endDate}
          onStartChange={(v) => { setStartDate(v); setPage(1); }}
          onEndChange={(v) => { setEndDate(v); setPage(1); }} />
      </div>

      {/* Table */}
      {isLoading ? (
        <SkeletonTable rows={8} cols={6} />
      ) : !data?.data?.length ? (
        <EmptyState title="No expenses recorded" description="Start tracking your dining hall expenses." />
      ) : (
        <>
          <DataTable columns={columns} data={data.data} />
          <Pagination meta={data.meta} page={page} perPage={perPage} setPage={setPage} setPerPage={setPerPage} />
        </>
      )}

      <ConfirmModal
        open={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={() => deleteMutation.mutate(deleteId)}
        isLoading={deleteMutation.isPending}
        title="Delete this expense?"
        description="This action cannot be undone."
        confirmLabel="Delete"
        variant="danger"
      />
    </PageContainer>
  );
}
