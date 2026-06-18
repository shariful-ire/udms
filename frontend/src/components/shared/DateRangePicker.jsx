"use client";

import { useState } from "react";
import { CalendarDays, ChevronDown } from "lucide-react";
import { format, subDays, startOfMonth, endOfMonth, startOfWeek, endOfWeek } from "date-fns";
import { cn } from "@/lib/utils";

const PRESETS = [
  {
    label: "Today",
    getRange: () => {
      const today = new Date();
      return { from: today, to: today };
    },
  },
  {
    label: "Last 7 days",
    getRange: () => ({ from: subDays(new Date(), 6), to: new Date() }),
  },
  {
    label: "Last 30 days",
    getRange: () => ({ from: subDays(new Date(), 29), to: new Date() }),
  },
  {
    label: "This month",
    getRange: () => ({ from: startOfMonth(new Date()), to: endOfMonth(new Date()) }),
  },
  {
    label: "This week",
    getRange: () => ({ from: startOfWeek(new Date(), { weekStartsOn: 1 }), to: endOfWeek(new Date(), { weekStartsOn: 1 }) }),
  },
];

/**
 * DateRangePicker
 *
 * Two date inputs (from / to) with quick-select presets dropdown.
 *
 * @param {{ from: Date|null, to: Date|null }} value
 * @param {function} onChange — Called with { from: Date, to: Date }
 * @param {string} [className]
 */
export function DateRangePicker({ value = {}, onChange, className }) {
  const [showPresets, setShowPresets] = useState(false);

  const formatVal = (d) => (d ? format(new Date(d), "yyyy-MM-dd") : "");

  const handleFrom = (e) => {
    const from = e.target.value ? new Date(e.target.value) : null;
    onChange?.({ ...value, from });
  };

  const handleTo = (e) => {
    const to = e.target.value ? new Date(e.target.value) : null;
    onChange?.({ ...value, to });
  };

  const applyPreset = (preset) => {
    onChange?.(preset.getRange());
    setShowPresets(false);
  };

  const inputClass =
    "h-9 rounded-lg border border-input bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-ring transition-shadow";

  return (
    <div className={cn("flex flex-wrap items-center gap-2", className)}>
      <CalendarDays className="h-4 w-4 text-muted-foreground shrink-0" aria-hidden />

      <input
        type="date"
        value={formatVal(value.from)}
        max={value.to ? formatVal(value.to) : undefined}
        onChange={handleFrom}
        className={inputClass}
        aria-label="Start date"
      />

      <span className="text-sm text-muted-foreground">to</span>

      <input
        type="date"
        value={formatVal(value.to)}
        min={value.from ? formatVal(value.from) : undefined}
        onChange={handleTo}
        className={inputClass}
        aria-label="End date"
      />

      {/* Presets */}
      <div className="relative">
        <button
          type="button"
          onClick={() => setShowPresets((v) => !v)}
          className="flex h-9 items-center gap-1 rounded-lg border border-input bg-background px-3 text-sm
            hover:bg-muted transition-colors"
        >
          Presets
          <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />
        </button>

        {showPresets && (
          <>
            <div
              className="fixed inset-0 z-30"
              onClick={() => setShowPresets(false)}
            />
            <div className="absolute right-0 top-10 z-40 min-w-[140px] rounded-xl border bg-popover shadow-lg p-1">
              {PRESETS.map((p) => (
                <button
                  key={p.label}
                  type="button"
                  onClick={() => applyPreset(p)}
                  className="w-full rounded-md px-3 py-2 text-left text-sm hover:bg-accent transition-colors"
                >
                  {p.label}
                </button>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default DateRangePicker;
