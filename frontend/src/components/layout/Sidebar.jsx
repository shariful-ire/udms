"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Users, UtensilsCrossed, CreditCard, BarChart3,
  Shield, Settings, UserCheck, ClipboardList, CalendarDays, PieChart,
  ChevronLeft, ChevronRight, X,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/authStore";
import { useUIStore } from "@/store/uiStore";
import { NAV_LINKS } from "@/lib/constants";
import Avatar from "@/components/shared/Avatar";
import RoleBadge from "@/components/shared/RoleBadge";

const ICON_MAP = {
  LayoutDashboard, Users, UtensilsCrossed, CreditCard, BarChart3,
  Shield, Settings, UserCheck, ClipboardList, CalendarDays, PieChart,
};

function NavItem({ href, label, icon: iconName, collapsed, onClick }) {
  const pathname = usePathname();
  const Icon = ICON_MAP[iconName] ?? LayoutDashboard;
  const isActive = pathname === href || (href !== "/dashboard" && pathname.startsWith(href));

  return (
    <Link
      href={href}
      onClick={onClick}
      className={cn(
        "nav-item",
        isActive && "active",
        collapsed && "justify-center px-2"
      )}
      title={collapsed ? label : undefined}
    >
      <Icon className="h-4 w-4 shrink-0" />
      {!collapsed && <span className="truncate">{label}</span>}
    </Link>
  );
}

export function Sidebar() {
  const user = useAuthStore((s) => s.user);
  const { sidebarCollapsed, toggleSidebar, mobileSidebarOpen, setMobileSidebarOpen } =
    useUIStore();

  const role = user?.role;
  const navLinks = NAV_LINKS[role] ?? [];

  const sidebarContent = (isMobile = false) => (
    <aside
      className={cn(
        "flex flex-col h-full bg-[hsl(var(--sidebar-bg))] border-r border-[hsl(var(--sidebar-border))]",
        "transition-all duration-300 ease-in-out",
        !isMobile && (sidebarCollapsed
          ? "w-[var(--sidebar-collapsed)]"
          : "w-[var(--sidebar-width)]"),
        isMobile && "w-64"
      )}
    >
      {/* Logo / Header */}
      <div
        className={cn(
          "flex h-[var(--topbar-height)] items-center border-b border-[hsl(var(--sidebar-border))]",
          sidebarCollapsed && !isMobile ? "justify-center px-4" : "px-4 gap-3"
        )}
      >
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary">
          <span className="text-sm font-bold text-primary-foreground">U</span>
        </div>
        {(!sidebarCollapsed || isMobile) && (
          <div className="min-w-0">
            <p className="text-sm font-semibold truncate">UDMS</p>
            <p className="text-[10px] text-muted-foreground truncate">Dining System</p>
          </div>
        )}
        {isMobile && (
          <button
            onClick={() => setMobileSidebarOpen(false)}
            className="ml-auto text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-2 space-y-0.5">
        {navLinks.map((link) => (
          <NavItem
            key={link.href}
            {...link}
            collapsed={sidebarCollapsed && !isMobile}
            onClick={isMobile ? () => setMobileSidebarOpen(false) : undefined}
          />
        ))}
      </nav>

      {/* User info at bottom */}
      {user && (
        <div className={cn(
          "border-t border-[hsl(var(--sidebar-border))] p-3",
          sidebarCollapsed && !isMobile ? "flex justify-center" : "flex items-center gap-3"
        )}>
          <Avatar
            src={user.profile_image}
            name={user.full_name}
            size="sm"
            className="shrink-0"
          />
          {(!sidebarCollapsed || isMobile) && (
            <div className="min-w-0 flex-1">
              <p className="text-xs font-medium truncate">{user.full_name}</p>
              <RoleBadge role={user.role} className="mt-0.5" />
            </div>
          )}
        </div>
      )}

      {/* Collapse toggle — desktop only */}
      {!isMobile && (
        <button
          onClick={toggleSidebar}
          className="flex items-center justify-center h-8 border-t border-[hsl(var(--sidebar-border))]
            text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors"
          aria-label={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {sidebarCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </button>
      )}
    </aside>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <div className="hidden lg:flex h-screen sticky top-0">
        {sidebarContent(false)}
      </div>

      {/* Mobile drawer */}
      {mobileSidebarOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={() => setMobileSidebarOpen(false)}
          />
          {/* Drawer */}
          <div className="absolute left-0 top-0 h-full">
            {sidebarContent(true)}
          </div>
        </div>
      )}
    </>
  );
}

export default Sidebar;
