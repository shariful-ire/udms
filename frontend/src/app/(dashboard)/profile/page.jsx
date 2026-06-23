"use client";

import { useState, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Loader2, Eye, EyeOff, Camera } from "lucide-react";
import { toast } from "sonner";
import { profileApi } from "@/lib/axios";
import { queryKeys } from "@/lib/queryClient";
import { useAuthStore } from "@/store/authStore";
import { getErrorMessage } from "@/lib/utils";
import { PageContainer, PageLoader } from "@/components/shared/LoadingSpinner";
import { PageHeader } from "@/components/layout/PageHeader";
import { Avatar } from "@/components/shared/Avatar";
import { RoleBadge, StatusBadge } from "@/components/shared/Badge";

const DEPARTMENTS = ["IRE", "CySE", "DSE", "EdTE", "SE"];
const HALLS = ["UFTB Boys Hall", "UFTB Girls Hall-1", "UFTB Girls Hall-2"];

const profileSchema = z.object({
  full_name: z.string().min(2).max(150),
  phone: z.string().optional().or(z.literal("")),
  department: z.string().min(1),
  hall_name: z.string().min(1),
});

const passwordSchema = z.object({
  current_password: z.string().min(1, "Required"),
  new_password: z.string().min(8).regex(/[A-Z]/).regex(/[0-9]/).regex(/[^a-zA-Z0-9]/),
  confirm_password: z.string(),
}).refine((d) => d.new_password === d.confirm_password, { message: "Passwords do not match", path: ["confirm_password"] });

const inputCls = "w-full rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring transition-shadow";

