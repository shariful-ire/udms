"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Trash2, Ban } from "lucide-react";
import { toast } from "sonner";
import { diningApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { formatDate, getErrorMessage } from "@/lib/utils";
import { MEAL_TYPE_LABELS, MEAL_TYPE_ICONS } from "@/lib/constants";
import { PageContainer, SkeletonTable, EmptyState } from "@/components/shared/LoadingSpinner";
import { PageHeader } from "@/components/layout/PageHeader";
import { DateRangePicker } from "@/components/shared/SearchInput";
import { DataTable } from "@/components/tables/DataTable";
import { Pagination } from "@/components/tables/Pagination";
import { ConfirmModal } from "@/components/modals/ConfirmModal";
import { Modal } from "@/components/modals/UserModal";
import { MenuForm } from "@/components/forms/MenuForm";
import { usePagination } from "@/lib/hooks/usePagination";

export default function DiningMenuPage() {
  const qc = useQueryClient();
  const { page, perPage, params, setPage, setPerPage } = usePagination();
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [modal, setModal] = useState(null); // null | { type: 'create'|'edit'|'delete'|'cancel', menu?: {} }

  const qParams = { ...params, start_date: startDate, end_date: endDate };

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.dining.menus(qParams),
    queryFn: () => diningApi.getMenus(qParams).then((r) => r.data),
  });

  const createMutation = useMutation({
    mutationFn: (d) => diningApi.createMenu(d),
    onSuccess: () => { toast.success("Menu created"); qc.invalidateQueries({ queryKey: ["dining","menus"] }); setModal(null); },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => diningApi.updateMenu(id, data),
    onSuccess: () => { toast.success("Menu updated"); qc.invalidateQueries({ queryKey: ["dining","menus"] }); setModal(null); },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const cancelMutation = useMutation({
    mutationFn: (id) => diningApi.cancelMenu(id),
    onSuccess: () => { toast.success("Menu cancelled"); qc.invalidateQueries({ queryKey: ["dining","menus"] }); setModal(null); },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => diningApi.deleteMenu(id),
    onSuccess: () => { toast.success("Menu deleted"); qc.invalidateQueries({ queryKey: ["dining","menus"] }); setModal(null); },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const columns = [
    { key: "date", label: "Date", render: (m) => <span className="font-medium">{formatDate(m.date)}</span> },
    { key: "type", label: "Meal", render: (m) => <span className="flex items-center gap-1.5">{MEAL_TYPE_ICONS[m.meal_type]} {MEAL_TYPE_LABELS[m.meal_type]}</span> },
    { key: "items", label: "Items", render: (m) => <span className="text-sm text-muted-foreground">{m.items?.join(", ") ?? "—"}</span> },
    { key: "status", label: "Status", render: (m) => (
      <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${m.is_cancelled ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"}`}>
        {m.is_cancelled ? "Cancelled" : "Active"}
      </span>
    )},
    { key: "actions", label: "", render: (m) => (
      <div className="flex gap-1 justify-end">
        <button onClick={() => setModal({ type: "edit", menu: m })} className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent transition-colors"><Pencil className="h-4 w-4" /></button>
        {!m.is_cancelled && <button onClick={() => setModal({ type: "cancel", menu: m })} className="rounded-lg p-1.5 text-muted-foreground hover:text-amber-600 hover:bg-amber-50 transition-colors"><Ban className="h-4 w-4" /></button>}
        <button onClick={() => setModal({ type: "delete", menu: m })} className="rounded-lg p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"><Trash2 className="h-4 w-4" /></button>
      </div>
    )},
  ];

  return (
    <PageContainer>
      <PageHeader
        title="Daily Menus"
        description="Manage what's served each day"
        action={
          <button onClick={() => setModal({ type: "create" })}
            className="flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors">
            <Plus className="h-4 w-4" /> Add Menu
          </button>
        }
      />

      <DateRangePicker startDate={startDate} endDate={endDate} onStartChange={(v) => { setStartDate(v); setPage(1); }} onEndChange={(v) => { setEndDate(v); setPage(1); }} />

      {isLoading ? <SkeletonTable rows={8} cols={5} /> : !data?.data?.length ? (
        <EmptyState title="No menus found" description="Create a daily menu to get started." />
      ) : (
        <>
          <DataTable columns={columns} data={data.data} />
          <Pagination meta={data.meta} page={page} perPage={perPage} setPage={setPage} setPerPage={setPerPage} />
        </>
      )}

      <Modal open={modal?.type === "create" || modal?.type === "edit"} onClose={() => setModal(null)}
        title={modal?.type === "create" ? "Create Menu" : "Edit Menu"}>
        <MenuForm
          defaultValues={modal?.menu ? { date: modal.menu.date, meal_type: modal.menu.meal_type, items: modal.menu.items?.map((name) => ({ name })) ?? [{ name: "" }], note: modal.menu.note ?? "" } : undefined}
          onSubmit={(d) => modal?.type === "create" ? createMutation.mutate(d) : updateMutation.mutate({ id: modal.menu.id, data: d })}
          isLoading={createMutation.isPending || updateMutation.isPending}
        />
      </Modal>

      <ConfirmModal open={modal?.type === "cancel"} onClose={() => setModal(null)} onConfirm={() => cancelMutation.mutate(modal.menu.id)} isLoading={cancelMutation.isPending} title="Cancel this menu?" description="Students will no longer be able to add this meal." confirmLabel="Cancel Menu" variant="danger" />
      <ConfirmModal open={modal?.type === "delete"} onClose={() => setModal(null)} onConfirm={() => deleteMutation.mutate(modal.menu.id)} isLoading={deleteMutation.isPending} title="Delete this menu?" description="This cannot be undone." confirmLabel="Delete" variant="danger" />
    </PageContainer>
  );
}
