import { cn } from "@/lib/utils";
import {
  USER_STATUS_LABELS, USER_STATUS_COLORS,
  REQUEST_STATUS_LABELS, REQUEST_STATUS_COLORS,
} from "@/lib/constants";

/**
 * StatusBadge
 *
 * Renders a coloured pill for user statuses OR request statuses.
 * Determines the type automatically from the status string.
 *
 * @param {string} status  — e.g. "ACTIVE" | "PENDING_APPROVAL"
 * @param {string} [className]
 */
export function StatusBadge({ status, className }) {
  if (!status) return null;

  // Determine label & colour
  let label, color;

  if (status in USER_STATUS_LABELS) {
    label = USER_STATUS_LABELS[status];
    color = USER_STATUS_COLORS[status];
  } else if (status in REQUEST_STATUS_LABELS) {
    label = REQUEST_STATUS_LABELS[status];
    color = REQUEST_STATUS_COLORS[status];
  } else {
    label = status;
    color = "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400";
  }

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        color,
        className
      )}
    >
      {label}
    </span>
  );
}

export default StatusBadge;
