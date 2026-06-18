import { cn } from "@/lib/utils";
import { Inbox } from "lucide-react";

/**
 * EmptyState
 *
 * Displayed when a list / table has no data.
 *
 * @param {React.ReactNode} [icon] — Override default icon
 * @param {string} title
 * @param {string} [description]
 * @param {React.ReactNode} [action] — CTA button / link
 * @param {string} [className]
 */
export function EmptyState({ icon, title, description, action, className }) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-4 rounded-xl border border-dashed",
        "bg-muted/20 px-6 py-16 text-center",
        className
      )}
    >
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-muted">
        {icon ?? <Inbox className="h-7 w-7 text-muted-foreground" />}
      </div>

      <div className="space-y-1.5">
        <h3 className="font-semibold text-foreground">{title}</h3>
        {description && (
          <p className="max-w-sm text-sm text-muted-foreground">{description}</p>
        )}
      </div>

      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}

export default EmptyState;
