import { cn } from "@/lib/utils";
import Link from "next/link";
import { ChevronRight } from "lucide-react";

/**
 * PageHeader
 *
 * @param {string} title — Page title
 * @param {string} [description] — Optional subtitle
 * @param {Array<{label, href?}>} [breadcrumbs] — Breadcrumb trail
 * @param {React.ReactNode} [action] — CTA button / element aligned to the right
 * @param {string} [className]
 */
export function PageHeader({ title, description, breadcrumbs, action, className }) {
  return (
    <div className={cn("flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between", className)}>
      <div className="space-y-1">
        {/* Breadcrumbs */}
        {breadcrumbs && breadcrumbs.length > 0 && (
          <nav className="flex items-center gap-1 text-xs text-muted-foreground" aria-label="Breadcrumb">
            {breadcrumbs.map((crumb, i) => (
              <span key={i} className="flex items-center gap-1">
                {i > 0 && <ChevronRight className="h-3 w-3 shrink-0" />}
                {crumb.href ? (
                  <Link href={crumb.href} className="hover:text-foreground transition-colors">
                    {crumb.label}
                  </Link>
                ) : (
                  <span className="text-foreground font-medium">{crumb.label}</span>
                )}
              </span>
            ))}
          </nav>
        )}

        {/* Title */}
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">{title}</h1>

        {/* Description */}
        {description && (
          <p className="text-sm text-muted-foreground">{description}</p>
        )}
      </div>

      {/* Action slot */}
      {action && (
        <div className="mt-3 sm:mt-0 shrink-0">{action}</div>
      )}
    </div>
  );
}

export default PageHeader;
