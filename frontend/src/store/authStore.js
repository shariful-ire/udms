/**
 * Zustand auth store
 * Holds the authenticated user, access token in memory, and derived flags.
 * The refresh token lives in an HttpOnly cookie — never touched directly by JS.
 */
import { create } from "zustand";
import { setAccessToken as axiosSetToken, clearTokens } from "@/lib/axios";

const useAuthStore = create((set, get) => ({
  // ── State ──────────────────────────────────────────────────────────────
  user: null,         // Full user profile object from /auth/me
  accessToken: null,  // In-memory only — never persisted to storage
  isHydrated: false,  // True after initial /auth/me check completes

  // ── Derived ────────────────────────────────────────────────────────────
  isAuthenticated: () => !!get().accessToken && !!get().user,

  // ── Actions ────────────────────────────────────────────────────────────

  /**
   * Called after successful login / token refresh.
   * Sets access token in store and syncs to Axios instance.
   */
  setAccessToken: (token) => {
    axiosSetToken(token);
    set({ accessToken: token });
  },

  /**
   * Called after successful login or profile fetch.
   */
  setUser: (user) => set({ user }),

  /**
   * Full login — sets both token and user simultaneously.
   */
  loginSuccess: (token, user) => {
    axiosSetToken(token);
    set({ accessToken: token, user, isHydrated: true });
  },

  /**
   * Clear all auth state — called on logout or session expiry.
   */
  logout: () => {
    clearTokens();
    set({ accessToken: null, user: null, isHydrated: true });
  },

  /**
   * Mark hydration complete (e.g. after /auth/me returns 401 on first load).
   */
  setHydrated: () => set({ isHydrated: true }),

  /**
   * Update specific user fields (e.g. after profile edit).
   */
  updateUser: (patch) =>
    set((state) => ({
      user: state.user ? { ...state.user, ...patch } : state.user,
    })),
}));

export { useAuthStore };
export default useAuthStore;
