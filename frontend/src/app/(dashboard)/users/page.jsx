"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, UserX, UserCheck, Shield, MoreHorizontal } from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";
import { usersApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { useDebounce } from "@/lib/hooks/useDebounce";
import { usePagination } from "@/lib/hooks/usePagination";
import { PageContainer, SkeletonTable, EmptyState } from "@/components/shared/LoadingSpinner";
import { SearchInput } from "@/components/shared/SearchInput";
import { DataTable } from "@/components/tables/DataTable";
import { Pagination } from "@/components/tables/Pagination";
import { RoleBadge, StatusBadge } from "@/components/shared/Badge";
import { Avatar } from "@/components/shared/Avatar";
import { PageHeader } from "@/components/layout/PageHeader";
import { ConfirmModal } from "@/components/modals/ConfirmModal";
import { formatDate, getErrorMessage } from "@/lib/utils";
import { ROLES } from "@/lib/constants";

const ROLE_FILTER_OPTIONS = [
  { value: "", label: "All Roles" },
  { value: ROLES.NON_CUSTOMER, label: "Students" },
  { value: ROLES.CUSTOMER, label: "Customers" },
  { value: ROLES.DINING_MANAGER, label: "Dining Manager" },
];

const STATUS_FILTER_OPTIONS = [
  { value: "", label: "All Statuses" },
  { value: "ACTIVE", label: "Active" },
  { value: "INACTIVE", label: "Inactive" },
  { value: "SUSPENDED", label: "Suspended" },
];

export default function UsersPage() {
  const qc = useQueryClient();
  const { page, perPage, params, setPage, setPerPage } = usePagination();
  const [search, setSearch] = useState("");
  const [role, setRole] = useState("");
  const [status, setStatus] = useState("");
  const debouncedSearch = useDebounce(search, 400);
  const [confirmModal, setConfirmModal] = useState(null);

  const queryParams = { ...params, search: debouncedSearch, role, status };

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.users.list(queryParams),
    queryFn: () => usersApi.list(queryParams).then((r) => r.data),
  });

  const suspendMutation = useMutation({
    mutationFn: (id) => usersApi.suspend(id),
    onSuccess: () => { toast.success("User suspended"); qc.invalidateQueries({ queryKey: queryKeys.users.all }); },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const activateMutation = useMutation({
    mutationFn: (id) => usersApi.activate(id),
    onSuccess: () => { toast.success("User activated"); qc.invalidateQueries({ queryKey: queryKeys.users.all }); },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const assignManagerMutation = useMutation({
    mutationFn: (id) => usersApi.assignManager(id),
    onSuccess: () => { toast.success("Dining manager assigned"); qc.invalidateQueries({ queryKey: queryKeys.users.all }); },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const columns = [
    {
      key: "user",
      label: "User",
      render: (u) => (
        <div className="flex items-center gap-3">
          <Avatar src={u.profile_image} name={u.full_name} size="sm" />
          <div>
            <Link href={`/users/${u.id}`} className="font-medium hover:text-primary transition-colors text-sm">
              {u.full_name}
            </Link>
            <p className="text-xs text-muted-foreground">{u.email}</p>
          </div>
        </div>
      ),
    },
    { key: "student_id", label: "Student ID", render: (u) => <span className="font-mono text-sm">{u.student_id}</span> },
    { key: "role", label: "Role", render: (u) => <RoleBadge role={u.role} /> },
    { key: "status", label: "Status", render: (u) => <StatusBadge status={u.status} /> },
    { key: "created_at", label: "Joined", render: (u) => <span className="text-sm text-muted-foreground">{formatDate(u.created_at)}</span> },
    {
      key: "actions",
      label: "",
      render: (u) => (
        <div className="flex items-center gap-1 justify-end">
          <Link href={`/users/${u.id}`}
            className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
            title="View details">
            <MoreHorizontal className="h-4 w-4" />
          </Link>
          {u.status === "ACTIVE" ? (
            <button
              onClick={() => setConfirmModal({ type: "suspend", user: u })}
              className="rounded-lg p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
              title="Suspend">
              <UserX className="h-4 w-4" />
            </button>
          ) : (
            <button
              onClick={() => setConfirmModal({ type: "activate", user: u })}
              className="rounded-lg p-1.5 text-muted-foreground hover:bg-green-50 hover:text-green-600 transition-colors"
              title="Activate">
              <UserCheck className="h-4 w-4" />
            </button>
          )}
          {u.role === ROLES.NON_CUSTOMER && (
            <button
              onClick={() => setConfirmModal({ type: "assign_manager", user: u })}
              className="rounded-lg p-1.5 text-muted-foreground hover:bg-blue-50 hover:text-blue-600 transition-colors"
              title="Assign as Dining Manager">
              <Shield className="h-4 w-4" />
            </button>
          )}
        </div>
      ),
    },
  ];

  const handleConfirm = () => {
    if (!confirmModal) return;
    const { type, user: u } = confirmModal;
    if (type === "suspend") suspendMutation.mutate(u.id);
    else if (type === "activate") activateMutation.mutate(u.id);
    else if (type === "assign_manager") assignManagerMutation.mutate(u.id);
    setConfirmModal(null);
  };

  const isActionLoading = suspendMutation.isPending || activateMutation.isPending || assignManagerMutation.isPending;

  return (
    <PageContainer>
      <PageHeader
        title="Users"
        description="Manage all registered users"
        action={
          <Link href="/users/create"
            className="flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors">
            <Plus className="h-4 w-4" /> New User
          </Link>
        }
      />

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <SearchInput value={search} onSearch={setSearch} placeholder="Search name, email, student ID…" className="w-64" />
        <select value={role} onChange={(e) => { setRole(e.target.value); setPage(1); }}
          className="rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring">
          {ROLE_FILTER_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        <select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1); }}
          className="rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring">
          {STATUS_FILTER_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
      </div>

      {/* Table */}
      {isLoading ? (
        <SkeletonTable rows={8} cols={6} />
      ) : !data?.data?.length ? (
        <EmptyState title="No users found" description="Try adjusting your filters." />
      ) : (
        <>
          <DataTable columns={columns} data={data.data} />
          <Pagination meta={data.meta} page={page} perPage={perPage} setPage={setPage} setPerPage={setPerPage} />
        </>
      )}

      {/* Confirm modal */}
      <ConfirmModal
        open={!!confirmModal}
        onClose={() => setConfirmModal(null)}
        onConfirm={handleConfirm}
        isLoading={isActionLoading}
        title={confirmModal?.type === "suspend" ? "Suspend user?" : confirmModal?.type === "activate" ? "Activate user?" : "Assign as Dining Manager?"}
        description={
          confirmModal?.type === "suspend"
            ? `${confirmModal?.user?.full_name} will lose access to the system.`
            : confirmModal?.type === "activate"
            ? `${confirmModal?.user?.full_name}'s account will be re-activated.`
            : `${confirmModal?.user?.full_name} will become the Dining Manager. Any existing manager will be demoted.`
        }
        confirmLabel={confirmModal?.type === "suspend" ? "Suspend" : confirmModal?.type === "activate" ? "Activate" : "Assign"}
        variant={confirmModal?.type === "suspend" ? "danger" : "default"}
      />
    </PageContainer>
  );
}
