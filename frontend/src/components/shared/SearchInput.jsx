"use client";

import { useState, useEffect, useRef } from "react";
import { Search, X } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * SearchInput
 *
 * Controlled or uncontrolled search box that calls `onSearch` after a debounce.
 *
 * @param {string} [value] — Controlled value (optional)
 * @param {function} onSearch — Called with the debounced search string
 * @param {number} [debounce=400] — Debounce delay in ms
 * @param {string} [placeholder="Search…"]
 * @param {string} [className]
 */
export function SearchInput({
  value: controlledValue,
  onSearch,
  debounce = 400,
  placeholder = "Search…",
  className,
  autoFocus = false,
}) {
  const isControlled = controlledValue !== undefined;
  const [localValue, setLocalValue] = useState(controlledValue ?? "");
  const timerRef = useRef(null);
  const inputRef = useRef(null);

  // Sync when controlled value changes externally
  useEffect(() => {
    if (isControlled) setLocalValue(controlledValue);
  }, [controlledValue, isControlled]);

  const handleChange = (e) => {
    const val = e.target.value;
    setLocalValue(val);

    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      onSearch?.(val);
    }, debounce);
  };

  const handleClear = () => {
    setLocalValue("");
    onSearch?.("");
    inputRef.current?.focus();
  };

  // Cleanup on unmount
  useEffect(() => () => clearTimeout(timerRef.current), []);

  return (
    <div className={cn("relative flex items-center", className)}>
      <Search
        className="absolute left-3 h-4 w-4 text-muted-foreground pointer-events-none"
        aria-hidden="true"
      />
      <input
        ref={inputRef}
        type="search"
        value={localValue}
        onChange={handleChange}
        placeholder={placeholder}
        autoFocus={autoFocus}
        className="h-9 w-full rounded-lg border border-input bg-background pl-9 pr-9 text-sm
          outline-none placeholder:text-muted-foreground
          focus:ring-2 focus:ring-ring transition-shadow"
        aria-label={placeholder}
      />
      {localValue && (
        <button
          type="button"
          onClick={handleClear}
          className="absolute right-2.5 flex h-5 w-5 items-center justify-center rounded-full
            text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
          aria-label="Clear search"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      )}
    </div>
  );
}

export function DateRangePicker({ startDate, endDate, onStartChange, onEndChange }) {
  return (
    <div className="flex items-center gap-2">
      <input
        type="date"
        value={startDate}
        onChange={(e) => onStartChange?.(e.target.value)}
        className="rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring transition-shadow"
        aria-label="Start date"
      />
      <span className="text-sm text-muted-foreground">–</span>
      <input
        type="date"
        value={endDate}
        onChange={(e) => onEndChange?.(e.target.value)}
        className="rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring transition-shadow"
        aria-label="End date"
      />
    </div>
  );
}

export default SearchInput;
