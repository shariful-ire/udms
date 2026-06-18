"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Menu, Sun, Moon, Monitor, LogOut, User, Settings, ChevronDown } from "lucide-react";
import { useTheme } from "next-themes";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/authStore";
import { useUIStore } from "@/store/uiStore";
import { authApi } from "@/lib/axios";
import Avatar from "@/components/shared/Avatar";
import RoleBadge from "@/components/shared/RoleBadge";

function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const options = [
    { value: "light", icon: Sun, label: "Light" },
    { value: "dark", icon: Moon, label: "Dark" },
    { value: "system", icon: Monitor, label: "System" },
  ];
  const current = options.find((o) => o.value === theme) ?? options[2];
  const Icon = current.icon;

  return (
    <div className="relative group">
      <button
        className="flex h-9 w-9 items-center justify-center rounded-lg border border-input
          hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
        aria-label="Toggle theme"
      >
        <Icon className="h-4 w-4" />
      </button>
      <div className="absolute right-0 top-10 z-50 hidden group-hover:block min-w-[120px] rounded-xl border bg-popover shadow-lg p-1">
        {options.map(({ value, icon: OptionIcon, label }) => (
          <button
            key={value}
            onClick={() => setTheme(value)}
            className={cn(
              "flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-accent transition-colors",
              theme === value && "text-primary font-medium"
            )}
          >
            <OptionIcon className="h-3.5 w-3.5" />
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}

function UserMenu({ user }) {
  const router = useRouter();
  const { logout } = useAuthStore();
  const [open, setOpen] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

  const handleLogout = async () => {
    setLoggingOut(true);
    try {
      await authApi.logout();
    } catch {
      // Ignore errors — logout anyway
    } finally {
      document.cookie = "udms_session=; path=/; max-age=0";
      logout();
      router.replace("/login");
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 rounded-lg border border-input px-2.5 py-1.5
          hover:bg-muted transition-colors"
        aria-expanded={open}
        aria-haspopup="true"
      >
        <Avatar src={user?.profile_image} name={user?.full_name} size="sm" />
        <div className="hidden sm:block text-left min-w-0">
          <p className="text-sm font-medium truncate max-w-[120px]">{user?.full_name}</p>
        </div>
        <ChevronDown className={cn("h-4 w-4 text-muted-foreground transition-transform", open && "rotate-180")} />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-30" onClick={() => setOpen(false)} />
          <div className="absolute right-0 top-11 z-40 min-w-[200px] rounded-xl border bg-popover shadow-lg p-1">
            {/* User info */}
            <div className="px-3 py-2 border-b mb-1">
              <p className="text-sm font-medium truncate">{user?.full_name}</p>
              <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
              <RoleBadge role={user?.role} className="mt-1" />
            </div>

            <button
              onClick={() => { router.push("/profile"); setOpen(false); }}
              className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-accent transition-colors"
            >
              <User className="h-4 w-4" />
              Profile
            </button>
            <button
              onClick={() => { router.push("/settings"); setOpen(false); }}
              className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-accent transition-colors"
            >
              <Settings className="h-4 w-4" />
              Settings
            </button>
            <div className="border-t mt-1 pt-1">
              <button
                onClick={handleLogout}
                disabled={loggingOut}
                className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm text-destructive hover:bg-destructive/10 transition-colors disabled:opacity-60"
              >
                <LogOut className="h-4 w-4" />
                {loggingOut ? "Signing out…" : "Sign out"}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export function Topbar() {
  const user = useAuthStore((s) => s.user);
  const { toggleMobileSidebar } = useUIStore();

  return (
    <header className="sticky top-0 z-20 flex h-[var(--topbar-height)] items-center gap-3 border-b bg-background/95 backdrop-blur px-4 sm:px-6">
      {/* Mobile menu toggle */}
      <button
        onClick={toggleMobileSidebar}
        className="lg:hidden flex h-9 w-9 items-center justify-center rounded-lg border border-input
          hover:bg-muted transition-colors text-muted-foreground"
        aria-label="Open navigation"
      >
        <Menu className="h-4 w-4" />
      </button>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Right controls */}
      <div className="flex items-center gap-2">
        <ThemeToggle />
        <UserMenu user={user} />
      </div>
    </header>
  );
}

export default Topbar;