export default function ProfilePage() {
  const { user, updateUser } = useAuthStore();
  const qc = useQueryClient();
  const avatarInputRef = useRef(null);
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);

  const { data: profile, isLoading } = useQuery({
    queryKey: queryKeys.profile,
    queryFn: () => profileApi.get().then((r) => r.data.data),
  });

  const profileForm = useForm({ resolver: zodResolver(profileSchema), values: profile ? { full_name: profile.full_name, phone: profile.phone ?? "", department: profile.department, hall_name: profile.hall_name } : {} });
  const passwordForm = useForm({ resolver: zodResolver(passwordSchema) });

  const updateMutation = useMutation({
    mutationFn: (data) => profileApi.update(data),
    onSuccess: (res) => {
      const updated = res.data.data;
      toast.success("Profile updated");
      updateUser(updated);
      qc.invalidateQueries({ queryKey: queryKeys.profile });
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const passwordMutation = useMutation({
    mutationFn: (data) => profileApi.changePassword(data),
    onSuccess: () => { toast.success("Password changed"); passwordForm.reset(); },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const avatarMutation = useMutation({
    mutationFn: (formData) => profileApi.uploadAvatar(formData),
    onSuccess: (res) => {
      const { profile_image } = res.data.data ?? {};
      if (profile_image) updateUser({ profile_image });
      qc.invalidateQueries({ queryKey: queryKeys.profile });
      toast.success("Avatar updated");
    },
    onError: (e) => toast.error(getErrorMessage(e)),
  });

  const handleAvatarChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("avatar", file);
    avatarMutation.mutate(formData);
  };

  if (isLoading) return <PageLoader />;

  const Field = ({ label, name, form, type = "text", children }) => {
    const { register, formState: { errors } } = form;
    return (
      <div className="space-y-1.5">
        <label className="text-sm font-medium">{label}</label>
        {children ?? <input type={type} {...register(name)} className={inputCls} />}
        {errors[name] && <p className="text-xs text-destructive">{errors[name].message}</p>}
      </div>
    );
  };

  return (
    <PageContainer>
      <PageHeader title="My Profile" description="Manage your account information" />

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Avatar + info */}
        <div className="rounded-xl border bg-card p-6 flex flex-col items-center gap-4 text-center">
          <div className="relative">
            <Avatar src={profile?.profile_image} name={profile?.full_name} size="2xl" />
            <button
              onClick={() => avatarInputRef.current?.click()}
              className="absolute bottom-0 right-0 rounded-full bg-primary p-2 text-white shadow-md hover:bg-primary/90 transition-colors"
              title="Change avatar">
              {avatarMutation.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Camera className="h-3.5 w-3.5" />}
            </button>
            <input ref={avatarInputRef} type="file" accept="image/*" className="hidden" onChange={handleAvatarChange} />
          </div>
          <div>
            <h2 className="font-semibold">{profile?.full_name}</h2>
            <p className="text-sm text-muted-foreground">@{profile?.username}</p>
          </div>
          <div className="flex gap-2 flex-wrap justify-center">
            <RoleBadge role={profile?.role} />
            <StatusBadge status={profile?.status} />
          </div>
          <div className="w-full space-y-2 text-sm text-left pt-3 border-t">
            {[
              { label: "Email", value: profile?.email },
              { label: "Student ID", value: profile?.student_id },
              { label: "Batch", value: profile?.batch },
            ].map(({ label, value }) => (
              <div key={label} className="flex justify-between">
                <span className="text-muted-foreground">{label}</span>
                <span className="font-medium">{value ?? "—"}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Edit forms */}
        <div className="lg:col-span-2 space-y-6">
          {/* Profile info */}
          <div className="rounded-xl border bg-card p-6 space-y-4">
            <h3 className="font-semibold">Personal Information</h3>
            <form onSubmit={profileForm.handleSubmit(updateMutation.mutate)} className="space-y-4" noValidate>
              <div className="grid grid-cols-2 gap-4">
                <Field label="Full Name" name="full_name" form={profileForm} />
                <Field label="Phone" name="phone" form={profileForm} type="tel" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <Field label="Department" name="department" form={profileForm}>
                  <select {...profileForm.register("department")} className={inputCls}>
                    <option value="">Select…</option>
                    {DEPARTMENTS.map((d) => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                </Field>
                <Field label="Hall Name" name="hall_name" form={profileForm}>
                  <select {...profileForm.register("hall_name")} className={inputCls}>
                    <option value="">Select…</option>
                    {HALLS.map((h) => (
                      <option key={h} value={h}>{h}</option>
                    ))}
                  </select>
                </Field>
              </div>
              <button type="submit" disabled={updateMutation.isPending}
                className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-60 transition-colors">
                {updateMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                {updateMutation.isPending ? "Saving…" : "Save changes"}
              </button>
            </form>
          </div>

          {/* Change password */}
          <div className="rounded-xl border bg-card p-6 space-y-4">
            <h3 className="font-semibold">Change Password</h3>
            <form onSubmit={passwordForm.handleSubmit(passwordMutation.mutate)} className="space-y-4" noValidate>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Current Password</label>
                <div className="relative">
                  <input type={showCurrent ? "text" : "password"} {...passwordForm.register("current_password")}
                    placeholder="Your current password"
                    className={`${inputCls} pr-10`} />
                  <button type="button" onClick={() => setShowCurrent((v) => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                    {showCurrent ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {passwordForm.formState.errors.current_password && <p className="text-xs text-destructive">{passwordForm.formState.errors.current_password.message}</p>}
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">New Password</label>
                <div className="relative">
                  <input type={showNew ? "text" : "password"} {...passwordForm.register("new_password")}
                    placeholder="Min 8 chars, uppercase, number, symbol"
                    className={`${inputCls} pr-10`} />
                  <button type="button" onClick={() => setShowNew((v) => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                    {showNew ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {passwordForm.formState.errors.new_password && <p className="text-xs text-destructive">{passwordForm.formState.errors.new_password.message}</p>}
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Confirm New Password</label>
                <input type="password" {...passwordForm.register("confirm_password")} placeholder="Repeat new password" className={inputCls} />
                {passwordForm.formState.errors.confirm_password && <p className="text-xs text-destructive">{passwordForm.formState.errors.confirm_password.message}</p>}
              </div>
              <button type="submit" disabled={passwordMutation.isPending}
                className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-60 transition-colors">
                {passwordMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                {passwordMutation.isPending ? "Changing…" : "Change password"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
