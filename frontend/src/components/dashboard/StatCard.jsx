"use client";

import { useEffect, useRef, useState } from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * useCountUp — animates a number from 0 to `target` over `duration` ms.
 */
function useCountUp(target, duration = 800, enabled = true) {
  const [count, setCount] = useState(0);
  const raf = useRef(null);

  useEffect(() => {
    if (!enabled) { setCount(target); return; }
    const start = performance.now();
    const startVal = 0;

    const tick = (now) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setCount(Math.round(startVal + (target - startVal) * eased));
      if (progress < 1) raf.current = requestAnimationFrame(tick);
    };

    raf.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf.current);
  }, [target, duration, enabled]);

  return count;
}

/**
 * StatCard
 *
 * @param {string} title — Card label
 * @param {number} value — Numeric value to display
 * @param {string} [formatted] — Pre-formatted string (overrides animated count)
 * @param {React.ReactNode} [icon] — Icon component
 * @param {string} [iconColor] — Tailwind bg colour class for icon bg
 * @param {number} [trend] — Percentage change (positive = up, negative = down)
 * @param {string} [trendLabel] — E.g. "vs last month"
 * @param {string} [className]
 */
export function StatCard({
  title,
  value = 0,
  formatted,
  icon,
  iconColor = "bg-primary/10 text-primary",
  trend,
  trendLabel = "vs last period",
  className,
}) {
  const animated = useCountUp(typeof value === "number" ? value : 0);

  const TrendIcon =
    trend > 0 ? TrendingUp : trend < 0 ? TrendingDown : Minus;
  const trendColor =
    trend > 0
      ? "text-green-600 dark:text-green-400"
      : trend < 0
      ? "text-red-600 dark:text-red-400"
      : "text-muted-foreground";

  return (
    <div
      className={cn(
        "rounded-xl border bg-card p-6 shadow-sm hover:shadow-md transition-shadow",
        className
      )}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1 min-w-0">
          <p className="text-sm font-medium text-muted-foreground truncate">{title}</p>
          <p className="text-2xl font-semibold tracking-tight text-foreground tabular-nums">
            {formatted ?? animated.toLocaleString()}
          </p>

          {trend !== undefined && (
            <div className={cn("flex items-center gap-1 text-xs", trendColor)}>
              <TrendIcon className="h-3.5 w-3.5 shrink-0" />
              <span className="font-medium">{Math.abs(trend)}%</span>
              <span className="text-muted-foreground">{trendLabel}</span>
            </div>
          )}
        </div>

        {icon && (
          <div
            className={cn(
              "flex h-11 w-11 shrink-0 items-center justify-center rounded-xl",
              iconColor
            )}
          >
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}

export default StatCard;
