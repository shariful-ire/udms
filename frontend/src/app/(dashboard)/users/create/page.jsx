"use client";

import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";
import { usersApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { getErrorMessage } from "@/lib/utils";
import { PageContainer } from "@/components/shared/LoadingSpinner";
import { PageHeader } from "@/components/layout/PageHeader";
import { UserForm } from "@/components/forms/UserForm";

export default function CreateUserPage() {
  const router = useRouter();
  const qc = useQueryClient();

  const mutation = useMutation({
    mutationFn: (data) => usersApi.create(data),
    onSuccess: () => {
      toast.success("User created successfully");
      qc.invalidateQueries({ queryKey: queryKeys.users.all });
      router.push("/users");
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  return (
    <PageContainer>
      <PageHeader
        title="Create User"
        description="Add a new user to the system"
        action={
          <Link href="/users"
            className="flex items-center gap-1.5 rounded-lg border border-input px-3 py-2 text-sm font-medium hover:bg-accent transition-colors">
            <ArrowLeft className="h-4 w-4" /> Back
          </Link>
        }
      />
      <div className="max-w-2xl">
        <div className="rounded-xl border bg-card p-6">
          <UserForm onSubmit={mutation.mutate} isLoading={mutation.isPending} />
        </div>
      </div>
    </PageContainer>
  );
}
