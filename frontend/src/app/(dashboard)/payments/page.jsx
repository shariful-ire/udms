"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  CheckCircle, Clock, UserCheck, UserX, Eye, RefreshCw,
  FileCheck, AlertCircle, Filter,
} from "lucide-react";
import { toast } from "sonner";
import { memberPaymentsApi, paymentProofsApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { usePermissions } from "@/lib/hooks/usePermissions";
import { formatDate, formatCurrency, getErrorMessage } from "@/lib/utils";
import { PageContainer, SkeletonTable, EmptyState } from "@/components/shared/LoadingSpinner";
import { PageHeader } from "@/components/layout/PageHeader";
import { DataTable } from "@/components/tables/DataTable";
import { Pagination } from "@/components/tables/Pagination";
import { usePagination } from "@/lib/hooks/usePagination";
import { ConfirmModal } from "@/components/modals/ConfirmModal";

const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

function ProofReviewModal({ proof, open, onClose, onApprove, onReject, isLoading }) {
  const [rejectNote, setRejectNote] = useState("");
  if (!proof || !open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <div className="w-full max-w-lg rounded-xl bg-card border p-6 space-y-4 mx-4" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-lg font-semibold">Review Payment Proof</h3>
        <div className="space-y-2 text-sm">
          <p><span className="text-muted-foreground">Type:</span> {proof.proof_type.replace("_", " ")}</p>
          <p><span className="text-muted-foreground">Submitted:</span> {formatDate(proof.created_at)}</p>
          <p><span className="text-muted-foreground">Member:</span> {proof.user?.full_name ?? proof.user_id}</p>
          <div className="rounded-lg border bg-muted/30 p-3 mt-2">
            <p className="text-xs text-muted-foreground mb-1">Proof Content</p>
            {proof.proof_type === "IMAGE" ? (
              <img src={proof.proof_value} alt="Payment proof" className="max-h-48 rounded" />
            ) : (
              <p className="font-mono text-sm break-all">{proof.proof_value}</p>
            )}
          </div>
        </div>
        {proof.status === "SUBMITTED" && (
          <>
            <div>
              <label className="block text-sm font-medium mb-1">Rejection Note (if rejecting)</label>
              <textarea value={rejectNote} onChange={(e) => setRejectNote(e.target.value)} rows={2}
                className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring resize-none"
                placeholder="Reason for rejection..." />
            </div>
            <div className="flex gap-2 justify-end">
              <button onClick={onClose}
                className="rounded-lg border border-input px-4 py-2 text-sm font-medium hover:bg-accent transition-colors">
                Cancel
              </button>
              <button onClick={() => onReject(rejectNote)} disabled={isLoading}
                className="rounded-lg bg-destructive px-4 py-2 text-sm font-semibold text-destructive-foreground hover:bg-destructive/90 transition-colors disabled:opacity-50">
                Reject
              </button>
              <button onClick={onApprove} disabled={isLoading}
                className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50">
                Approve
              </button>
            </div>
          </>
        )}
        {proof.status !== "SUBMITTED" && (
          <div className="flex justify-end">
            <button onClick={onClose}
              className="rounded-lg border border-input px-4 py-2 text-sm font-medium hover:bg-accent transition-colors">
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default function PaymentsPage() {
  const qc = useQueryClient();
  const { isManager, isProvost } = usePermissions();
  const { page, perPage, params, setPage, setPerPage } = usePagination();
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [statusFilter, setStatusFilter] = useState("");
  const [tab, setTab] = useState("payments");
  const [reviewProof, setReviewProof] = useState(null);
  const [submitProofFor, setSubmitProofFor] = useState(null);
  const [proofForm, setProofForm] = useState({ proof_type: "TRANSACTION_ID", proof_value: "" });

  const qParams = { ...params, year, month, status: statusFilter || undefined };

  const { data: paymentsData, isLoading } = useQuery({
    queryKey: queryKeys.memberPayments.list(qParams),
    queryFn: () => memberPaymentsApi.list(qParams).then((r) => r.data),
  });

  const { data: summaryData } = useQuery({
    queryKey: queryKeys.memberPayments.summary({ year, month }),
    queryFn: () => memberPaymentsApi.summary({ year, month }).then((r) => r.data.data),
    enabled: isManager || isProvost,
  });

  const { data: proofsData, isLoading: loadingProofs } = useQuery({
    queryKey: queryKeys.paymentProofs.list({ status: statusFilter || undefined }),
    queryFn: () => paymentProofsApi.list({ status: statusFilter || undefined, per_page: 50 }).then((r) => r.data),
    enabled: tab === "proofs",
  });

  const initMutation = useMutation({
    mutationFn: () => memberPaymentsApi.initMonth({ year, month, amount_due: 0 }),
    onSuccess: (r) => {
      toast.success(r.data.message);
      qc.invalidateQueries({ queryKey: ["member-payments"] });
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const markPaidMutation = useMutation({
    mutationFn: (id) => memberPaymentsApi.markPaid(id),
    onSuccess: () => { toast.success("Marked as paid"); qc.invalidateQueries({ queryKey: ["member-payments"] }); },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const markPendingMutation = useMutation({
    mutationFn: (id) => memberPaymentsApi.markPending(id),
    onSuccess: () => { toast.success("Marked as pending"); qc.invalidateQueries({ queryKey: ["member-payments"] }); },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const toggleActiveMutation = useMutation({
    mutationFn: (id) => memberPaymentsApi.toggleActive(id),
    onSuccess: (r) => {
      toast.success(r.data.message);
      qc.invalidateQueries({ queryKey: ["member-payments"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const approveProofMutation = useMutation({
    mutationFn: (id) => paymentProofsApi.approve(id),
    onSuccess: () => {
      toast.success("Proof approved & payment marked paid");
      qc.invalidateQueries({ queryKey: ["payment-proofs"] });
      qc.invalidateQueries({ queryKey: ["member-payments"] });
      setReviewProof(null);
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const rejectProofMutation = useMutation({
    mutationFn: ({ id, note }) => paymentProofsApi.reject(id, { rejection_note: note }),
    onSuccess: () => {
      toast.success("Proof rejected");
      qc.invalidateQueries({ queryKey: ["payment-proofs"] });
      setReviewProof(null);
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const submitProofMutation = useMutation({
    mutationFn: (data) => paymentProofsApi.submit(data),
    onSuccess: () => {
      toast.success("Proof submitted");
      qc.invalidateQueries({ queryKey: ["payment-proofs"] });
      qc.invalidateQueries({ queryKey: ["member-payments"] });
      setSubmitProofFor(null);
      setProofForm({ proof_type: "TRANSACTION_ID", proof_value: "" });
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const paymentColumns = [
    {
      key: "user", label: "Member",
      render: (p) => (
        <div>
          <p className="font-medium text-sm">{p.user?.full_name ?? "—"}</p>
          <p className="text-xs text-muted-foreground">{p.user?.student_id}</p>
        </div>
      ),
    },
    { key: "department", label: "Dept", render: (p) => <span className="text-sm">{p.user?.department ?? "—"}</span> },
    {
      key: "status", label: "Status",
      render: (p) => (
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
          p.status === "PAID"
            ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
            : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400"
        }`}>
          {p.status}
        </span>
      ),
    },
    {
      key: "user_status", label: "Active",
      render: (p) => (
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
          p.user?.status === "ACTIVE"
            ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
            : "bg-gray-100 text-gray-600 dark:bg-gray-900/30 dark:text-gray-400"
        }`}>
          {p.user?.status ?? "—"}
        </span>
      ),
    },
    {
      key: "actions", label: "",
      render: (p) => (
        <div className="flex gap-1 justify-end">
          {(isManager || isProvost) ? (
            <>
              {p.status === "PENDING" ? (
                <button onClick={() => markPaidMutation.mutate(p.id)} title="Mark Paid"
                  className="rounded-lg p-1.5 text-muted-foreground hover:bg-green-50 hover:text-green-600 transition-colors">
                  <CheckCircle className="h-4 w-4" />
                </button>
              ) : (
                <button onClick={() => markPendingMutation.mutate(p.id)} title="Mark Pending"
                  className="rounded-lg p-1.5 text-muted-foreground hover:bg-yellow-50 hover:text-yellow-600 transition-colors">
                  <Clock className="h-4 w-4" />
                </button>
              )}
              <button onClick={() => toggleActiveMutation.mutate(p.id)}
                title={p.user?.status === "ACTIVE" ? "Set Inactive" : "Set Active"}
                className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent transition-colors">
                {p.user?.status === "ACTIVE" ? <UserX className="h-4 w-4" /> : <UserCheck className="h-4 w-4" />}
              </button>
            </>
          ) : (
            p.status === "PENDING" && (
              <button onClick={() => setSubmitProofFor(p)} title="Submit Proof"
                className="rounded-lg px-3 py-1 text-xs font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-colors">
                Submit Proof
              </button>
            )
          )}
        </div>
      ),
    },
  ];

  const proofColumns = [
    {
      key: "user", label: "Member",
      render: (p) => <span className="font-medium text-sm">{p.user?.full_name ?? p.user_id}</span>,
    },
    { key: "proof_type", label: "Type", render: (p) => <span className="text-sm">{p.proof_type.replace("_", " ")}</span> },
    {
      key: "proof_value", label: "Proof",
      render: (p) => <span className="text-sm max-w-xs truncate block font-mono">{p.proof_value.substring(0, 40)}{p.proof_value.length > 40 ? "..." : ""}</span>,
    },
    {
      key: "status", label: "Status",
      render: (p) => (
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
          p.status === "APPROVED" ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
          : p.status === "REJECTED" ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
          : "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
        }`}>
          {p.status}
        </span>
      ),
    },
    { key: "created_at", label: "Submitted", render: (p) => <span className="text-sm text-muted-foreground">{formatDate(p.created_at)}</span> },
    {
      key: "actions", label: "",
      render: (p) => (
        <button onClick={() => setReviewProof(p)} title="Review"
          className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent transition-colors">
          <Eye className="h-4 w-4" />
        </button>
      ),
    },
  ];

  return (
    <PageContainer>
      <PageHeader
        title="Member Payments"
        description="Track payment status and review payment proofs"
        action={(isManager || isProvost) && (
          <button onClick={() => initMutation.mutate()} disabled={initMutation.isPending}
            className="flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50">
            <RefreshCw className={`h-4 w-4 ${initMutation.isPending ? "animate-spin" : ""}`} />
            Init {MONTHS[month - 1]} {year}
          </button>
        )}
      />

      {/* Summary cards */}
      {summaryData && (
        <div className="grid gap-4 sm:grid-cols-5">
          {[
            { label: "Paid", value: summaryData.paid, icon: <CheckCircle className="h-4 w-4" />, color: "text-green-600" },
            { label: "Pending", value: summaryData.pending, icon: <Clock className="h-4 w-4" />, color: "text-yellow-600" },
            { label: "Proofs Submitted", value: summaryData.proofs_submitted, icon: <FileCheck className="h-4 w-4" />, color: "text-blue-600" },
            { label: "Approved", value: summaryData.proofs_approved, icon: <CheckCircle className="h-4 w-4" />, color: "text-emerald-600" },
            { label: "Rejected", value: summaryData.proofs_rejected, icon: <AlertCircle className="h-4 w-4" />, color: "text-red-600" },
          ].map((s) => (
            <div key={s.label} className="rounded-xl border bg-card p-4">
              <div className="flex items-center gap-2 mb-1">
                <span className={s.color}>{s.icon}</span>
                <p className="text-xs text-muted-foreground">{s.label}</p>
              </div>
              <p className="text-2xl font-bold">{s.value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 border-b">
        {["payments", "proofs"].map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === t ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"
            }`}>
            {t === "payments" ? "Payment Status" : "Payment Proofs"}
          </button>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <select value={month} onChange={(e) => { setMonth(Number(e.target.value)); setPage(1); }}
          className="rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring">
          {MONTHS.map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
        </select>
        <select value={year} onChange={(e) => { setYear(Number(e.target.value)); setPage(1); }}
          className="rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring">
          {[2024, 2025, 2026, 2027].map((y) => <option key={y} value={y}>{y}</option>)}
        </select>
        <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
          className="rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring">
          <option value="">All Statuses</option>
          {tab === "payments"
            ? [<option key="PAID" value="PAID">Paid</option>, <option key="PENDING" value="PENDING">Pending</option>]
            : [<option key="SUBMITTED" value="SUBMITTED">Submitted</option>, <option key="APPROVED" value="APPROVED">Approved</option>, <option key="REJECTED" value="REJECTED">Rejected</option>]
          }
        </select>
      </div>

      {/* Table */}
      {tab === "payments" ? (
        isLoading ? <SkeletonTable rows={8} cols={5} /> :
        !paymentsData?.data?.length ? <EmptyState title="No payment records" description={`Click "Init ${MONTHS[month-1]}" to create payment records for active customers.`} /> :
        <>
          <DataTable columns={paymentColumns} data={paymentsData.data} />
          <Pagination meta={paymentsData.meta} page={page} perPage={perPage} setPage={setPage} setPerPage={setPerPage} />
        </>
      ) : (
        loadingProofs ? <SkeletonTable rows={8} cols={6} /> :
        !proofsData?.data?.length ? <EmptyState title="No payment proofs" description="Members haven't submitted any payment proofs yet." /> :
        <DataTable columns={proofColumns} data={proofsData.data} />
      )}

      {/* Proof review modal */}
      <ProofReviewModal
        proof={reviewProof}
        open={!!reviewProof}
        onClose={() => setReviewProof(null)}
        onApprove={() => approveProofMutation.mutate(reviewProof.id)}
        onReject={(note) => rejectProofMutation.mutate({ id: reviewProof.id, note })}
        isLoading={approveProofMutation.isPending || rejectProofMutation.isPending}
      />

      {/* Submit proof modal (customer) */}
      {submitProofFor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={() => setSubmitProofFor(null)}>
          <div className="w-full max-w-md rounded-xl bg-card border p-6 space-y-4 mx-4" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-semibold">Submit Payment Proof</h3>
            <p className="text-sm text-muted-foreground">
              For {MONTHS[submitProofFor.month - 1]} {submitProofFor.year}
            </p>
            <div>
              <label className="block text-sm font-medium mb-1.5">Proof Type</label>
              <select value={proofForm.proof_type}
                onChange={(e) => setProofForm((p) => ({ ...p, proof_type: e.target.value }))}
                className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring">
                <option value="TRANSACTION_ID">Transaction ID</option>
                <option value="TEXT_NOTE">Manual Note</option>
                <option value="IMAGE">Image URL</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">
                {proofForm.proof_type === "TRANSACTION_ID" ? "Transaction ID" :
                 proofForm.proof_type === "IMAGE" ? "Image URL" : "Note"}
              </label>
              {proofForm.proof_type === "TEXT_NOTE" ? (
                <textarea value={proofForm.proof_value}
                  onChange={(e) => setProofForm((p) => ({ ...p, proof_value: e.target.value }))}
                  rows={3} placeholder="Describe your payment..."
                  className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring resize-none" />
              ) : (
                <input value={proofForm.proof_value}
                  onChange={(e) => setProofForm((p) => ({ ...p, proof_value: e.target.value }))}
                  placeholder={proofForm.proof_type === "TRANSACTION_ID" ? "e.g. TXN123456789" : "https://..."}
                  className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring" />
              )}
            </div>
            <div className="flex gap-2 justify-end">
              <button onClick={() => setSubmitProofFor(null)}
                className="rounded-lg border border-input px-4 py-2 text-sm font-medium hover:bg-accent transition-colors">
                Cancel
              </button>
              <button
                disabled={!proofForm.proof_value.trim() || submitProofMutation.isPending}
                onClick={() => submitProofMutation.mutate({
                  member_payment_id: submitProofFor.id,
                  proof_type: proofForm.proof_type,
                  proof_value: proofForm.proof_value,
                })}
                className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50">
                {submitProofMutation.isPending ? "Submitting..." : "Submit Proof"}
              </button>
            </div>
          </div>
        </div>
      )}
    </PageContainer>
  );
}
