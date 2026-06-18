import { useState, useCallback, useMemo } from "react";
import { DEFAULT_PER_PAGE } from "@/lib/constants";

/**
 * usePagination
 *
 * Manages pagination state for server-side paginated tables.
 * Returns params to pass to API calls and handlers to update them.
 *
 * @param {object} [options]
 * @param {number} [options.initialPage=1]
 * @param {number} [options.initialPerPage=20]
 *
 * Usage:
 *   const { page, perPage, params, setPage, setPerPage, reset } = usePagination();
 *   const { data } = useQuery({ queryKey: [..., params], queryFn: () => api.list(params) });
 */
export function usePagination(options = {}) {
  const {
    initialPage = 1,
    initialPerPage = DEFAULT_PER_PAGE,
  } = options;

  const [page, setPageState] = useState(initialPage);
  const [perPage, setPerPageState] = useState(initialPerPage);

  const setPage = useCallback((newPage) => {
    setPageState(Math.max(1, Number(newPage)));
  }, []);

  const setPerPage = useCallback((newPerPage) => {
    setPerPageState(Number(newPerPage));
    setPageState(1); // Reset to page 1 when page size changes
  }, []);

  const reset = useCallback(() => {
    setPageState(initialPage);
    setPerPageState(initialPerPage);
  }, [initialPage, initialPerPage]);

  const goNext = useCallback((totalPages) => {
    setPageState((p) => Math.min(p + 1, totalPages));
  }, []);

  const goPrev = useCallback(() => {
    setPageState((p) => Math.max(p - 1, 1));
  }, []);

  const params = useMemo(
    () => ({ page, per_page: perPage }),
    [page, perPage]
  );

  return {
    page,
    perPage,
    params,
    setPage,
    setPerPage,
    reset,
    goNext,
    goPrev,
  };
}

export default usePagination;
