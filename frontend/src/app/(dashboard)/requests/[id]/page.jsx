"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, CheckCircle2, XCircle } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";
import { requestsApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { formatDate, formatDatetime, formatCurrency, getErrorMessage } from "@/lib/utils";
import { PageContainer, PageLoader } from "@/components/shared/LoadingSpinner";
import { PageHeader } from "@/components/layout/PageHeader";
import { StatusBadge, RoleBadge } from "@/components/shared/Badge";
import { Avatar } from "@/components/shared/Avatar";
import { PaymentForm } from "@/components/forms/MenuForm";
import { usePermissions } from "@/lib/hooks/usePermissions";
import { useAuthStore } from "@/store/authStore";
import { useState } from "react";
import { Modal } from "@/components/modals/UserModal";
import { ConfirmModal } from "@/components/modals/ConfirmModal";

export default function RequestDetailPage({ params }) {
  const { id } = params;
  const qc = useQueryClient();
  const { isManager, isProvost } = usePermissions();
  const { user: currentUser } = useAuthStore();
  const [showPayment, setShowPayment] = useState(false);
  const [showReject, setShowReject] = useState(false);
  const [rejectReason, setRejectReason] = useState("");

  const { data: request, isLoading } = useQuery({
    queryKey: queryKeys.requests.detail(id),
    queryFn: () => requestsApi.get(id).then((r) => r.data.data),
  });

  const paymentMutation = useMutation({
    mutationFn: (data) => requestsApi.submitPayment(id, data),
    onSuccess: () => { toast.success("Payment submitted!"); qc.invalidateQueries({ queryKey: queryKeys.requests.detail(id) }); setShowPayment(false); },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const approveMutation = useMutation({
    mutationFn: () => requestsApi.approve(id),
    onSuccess: () => { toast.success("Request approved"); qc.invalidateQueries({ queryKey: queryKeys.requests.detail(id) }); },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const rejectMutation = useMutation({
    mutationFn: () => requestsApi.reject(id, { reason: rejectReason }),
    onSuccess: () => { toast.success("Request rejected"); qc.invalidateQueries({ queryKey: queryKeys.requests.detail(id) }); setShowReject(false); },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  if (isLoading) return <PageLoader />;
  if (!request) return null;

  const canReview = (isManager || isProvost) && request.status === "PENDING_APPROVAL";
  const isOwner = currentUser?.id === request.user?.id;
  const canPay = isOwner && request.status === "PENDING_PAYMENT";

  return (
    <PageContainer>
      <PageHeader
        title="Request Details"
        description={`Request #${id.slice(0, 8).toUpperCase()}`}
        action={
          <Link href="/requests"
            className="flex items-center gap-1.5 rounded-lg border border-input px-3 py-2 text-sm font-medium hover:bg-accent transition-colors">
            <ArrowLeft className="h-4 w-4" /> Back
          </Link>
        }
      />

      <div className="grid gap-6 lg:grid-cols-2 max-w-4xl">
        {/* Request info */}
        <div className="rounded-xl border bg-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">Request Information</h3>
            <StatusBadge status={request.status} type="request" />
          </div>

          {(isManager || isProvost) && (
            <div className="flex items-center gap-3 pb-3 border-b">
              <Avatar src={request.user?.avatar_url} name={request.user?.full_name} size="sm" />
              <div>
                <p className="font-medium text-sm">{request.user?.full_name}</p>
                <p className="text-xs text-muted-foreground">{request.user?.student_id} · {request.user?.department}</p>
              </div>
            </div>
          )}

          <div className="space-y-3 text-sm">
            {[
              { label: "Meal Date", value: formatDate(request.date) },
              { label: "Meal Type", value: request.meal_type },
              { label: "Submitted", value: formatDatetime(request.created_at) },
              { label: "Hall", value: request.user?.hall_name ?? "—" },
              { label: "Batch", value: request.user?.batch ?? "—" },
            ].map(({ label, value }) => (
              <div key={label} className="flex justify-between">
                <span className="text-muted-foreground">{label}</span>
                <span className="font-medium">{value}</span>
              </div>
            ))}
            {request.note && (
              <div>
                <span className="text-muted-foreground">Note</span>
                <p className="mt-1 text-sm">{request.note}</p>
              </div>
            )}
            {request.rejection_reason && (
              <div className="rounded-lg bg-destructive/10 p-3">
                <p className="text-xs font-semibold text-destructive mb-1">Rejection Reason</p>
                <p className="text-sm">{request.rejection_reason}</p>
              </div>
            )}
          </div>

          {/* Manager actions */}
          {canReview && (
            <div className="flex gap-2 pt-2 border-t">
              <button onClick={() => approveMutation.mutate()}
                disabled={approveMutation.isPending}
                className="flex-1 flex items-center justify-center gap-1.5 rounded-lg bg-green-600 px-3 py-2 text-sm font-semibold text-white hover:bg-green-700 disabled:opacity-60 transition-colors">
                <CheckCircle2 className="h-4 w-4" /> Approve
              </button>
              <button onClick={() => setShowReject(true)}
                className="flex-1 flex items-center justify-center gap-1.5 rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm font-semibold text-destructive hover:bg-destructive/20 transition-colors">
                <XCircle className="h-4 w-4" /> Reject
              </button>
            </div>
          )}
        </div>

        {/* Payment info */}
        <div className="rounded-xl border bg-card p-6 space-y-4">
          <h3 className="font-semibold">Payment Information</h3>
          {request.payment ? (
            <div className="space-y-3 text-sm">
              {[
                { label: "Amount", value: formatCurrency(request.payment.amount) },
                { label: "Method", value: request.payment.payment_method },
                { label: "Date", value: formatDate(request.payment.created_at) },
                { label: "Reference No.", value: request.payment.reference_no ?? "—" },
              ].map(({ label, value }) => (
                <div key={label} className="flex justify-between">
                  <span className="text-muted-foreground">{label}</span>
                  <span className="font-medium">{value}</span>
                </div>
              ))}
            </div>
          ) : canPay ? (
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">Payment is required to proceed with your request.</p>
              <button onClick={() => setShowPayment(true)}
                className="w-full rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors">
                Submit Payment
              </button>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No payment recorded yet.</p>
          )}
        </div>
      </div>

      {/* Payment modal */}
      <Modal open={showPayment} onClose={() => setShowPayment(false)} title="Submit Payment">
        <PaymentForm onSubmit={paymentMutation.mutate} isLoading={paymentMutation.isPending} />
      </Modal>

      {/* Reject modal */}
      <ConfirmModal
        open={showReject}
        onClose={() => setShowReject(false)}
        onConfirm={() => rejectMutation.mutate()}
        isLoading={rejectMutation.isPending}
        title="Reject this request?"
        variant="danger"
        confirmLabel="Reject"
      >
        <textarea value={rejectReason} onChange={(e) => setRejectReason(e.target.value)}
          rows={3} placeholder="Reason for rejection…"
          className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring mt-3" />
      </ConfirmModal>
    </PageContainer>
  );
}
