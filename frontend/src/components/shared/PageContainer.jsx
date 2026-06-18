import { cn } from "@/lib/utils";

/**
 * PageContainer
 *
 * Wraps page content with consistent horizontal padding and max-width.
 * Use as the outermost wrapper inside every dashboard page.
 */
export function PageContainer({ children, className }) {
  return (
    <div
      className={cn(
        "page-enter flex flex-col gap-6 px-4 py-6 sm:px-6 lg:px-8 max-w-screen-2xl mx-auto w-full",
        className
      )}
    >
      {children}
    </div>
  );
}

export default PageContainer;
