from enum import Enum
from typing import List, Set, Callable
from functools import wraps

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PermissionDeniedException, InsufficientPermissionsException


# ─── Role Enum ───────────────────────────────────────────────────────────────
class UserRole(str, Enum):
    PROVOST = "PROVOST"
    DINING_MANAGER = "DINING_MANAGER"
    CUSTOMER = "CUSTOMER"
    NON_CUSTOMER = "NON_CUSTOMER"


# ─── Permission Enum ─────────────────────────────────────────────────────────
class Permission(str, Enum):
    # User management (Provost only)
    MANAGE_USERS = "manage_users"
    VIEW_ALL_USERS = "view_all_users"
    ASSIGN_MANAGER = "assign_manager"
    VIEW_AUDIT_LOGS = "view_audit_logs"

    # Dining operations (Manager + Provost)
    MANAGE_MEAL_SCHEDULES = "manage_meal_schedules"
    MANAGE_DAILY_MENUS = "manage_daily_menus"
    MANAGE_CUSTOMERS = "manage_customers"
    MANAGE_EXPENSES = "manage_expenses"
    APPROVE_MEAL_REQUESTS = "approve_meal_requests"

    # Earnings
    MANAGE_EARNINGS = "manage_earnings"

    # Member Payments
    MANAGE_MEMBER_PAYMENTS = "manage_member_payments"
    SUBMIT_PAYMENT_PROOF = "submit_payment_proof"
    TOGGLE_USER_STATUS = "toggle_user_status"

    # Reports (Manager + Provost)
    VIEW_FINANCIAL_REPORTS = "view_financial_reports"

    # Student operations (Customer only)
    ADD_PERSONAL_MEAL = "add_personal_meal"
    CANCEL_PERSONAL_MEAL = "cancel_personal_meal"
    VIEW_OWN_MEAL_HISTORY = "view_own_meal_history"

    # Non-customer operations
    SUBMIT_MEAL_REQUEST = "submit_meal_request"

    # Shared (all authenticated users)
    VIEW_MENU_AND_SCHEDULES = "view_menu_and_schedules"
    MANAGE_OWN_PROFILE = "manage_own_profile"
    VIEW_SETTINGS = "view_settings"


# ─── Role-to-Permission mapping ──────────────────────────────────────────────
ROLE_PERMISSIONS: dict[UserRole, Set[Permission]] = {
    UserRole.PROVOST: {
        Permission.MANAGE_USERS,
        Permission.VIEW_ALL_USERS,
        Permission.ASSIGN_MANAGER,
        Permission.VIEW_AUDIT_LOGS,
        Permission.VIEW_FINANCIAL_REPORTS,
        Permission.VIEW_MENU_AND_SCHEDULES,
        Permission.MANAGE_OWN_PROFILE,
        Permission.VIEW_SETTINGS,
        Permission.MANAGE_EXPENSES,
        Permission.MANAGE_EARNINGS,
        Permission.MANAGE_MEAL_SCHEDULES,
        Permission.MANAGE_DAILY_MENUS,
        Permission.MANAGE_CUSTOMERS,
        Permission.MANAGE_MEMBER_PAYMENTS,
        Permission.TOGGLE_USER_STATUS,
        Permission.APPROVE_MEAL_REQUESTS,
    },
    UserRole.DINING_MANAGER: {
        Permission.MANAGE_MEAL_SCHEDULES,
        Permission.MANAGE_DAILY_MENUS,
        Permission.MANAGE_CUSTOMERS,
        Permission.MANAGE_EXPENSES,
        Permission.MANAGE_EARNINGS,
        Permission.MANAGE_MEMBER_PAYMENTS,
        Permission.TOGGLE_USER_STATUS,
        Permission.APPROVE_MEAL_REQUESTS,
        Permission.VIEW_FINANCIAL_REPORTS,
        Permission.VIEW_MENU_AND_SCHEDULES,
        Permission.MANAGE_OWN_PROFILE,
        Permission.VIEW_SETTINGS,
    },
    UserRole.CUSTOMER: {
        Permission.SUBMIT_PAYMENT_PROOF,
        Permission.ADD_PERSONAL_MEAL,
        Permission.CANCEL_PERSONAL_MEAL,
        Permission.VIEW_OWN_MEAL_HISTORY,
        Permission.VIEW_MENU_AND_SCHEDULES,
        Permission.MANAGE_OWN_PROFILE,
        Permission.VIEW_SETTINGS,
    },
    UserRole.NON_CUSTOMER: {
        Permission.SUBMIT_MEAL_REQUEST,
        Permission.VIEW_MENU_AND_SCHEDULES,
        Permission.MANAGE_OWN_PROFILE,
        Permission.VIEW_SETTINGS,
    },
}

# Dining Manager permissions that Provost inherits when no active manager exists
DINING_MANAGER_PERMISSIONS: Set[Permission] = ROLE_PERMISSIONS[UserRole.DINING_MANAGER]


def get_effective_permissions(
    role: UserRole,
    has_active_dining_manager: bool = True,
) -> Set[Permission]:
    """
    Get effective permissions for a user role.
    Provost auto-inherits Dining Manager permissions if no active manager exists.
    """
    base_permissions = ROLE_PERMISSIONS.get(role, set())

    if role == UserRole.PROVOST and not has_active_dining_manager:
        return base_permissions | DINING_MANAGER_PERMISSIONS

    return base_permissions


def has_permission(
    role: UserRole,
    permission: Permission,
    has_active_dining_manager: bool = True,
) -> bool:
    """Check if a role has a specific permission."""
    effective = get_effective_permissions(role, has_active_dining_manager)
    return permission in effective


def require_roles(*roles: UserRole):
    """
    Dependency factory — requires current user to have one of the given roles.
    Usage:
        @router.get("/admin", dependencies=[Depends(require_roles(UserRole.PROVOST))])
    """
    from app.api.v1.deps import get_current_active_user

    async def _require_roles(current_user=Depends(get_current_active_user)):
        if UserRole(current_user.role) not in roles:
            raise PermissionDeniedException(
                f"This action requires one of the following roles: {', '.join(r.value for r in roles)}"
            )
        return current_user

    return _require_roles


def require_permission(permission: Permission):
    """
    Dependency factory — requires current user to have a specific permission.
    Also respects Provost auto-elevation logic.
    """
    from app.api.v1.deps import get_current_active_user, get_db
    from app.repositories.user_repo import UserRepository

    async def _require_permission(
        current_user=Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db),
    ):
        role = UserRole(current_user.role)
        has_active_manager = True

        if role == UserRole.PROVOST:
            user_repo = UserRepository(db)
            has_active_manager = await user_repo.has_active_dining_manager()

        if not has_permission(role, permission, has_active_manager):
            raise PermissionDeniedException(
                f"Permission '{permission.value}' required to perform this action"
            )
        return current_user

    return _require_permission


# ─── Role check helpers ───────────────────────────────────────────────────────
def is_provost(role: str) -> bool:
    return role == UserRole.PROVOST.value


def is_manager_or_above(role: str) -> bool:
    return role in (UserRole.PROVOST.value, UserRole.DINING_MANAGER.value)


def is_customer(role: str) -> bool:
    return role == UserRole.CUSTOMER.value


def is_non_customer(role: str) -> bool:
    return role == UserRole.NON_CUSTOMER.value


def can_manage_dining(role: str, has_active_manager: bool = True) -> bool:
    """Provost can manage dining when no active manager exists."""
    if role == UserRole.DINING_MANAGER.value:
        return True
    if role == UserRole.PROVOST.value and not has_active_manager:
        return True
    return False
