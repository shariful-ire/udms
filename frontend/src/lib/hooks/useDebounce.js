import { useState, useEffect } from "react";

/**
 * useDebounce
 *
 * Returns a debounced version of `value` that only updates after `delay` ms
 * of inactivity. Ideal for search inputs to avoid firing a query on every keystroke.
 *
 * @param {any} value - The value to debounce.
 * @param {number} [delay=400] - Delay in milliseconds.
 * @returns {any} The debounced value.
 *
 * Usage:
 *   const [search, setSearch] = useState("");
 *   const debouncedSearch = useDebounce(search, 400);
 *   // Use debouncedSearch in your query, not search
 */
export function useDebounce(value, delay = 400) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

export default useDebounce;
