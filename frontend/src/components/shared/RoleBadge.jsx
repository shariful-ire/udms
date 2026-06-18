import { cn } from "@/lib/utils";
import { ROLE_LABELS, ROLE_COLORS } from "@/lib/constants";

export function RoleBadge({ role, className }) {
  if (!role) return null;
  const label = ROLE_LABELS[role] ?? role;
  const color = ROLE_COLORS[role] ?? "bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400";
  return (
    <span className={cn("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium", color, className)}>
      {label}
    </span>
  );
}

export default RoleBadge;
