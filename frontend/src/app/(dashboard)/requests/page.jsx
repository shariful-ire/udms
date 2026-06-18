"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";
import { requestsApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { usePagination } from "@/lib/hooks/usePagination";
import { usePermissions } from "@/lib/hooks/usePermissions";
import { formatDate, formatCurrency, getErrorMessage } from "@/lib/utils";
import { REQUEST_STATUS_LABELS, REQUEST_STATUS_COLORS } from "@/lib/constants";
import { PageContainer, SkeletonTable, EmptyState } from "@/components/shared/LoadingSpinner";
import { PageHeader } from "@/components/layout/PageHeader";
import { DataTable } from "@/components/tables/DataTable";
import { Pagination } from "@/components/tables/Pagination";
import { StatusBadge } from "@/components/shared/Badge";
import { RequestReviewModal } from "@/components/modals/UserModal";
import { RequestForm } from "@/components/forms/MenuForm";
import { Modal } from "@/components/modals/UserModal";

export default function RequestsPage() {
  const qc = useQueryClient();
  const { isManager, isProvost, isNonCustomer } = usePermissions();
  const canReview = isManager || isProvost;

  const { page, perPage, params, setPage, setPerPage } = usePagination();
  const [statusFilter, setStatusFilter] = useState(canReview ? "PENDING_APPROVAL" : "");
  const [reviewTarget, setReviewTarget] = useState(null);
  const [showNewRequest, setShowNewRequest] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.requests.list({ ...params, status: statusFilter }),
    queryFn: () => requestsApi.list({ ...params, status: statusFilter }).then((r) => r.data),
  });

  const createMutation = useMutation({
    mutationFn: (data) => requestsApi.create(data),
    onSuccess: () => {
      toast.success("Request submitted! Please complete the payment.");
      qc.invalidateQueries({ queryKey: ["requests"] });
      setShowNewRequest(false);
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const approveMutation = useMutation({
    mutationFn: (id) => requestsApi.approve(id),
    onSuccess: () => { toast.success("Request approved"); qc.invalidateQueries({ queryKey: ["requests"] }); setReviewTarget(null); },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const rejectMutation = useMutation({
    mutationFn: ({ id, reason }) => requestsApi.reject(id, { reason }),
    onSuccess: () => { toast.success("Request rejected"); qc.invalidateQueries({ queryKey: ["requests"] }); setReviewTarget(null); },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const STATUS_FILTERS = [
    { value: "", label: "All" },
    { value: "PENDING_PAYMENT", label: "Pending Payment" },
    { value: "PENDING_APPROVAL", label: "Pending Approval" },
    { value: "APPROVED", label: "Approved" },
    { value: "REJECTED", label: "Rejected" },
  ];

  const columns = [
    ...(canReview ? [{
      key: "user", label: "Student",
      render: (r) => <div><p className="font-medium text-sm">{r.user?.full_name}</p><p className="text-xs text-muted-foreground">{r.user?.student_id}</p></div>
    }] : []),
    { key: "date", label: "Date", render: (r) => <span className="text-sm">{formatDate(r.date)}</span> },
    { key: "meal_type", label: "Meal", render: (r) => <span className="text-sm font-medium">{r.meal_type}</span> },
    { key: "amount", label: "Payment", render: (r) => r.payment ? <span className="text-sm">{formatCurrency(r.payment.amount)}</span> : <span className="text-sm text-muted-foreground">Pending</span> },
    { key: "status", label: "Status", render: (r) => <StatusBadge status={r.status} type="request" /> },
    { key: "submitted", label: "Submitted", render: (r) => <span className="text-sm text-muted-foreground">{formatDate(r.created_at)}</span> },
    ...(canReview ? [{
      key: "actions", label: "",
      render: (r) => r.status === "PENDING_APPROVAL" ? (
        <button onClick={() => setReviewTarget(r)}
          className="rounded-lg bg-primary px-3 py-1.5 text-xs font-semibold text-primary-foreground hover:bg-primary/90 transition-colors">
          Review
        </button>
      ) : (
        <Link href={`/requests/${r.id}`} className="text-xs text-primary hover:underline underline-offset-4">View</Link>
      )
    }] : [{
      key: "actions", label: "",
      render: (r) => <Link href={`/requests/${r.id}`} className="text-xs text-primary hover:underline underline-offset-4">View</Link>
    }]),
  ];

  return (
    <PageContainer>
      <PageHeader
        title={canReview ? "Membership Requests" : "My Requests"}
        description={canReview ? "Review and process customer enrollment requests" : "Track your dining membership requests"}
        action={isNonCustomer && (
          <button onClick={() => setShowNewRequest(true)}
            className="flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors">
            <Plus className="h-4 w-4" /> New Request
          </button>
        )}
      />

      <div className="flex gap-2">
        {STATUS_FILTERS.map((f) => (
          <button key={f.value} onClick={() => { setStatusFilter(f.value); setPage(1); }}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${statusFilter === f.value ? "bg-primary text-primary-foreground" : "border border-input hover:bg-accent"}`}>
            {f.label}
          </button>
        ))}
      </div>

      {isLoading ? <SkeletonTable rows={6} cols={canReview ? 6 : 5} /> : !data?.data?.length ? (
        <EmptyState title="No requests found" description={isNonCustomer ? "Submit a request to join the dining program." : "No requests match this filter."} />
      ) : (
        <>
          <DataTable columns={columns} data={data.data} />
          <Pagination meta={data.meta} page={page} perPage={perPage} setPage={setPage} setPerPage={setPerPage} />
        </>
      )}

      {/* New request modal */}
      <Modal open={showNewRequest} onClose={() => setShowNewRequest(false)} title="Submit Meal Request">
        <RequestForm onSubmit={createMutation.mutate} isLoading={createMutation.isPending} />
      </Modal>

      {/* Review modal */}
      <RequestReviewModal
        open={!!reviewTarget}
        onClose={() => setReviewTarget(null)}
        request={reviewTarget}
        onApprove={(id) => approveMutation.mutate(id)}
        onReject={(id, reason) => rejectMutation.mutate({ id, reason })}
        isLoading={approveMutation.isPending || rejectMutation.isPending}
      />
    </PageContainer>
  );
}
