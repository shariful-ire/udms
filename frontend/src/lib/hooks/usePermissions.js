import { useAuthStore } from "@/store/authStore";
import { ROLE_PERMISSIONS, ROLES } from "@/lib/constants";

/**
 * usePermissions
 *
 * Returns helpers to check what the current user is allowed to do.
 *
 * Usage:
 *   const { can, role, isProvost, isDiningManager, isCustomer, isNonCustomer } = usePermissions();
 *   if (can("MANAGE_EXPENSES")) { ... }
 */
export function usePermissions() {
  const user = useAuthStore((s) => s.user);
  const role = user?.role ?? null;

  /**
   * Effective permissions — Provost inherits DINING_MANAGER permissions
   * when no active dining manager exists (handled via user.has_manager_elevation flag
   * set by the backend in /auth/me response).
   */
  const getPermissions = () => {
    if (!role) return [];
    const base = ROLE_PERMISSIONS[role] ?? [];
    // Backend sets `has_manager_elevation: true` on Provost when no manager exists
    if (role === ROLES.PROVOST && user?.has_manager_elevation) {
      const managerPerms = ROLE_PERMISSIONS[ROLES.DINING_MANAGER] ?? [];
      return [...new Set([...base, ...managerPerms])];
    }
    return base;
  };

  const permissions = getPermissions();

  /**
   * Check if the current user has a specific permission string.
   */
  const can = (permission) => permissions.includes(permission);

  /**
   * Check if the current user has ALL of the given permissions.
   */
  const canAll = (...perms) => perms.every((p) => permissions.includes(p));

  /**
   * Check if the current user has ANY of the given permissions.
   */
  const canAny = (...perms) => perms.some((p) => permissions.includes(p));

  /**
   * Check if the current user has a specific role.
   */
  const hasRole = (r) => role === r;

  /**
   * Check if the current user has any of the given roles.
   */
  const hasAnyRole = (...roles) => roles.includes(role);

  return {
    // Current role string
    role,
    // All effective permissions
    permissions,
    // Convenience checkers
    can,
    canAll,
    canAny,
    hasRole,
    hasAnyRole,
    // Role shorthands
    isProvost: role === ROLES.PROVOST,
    isDiningManager: role === ROLES.DINING_MANAGER,
    isCustomer: role === ROLES.CUSTOMER,
    isNonCustomer: role === ROLES.NON_CUSTOMER,
    // True if user can perform management operations
    isManager: role === ROLES.DINING_MANAGER || role === ROLES.PROVOST,
    // True if user has dining service enrollment
    isEnrolled: role === ROLES.CUSTOMER,
  };
}

export default usePermissions;
