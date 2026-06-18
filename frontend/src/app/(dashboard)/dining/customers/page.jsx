"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { UserMinus, UserPlus } from "lucide-react";
import { toast } from "sonner";
import { customersApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { useDebounce } from "@/lib/hooks/useDebounce";
import { usePagination } from "@/lib/hooks/usePagination";
import { formatDate, getErrorMessage } from "@/lib/utils";
import { PageContainer, SkeletonTable, EmptyState } from "@/components/shared/LoadingSpinner";
import { PageHeader } from "@/components/layout/PageHeader";
import { SearchInput } from "@/components/shared/SearchInput";
import { DataTable } from "@/components/tables/DataTable";
import { Pagination } from "@/components/tables/Pagination";
import { Avatar } from "@/components/shared/Avatar";
import { ConfirmModal } from "@/components/modals/ConfirmModal";

export default function DiningCustomersPage() {
  const qc = useQueryClient();
  const { page, perPage, params, setPage, setPerPage } = usePagination();
  const [search, setSearch] = useState("");
  const [confirmModal, setConfirmModal] = useState(null);
  const debouncedSearch = useDebounce(search, 400);

  const qParams = { ...params, search: debouncedSearch };

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.customers.list(qParams),
    queryFn: () => customersApi.list(qParams).then((r) => r.data),
  });

  const removeMutation = useMutation({
    mutationFn: (userId) => customersApi.remove(userId),
    onSuccess: () => { toast.success("Customer removed from dining program"); qc.invalidateQueries({ queryKey: ["customers"] }); setConfirmModal(null); },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const columns = [
    {
      key: "user", label: "Student",
      render: (c) => (
        <div className="flex items-center gap-3">
          <Avatar src={c.profile_image} name={c.full_name} size="sm" />
          <div>
            <p className="font-medium text-sm">{c.full_name}</p>
            <p className="text-xs text-muted-foreground">{c.email}</p>
          </div>
        </div>
      )
    },
    { key: "student_id", label: "Student ID", render: (c) => <span className="font-mono text-sm">{c.student_id}</span> },
    { key: "department", label: "Department", render: (c) => <span className="text-sm">{c.department}</span> },
    { key: "hall", label: "Hall", render: (c) => <span className="text-sm text-muted-foreground">{c.hall_name}</span> },
    { key: "enrolled", label: "Joined", render: (c) => <span className="text-sm text-muted-foreground">{formatDate(c.created_at)}</span> },
    {
      key: "actions", label: "",
      render: (c) => (
        <button onClick={() => setConfirmModal(c)}
          className="rounded-lg p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
          title="Remove from dining program">
          <UserMinus className="h-4 w-4" />
        </button>
      )
    },
  ];

  return (
    <PageContainer>
      <PageHeader title="Dining Customers" description="Students currently enrolled in the dining program" />

      <SearchInput value={search} onSearch={setSearch} placeholder="Search by name, student ID…" className="w-64" />

      {isLoading ? <SkeletonTable rows={8} cols={6} /> : !data?.data?.length ? (
        <EmptyState icon={UserPlus} title="No customers enrolled" description="Approve membership requests to add customers." />
      ) : (
        <>
          <DataTable columns={columns} data={data.data} />
          <Pagination meta={data.meta} page={page} perPage={perPage} setPage={setPage} setPerPage={setPerPage} />
        </>
      )}

      <ConfirmModal
        open={!!confirmModal}
        onClose={() => setConfirmModal(null)}
        onConfirm={() => removeMutation.mutate(confirmModal.id)}
        isLoading={removeMutation.isPending}
        title="Remove this customer?"
        description={`${confirmModal?.full_name} will be removed from the dining program and their role will revert to Student.`}
        confirmLabel="Remove"
        variant="danger"
      />
    </PageContainer>
  );
}
