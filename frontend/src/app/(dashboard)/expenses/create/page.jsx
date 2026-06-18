"use client";

import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";
import { expensesApi } from "@/lib/axios";
import { getErrorMessage } from "@/lib/utils";
import { PageContainer } from "@/components/shared/LoadingSpinner";
import { PageHeader } from "@/components/layout/PageHeader";
import { ExpenseForm } from "@/components/forms/MenuForm";

export default function CreateExpensePage() {
  const router = useRouter();
  const qc = useQueryClient();

  const mutation = useMutation({
    mutationFn: (data) => expensesApi.create(data),
    onSuccess: () => {
      toast.success("Expense recorded");
      qc.invalidateQueries({ queryKey: ["expenses"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      qc.invalidateQueries({ queryKey: ["reports"] });
      router.push("/expenses");
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  return (
    <PageContainer>
      <PageHeader
        title="Add Expense"
        description="Record a new dining hall expense"
        action={
          <Link href="/expenses"
            className="flex items-center gap-1.5 rounded-lg border border-input px-3 py-2 text-sm font-medium hover:bg-accent transition-colors">
            <ArrowLeft className="h-4 w-4" /> Back
          </Link>
        }
      />
      <div className="max-w-xl">
        <div className="rounded-xl border bg-card p-6">
          <ExpenseForm onSubmit={mutation.mutate} isLoading={mutation.isPending} />
        </div>
      </div>
    </PageContainer>
  );
}
