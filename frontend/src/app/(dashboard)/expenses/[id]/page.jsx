"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { expensesApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { formatDate, getErrorMessage } from "@/lib/utils";
import { PageContainer, PageLoader } from "@/components/shared/LoadingSpinner";
import { PageHeader } from "@/components/layout/PageHeader";
import { ExpenseForm } from "@/components/forms/MenuForm";
import { EXPENSE_CATEGORIES } from "@/lib/constants";

export default function ExpenseDetailPage({ params }) {
  const { id } = params;
  const router = useRouter();
  const qc = useQueryClient();

  const { data: expense, isLoading } = useQuery({
    queryKey: queryKeys.expenses.detail(id),
    queryFn: () => expensesApi.get(id).then((r) => r.data.data),
  });

  const mutation = useMutation({
    mutationFn: (data) => expensesApi.update(id, data),
    onSuccess: () => {
      toast.success("Expense updated");
      qc.invalidateQueries({ queryKey: queryKeys.expenses.detail(id) });
      qc.invalidateQueries({ queryKey: ["expenses"] });
      router.push("/expenses");
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  if (isLoading) return <PageLoader />;
  if (!expense) return null;

  return (
    <PageContainer>
      <PageHeader
        title="Edit Expense"
        description={`Editing expense from ${formatDate(expense.date ?? expense.expense_date)}`}
        action={
          <Link href="/expenses"
            className="flex items-center gap-1.5 rounded-lg border border-input px-3 py-2 text-sm font-medium hover:bg-accent transition-colors">
            <ArrowLeft className="h-4 w-4" /> Back
          </Link>
        }
      />
      <div className="max-w-xl">
        <div className="rounded-xl border bg-card p-6">
          <ExpenseForm
            defaultValues={{
              name: expense.name ?? "",
              expense_date: expense.date ?? expense.expense_date,
              category: expense.category,
              amount: expense.amount,
              description: expense.description ?? "",
            }}
            onSubmit={mutation.mutate}
            isLoading={mutation.isPending}
          />
        </div>
      </div>
    </PageContainer>
  );
}
