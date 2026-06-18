"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, UserX, UserCheck, Trash2 } from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { usersApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { formatDate, formatDatetime, getErrorMessage } from "@/lib/utils";
import { PageContainer, PageLoader } from "@/components/shared/LoadingSpinner";
import { PageHeader } from "@/components/layout/PageHeader";
import { UserForm } from "@/components/forms/UserForm";
import { Avatar } from "@/components/shared/Avatar";
import { RoleBadge, StatusBadge } from "@/components/shared/Badge";
import { ConfirmModal } from "@/components/modals/ConfirmModal";
import { useState } from "react";

export default function UserDetailPage({ params }) {
  const { id } = params;
  const router = useRouter();
  const qc = useQueryClient();
  const [confirmModal, setConfirmModal] = useState(null);

  const { data: user, isLoading } = useQuery({
    queryKey: queryKeys.users.detail(id),
    queryFn: () => usersApi.get(id).then((r) => r.data.data),
  });

  const updateMutation = useMutation({
    mutationFn: (data) => usersApi.update(id, data),
    onSuccess: () => {
      toast.success("User updated");
      qc.invalidateQueries({ queryKey: queryKeys.users.detail(id) });
      qc.invalidateQueries({ queryKey: queryKeys.users.all });
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const suspendMutation = useMutation({
    mutationFn: () => usersApi.suspend(id),
    onSuccess: () => {
      toast.success("User suspended");
      qc.invalidateQueries({ queryKey: queryKeys.users.detail(id) });
      setConfirmModal(null);
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const activateMutation = useMutation({
    mutationFn: () => usersApi.activate(id),
    onSuccess: () => {
      toast.success("User activated");
      qc.invalidateQueries({ queryKey: queryKeys.users.detail(id) });
      setConfirmModal(null);
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const deleteMutation = useMutation({
    mutationFn: () => usersApi.delete(id),
    onSuccess: () => {
      toast.success("User deleted");
      qc.invalidateQueries({ queryKey: queryKeys.users.all });
      router.push("/users");
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  if (isLoading) return <PageLoader />;
  if (!user) return null;

  const isActionLoading = suspendMutation.isPending || activateMutation.isPending || deleteMutation.isPending;

  return (
    <PageContainer>
      <PageHeader
        title="User Details"
        description={`Managing account for ${user.full_name}`}
        action={
          <Link href="/users"
            className="flex items-center gap-1.5 rounded-lg border border-input px-3 py-2 text-sm font-medium hover:bg-accent transition-colors">
            <ArrowLeft className="h-4 w-4" /> Back
          </Link>
        }
      />

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Profile card */}
        <div className="rounded-xl border bg-card p-6 space-y-4">
          <div className="flex flex-col items-center gap-3 text-center">
            <Avatar src={user.profile_image} name={user.full_name} size="xl" />
            <div>
              <h2 className="font-semibold">{user.full_name}</h2>
              <p className="text-sm text-muted-foreground">@{user.username}</p>
            </div>
            <div className="flex gap-2">
              <RoleBadge role={user.role} />
              <StatusBadge status={user.status} />
            </div>
          </div>

          <div className="space-y-3 text-sm pt-2 border-t">
            {[
              { label: "Email", value: user.email },
              { label: "Student ID", value: user.student_id },
              { label: "Department", value: user.department },
              { label: "Batch", value: user.batch },
              { label: "Hall", value: user.hall_name },
              { label: "Phone", value: user.phone ?? "—" },
              { label: "Joined", value: formatDate(user.created_at) },
              { label: "Last login", value: user.last_login_at ? formatDatetime(user.last_login_at) : "—" },
            ].map(({ label, value }) => (
              <div key={label} className="flex justify-between gap-2">
                <span className="text-muted-foreground shrink-0">{label}</span>
                <span className="font-medium text-right">{value}</span>
              </div>
            ))}
          </div>

          {/* Action buttons */}
          <div className="space-y-2 pt-2 border-t">
            {user.status === "ACTIVE" ? (
              <button onClick={() => setConfirmModal("suspend")}
                className="w-full flex items-center justify-center gap-1.5 rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm font-medium text-destructive hover:bg-destructive/20 transition-colors">
                <UserX className="h-4 w-4" /> Suspend account
              </button>
            ) : (
              <button onClick={() => setConfirmModal("activate")}
                className="w-full flex items-center justify-center gap-1.5 rounded-lg border border-green-200 bg-green-50 px-3 py-2 text-sm font-medium text-green-700 hover:bg-green-100 transition-colors dark:border-green-800 dark:bg-green-900/20 dark:text-green-400 dark:hover:bg-green-900/30">
                <UserCheck className="h-4 w-4" /> Activate account
              </button>
            )}
            <button onClick={() => setConfirmModal("delete")}
              className="w-full flex items-center justify-center gap-1.5 rounded-lg border border-input px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-destructive/10 hover:text-destructive hover:border-destructive/30 transition-colors">
              <Trash2 className="h-4 w-4" /> Delete user
            </button>
          </div>
        </div>

        {/* Edit form */}
        <div className="lg:col-span-2 rounded-xl border bg-card p-6">
          <h3 className="font-semibold mb-4">Edit Information</h3>
          <UserForm
            defaultValues={{
              full_name: user.full_name, username: user.username, email: user.email,
              student_id: user.student_id, department: user.department, batch: user.batch,
              hall_name: user.hall_name, phone: user.phone ?? "", role: user.role,
            }}
            onSubmit={updateMutation.mutate}
            isLoading={updateMutation.isPending}
            isEdit
          />
        </div>
      </div>

      {/* Confirm modals */}
      <ConfirmModal
        open={confirmModal === "suspend"}
        onClose={() => setConfirmModal(null)}
        onConfirm={() => suspendMutation.mutate()}
        isLoading={isActionLoading}
        title="Suspend this user?"
        description={`${user.full_name} will lose access to the system immediately.`}
        confirmLabel="Suspend"
        variant="danger"
      />
      <ConfirmModal
        open={confirmModal === "activate"}
        onClose={() => setConfirmModal(null)}
        onConfirm={() => activateMutation.mutate()}
        isLoading={isActionLoading}
        title="Activate this user?"
        description={`${user.full_name}'s account will be re-enabled.`}
        confirmLabel="Activate"
      />
      <ConfirmModal
        open={confirmModal === "delete"}
        onClose={() => setConfirmModal(null)}
        onConfirm={() => deleteMutation.mutate()}
        isLoading={isActionLoading}
        title="Delete this user?"
        description="This action cannot be undone. All user data will be permanently removed."
        confirmLabel="Delete permanently"
        variant="danger"
      />
    </PageContainer>
  );
}
