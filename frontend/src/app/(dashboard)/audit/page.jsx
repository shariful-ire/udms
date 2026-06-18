"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { auditApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { usePagination } from "@/lib/hooks/usePagination";
import { useDebounce } from "@/lib/hooks/useDebounce";
import { formatDatetime } from "@/lib/utils";
import { AUDIT_ACTIONS } from "@/lib/constants";
import { PageContainer, SkeletonTable, EmptyState } from "@/components/shared/LoadingSpinner";
import { PageHeader } from "@/components/layout/PageHeader";
import { SearchInput } from "@/components/shared/SearchInput";
import { DataTable } from "@/components/tables/DataTable";
import { Pagination } from "@/components/tables/Pagination";
import { Avatar } from "@/components/shared/Avatar";
import { Shield } from "lucide-react";

export default function AuditPage() {
  const { page, perPage, params, setPage, setPerPage } = usePagination({ initialPerPage: 20 });
  const [search, setSearch] = useState("");
  const [action, setAction] = useState("");
  const debouncedSearch = useDebounce(search, 400);

  const qParams = { ...params, search: debouncedSearch, action };

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.audit.list(qParams),
    queryFn: () => auditApi.list(qParams).then((r) => r.data),
  });

  const columns = [
    {
      key: "actor", label: "Performed By",
      render: (log) => (
        <div className="flex items-center gap-2">
          <Avatar src={log.actor?.avatar_url} name={log.actor?.full_name ?? "System"} size="xs" />
          <span className="text-sm font-medium">{log.actor?.full_name ?? "System"}</span>
        </div>
      )
    },
    { key: "action", label: "Action", render: (log) => <span className="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">{log.action}</span> },
    { key: "target", label: "Target", render: (log) => <span className="text-sm text-muted-foreground">{log.target_description ?? "—"}</span> },
    { key: "ip", label: "IP Address", render: (log) => <span className="font-mono text-xs text-muted-foreground">{log.ip_address ?? "—"}</span> },
    { key: "at", label: "When", render: (log) => <span className="text-sm text-muted-foreground">{formatDatetime(log.created_at)}</span> },
  ];

  return (
    <PageContainer>
      <PageHeader title="Audit Logs" description="Complete history of system actions" />

      <div className="flex flex-wrap gap-3">
        <SearchInput value={search} onSearch={setSearch} placeholder="Search by user, action…" className="w-64" />
        <select value={action} onChange={(e) => { setAction(e.target.value); setPage(1); }}
          className="rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring max-w-xs">
          <option value="">All Actions</option>
          {AUDIT_ACTIONS.map((a) => <option key={a} value={a}>{a.replace(/_/g, " ")}</option>)}
        </select>
      </div>

      {isLoading ? <SkeletonTable rows={10} cols={5} /> : !data?.data?.length ? (
        <EmptyState icon={Shield} title="No audit logs" description="System actions will appear here." />
      ) : (
        <>
          <DataTable columns={columns} data={data.data} />
          <Pagination meta={data.meta} page={page} perPage={perPage} setPage={setPage} setPerPage={setPerPage} />
        </>
      )}
    </PageContainer>
  );
}
