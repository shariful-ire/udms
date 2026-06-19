"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, Pencil } from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";
import { earningsApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { usePagination } from "@/lib/hooks/usePagination";
import { formatDate, formatCurrency, getErrorMessage } from "@/lib/utils";
import { EARNING_CATEGORIES } from "@/lib/constants";
import { PageContainer, SkeletonTable, EmptyState } from "@/components/shared/LoadingSpinner";
import { PageHeader } from "@/components/layout/PageHeader";
import { DataTable } from "@/components/tables/DataTable";
import { Pagination } from "@/components/tables/Pagination";
import { ConfirmModal } from "@/components/modals/ConfirmModal";

export default function EarningsPage() {
  const qc = useQueryClient();
  const { page, perPage, params, setPage, setPerPage } = usePagination();
  const [category, setCategory] = useState("");
  const [deleteId, setDeleteId] = useState(null);

  const qParams = { ...params, category };

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.earnings.list(qParams),
    queryFn: () => earningsApi.list(qParams).then((r) => r.data),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => earningsApi.delete(id),
    onSuccess: () => {
      toast.success("Earning deleted");
      qc.invalidateQueries({ queryKey: ["earnings"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      setDeleteId(null);
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const columns = [
    { key: "date", label: "Date", render: (e) => <span className="font-medium text-sm">{formatDate(e.date)}</span> },
    { key: "description", label: "Description", render: (e) => <span className="font-medium text-sm">{e.description}</span> },
    {
      key: "category", label: "Category",
      render: (e) => {
        const cat = EARNING_CATEGORIES.find((c) => c.value === e.category);
        return <span className="flex items-center gap-1.5 text-sm">{cat?.icon} {cat?.label ?? e.category}</span>;
      }
    },
    { key: "notes", label: "Notes", render: (e) => <span className="text-sm max-w-xs truncate block">{e.notes ?? "—"}</span> },
    { key: "amount", label: "Amount", render: (e) => <span className="font-semibold text-sm text-green-600">{formatCurrency(e.amount)}</span> },
    {
      key: "actions", label: "",
      render: (e) => (
        <div className="flex gap-1 justify-end">
          <Link href={`/earnings/${e.id}`}
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
        title="Earnings"
        description="Track dining hall income and revenue"
        action={
          <Link href="/earnings/create"
            className="flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors">
            <Plus className="h-4 w-4" /> Add Earning
          </Link>
        }
      />

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <select value={category} onChange={(e) => { setCategory(e.target.value); setPage(1); }}
          className="rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring">
          <option value="">All Categories</option>
          {EARNING_CATEGORIES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
        </select>
      </div>

      {/* Table */}
      {isLoading ? (
        <SkeletonTable rows={8} cols={6} />
      ) : !data?.data?.length ? (
        <EmptyState title="No earnings recorded" description="Start tracking your dining hall revenue." />
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
        title="Delete this earning?"
        description="This action cannot be undone."
        confirmLabel="Delete"
        variant="danger"
      />
    </PageContainer>
  );
}
