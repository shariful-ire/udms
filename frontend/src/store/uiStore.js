/**
 * Zustand UI store
 * Manages sidebar collapse state, active modals, and theme.
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";

const useUIStore = create(
  persist(
    (set, get) => ({
      // ── Sidebar ──────────────────────────────────────────────────────────
      sidebarCollapsed: false,
      toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
      setSidebarCollapsed: (val) => set({ sidebarCollapsed: val }),

      // ── Mobile sidebar drawer ────────────────────────────────────────────
      mobileSidebarOpen: false,
      setMobileSidebarOpen: (val) => set({ mobileSidebarOpen: val }),
      toggleMobileSidebar: () =>
        set((s) => ({ mobileSidebarOpen: !s.mobileSidebarOpen })),

      // ── Theme ────────────────────────────────────────────────────────────
      // Managed by next-themes; store only acts as a preference cache
      theme: "system", // "light" | "dark" | "system"
      setTheme: (theme) => set({ theme }),

      // ── Modals ───────────────────────────────────────────────────────────
      activeModals: {}, // { [modalId]: { open: boolean, data: any } }

      openModal: (id, data = null) =>
        set((s) => ({
          activeModals: { ...s.activeModals, [id]: { open: true, data } },
        })),

      closeModal: (id) =>
        set((s) => ({
          activeModals: {
            ...s.activeModals,
            [id]: { open: false, data: null },
          },
        })),

      getModal: (id) => get().activeModals[id] ?? { open: false, data: null },

      closeAllModals: () =>
        set((s) => {
          const closed = {};
          Object.keys(s.activeModals).forEach((k) => {
            closed[k] = { open: false, data: null };
          });
          return { activeModals: closed };
        }),

      // ── Notification / toast queue (non-toast lib emergency fallback) ─────
      notifications: [],

      addNotification: (notif) =>
        set((s) => ({
          notifications: [
            ...s.notifications,
            { id: Date.now(), ...notif },
          ],
        })),

      removeNotification: (id) =>
        set((s) => ({
          notifications: s.notifications.filter((n) => n.id !== id),
        })),
    }),
    {
      name: "udms-ui",
      // Only persist sidebar state and theme — modals should not persist
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        theme: state.theme,
      }),
    }
  )
);

export { useUIStore };
export default useUIStore;
