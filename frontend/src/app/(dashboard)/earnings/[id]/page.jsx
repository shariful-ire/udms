"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";
import { earningsApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { getErrorMessage } from "@/lib/utils";
import { PageContainer, PageLoader } from "@/components/shared/LoadingSpinner";
import { PageHeader } from "@/components/layout/PageHeader";
import { EARNING_CATEGORIES } from "@/lib/constants";

export default function EditEarningPage() {
  const router = useRouter();
  const { id } = useParams();
  const qc = useQueryClient();

  const { data: earning, isLoading } = useQuery({
    queryKey: queryKeys.earnings.detail(id),
    queryFn: () => earningsApi.get(id).then((r) => r.data.data),
  });

  const [form, setForm] = useState(null);

  useEffect(() => {
    if (earning && !form) {
      setForm({
        description: earning.description,
        category: earning.category,
        amount: String(earning.amount),
        earning_date: earning.earning_date || earning.date,
        notes: earning.notes || "",
      });
    }
  }, [earning, form]);

  const mutation = useMutation({
    mutationFn: (data) => earningsApi.update(id, data),
    onSuccess: () => {
      toast.success("Earning updated");
      qc.invalidateQueries({ queryKey: ["earnings"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      router.push("/earnings");
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    mutation.mutate({
      ...form,
      amount: parseFloat(form.amount),
      notes: form.notes || null,
    });
  };

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  if (isLoading || !form) return <PageLoader />;

  return (
    <PageContainer>
      <PageHeader
        title="Edit Earning"
        description="Update earning record"
        action={
          <Link href="/earnings"
            className="flex items-center gap-1.5 rounded-lg border border-input px-3 py-2 text-sm font-medium hover:bg-accent transition-colors">
            <ArrowLeft className="h-4 w-4" /> Back
          </Link>
        }
      />
      <div className="max-w-xl">
        <div className="rounded-xl border bg-card p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Description</label>
              <input name="description" value={form.description} onChange={handleChange}
                className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"
                required minLength={2} maxLength={200} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1.5">Category</label>
                <select name="category" value={form.category} onChange={handleChange}
                  className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring">
                  {EARNING_CATEGORIES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5">Amount</label>
                <input name="amount" type="number" step="0.01" min="0.01" value={form.amount} onChange={handleChange}
                  className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"
                  required />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Date</label>
              <input name="earning_date" type="date" value={form.earning_date} onChange={handleChange}
                className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"
                required />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Notes (optional)</label>
              <textarea name="notes" value={form.notes} onChange={handleChange} rows={3}
                className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring resize-none" />
            </div>
            <button type="submit" disabled={mutation.isPending}
              className="w-full rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50">
              {mutation.isPending ? "Saving..." : "Save Changes"}
            </button>
          </form>
        </div>
      </div>
    </PageContainer>
  );
}
