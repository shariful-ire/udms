// ================================================================
// UDMS — Application-wide constants
// ================================================================

export const ROLES = {
  PROVOST: "PROVOST",
  DINING_MANAGER: "DINING_MANAGER",
  CUSTOMER: "CUSTOMER",
  NON_CUSTOMER: "NON_CUSTOMER",
};

export const ROLE_LABELS = {
  PROVOST: "Provost",
  DINING_MANAGER: "Dining Manager",
  CUSTOMER: "Customer",
  NON_CUSTOMER: "Student",
};

export const ROLE_COLORS = {
  PROVOST:        "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
  DINING_MANAGER: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  CUSTOMER:       "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  NON_CUSTOMER:   "bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400",
};

export const MEAL_TYPES = ["BREAKFAST", "LUNCH", "DINNER"];

export const MEAL_TYPE_LABELS = {
  BREAKFAST: "Breakfast",
  LUNCH: "Lunch",
  DINNER: "Dinner",
};

export const MEAL_TYPE_ICONS = {
  BREAKFAST: "☀️",
  LUNCH: "🌤",
  DINNER: "🌙",
};

export const MEAL_TYPE_COLORS = {
  BREAKFAST: "bg-amber-50 border-amber-200 dark:bg-amber-900/20 dark:border-amber-800",
  LUNCH:     "bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800",
  DINNER:    "bg-indigo-50 border-indigo-200 dark:bg-indigo-900/20 dark:border-indigo-800",
};

export const USER_STATUSES = {
  ACTIVE:    "ACTIVE",
  INACTIVE:  "INACTIVE",
  SUSPENDED: "SUSPENDED",
};

export const USER_STATUS_LABELS = {
  ACTIVE:    "Active",
  INACTIVE:  "Inactive",
  SUSPENDED: "Suspended",
};

export const USER_STATUS_COLORS = {
  ACTIVE:    "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  INACTIVE:  "bg-gray-100 text-gray-600 dark:bg-gray-900/30 dark:text-gray-400",
  SUSPENDED: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

export const REQUEST_STATUSES = {
  PENDING_PAYMENT:  "PENDING_PAYMENT",
  PENDING_APPROVAL: "PENDING_APPROVAL",
  APPROVED:  "APPROVED",
  REJECTED:  "REJECTED",
  CANCELLED: "CANCELLED",
};

export const REQUEST_STATUS_LABELS = {
  PENDING_PAYMENT:  "Pending Payment",
  PENDING_APPROVAL: "Pending Approval",
  APPROVED:  "Approved",
  REJECTED:  "Rejected",
  CANCELLED: "Cancelled",
};

export const REQUEST_STATUS_COLORS = {
  PENDING_PAYMENT:  "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
  PENDING_APPROVAL: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  APPROVED:  "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  REJECTED:  "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  CANCELLED: "bg-gray-100 text-gray-600 dark:bg-gray-900/30 dark:text-gray-400",
};

export const PAYMENT_METHODS = [
  { value: "CASH",            label: "Cash" },
  { value: "MOBILE_BANKING",  label: "Mobile Banking (bKash/Nagad)" },
  { value: "BANK_TRANSFER",   label: "Bank Transfer" },
  { value: "OTHER",           label: "Other" },
];

export const EXPENSE_CATEGORIES = [
  { value: "FOOD_PURCHASE", label: "Food Purchase",  icon: "🛒", color: "text-green-600" },
  { value: "UTILITIES",     label: "Utilities",      icon: "⚡", color: "text-yellow-600" },
  { value: "SALARY",        label: "Salary",         icon: "👥", color: "text-blue-600" },
  { value: "EQUIPMENT",     label: "Equipment",      icon: "🔧", color: "text-purple-600" },
  { value: "MAINTENANCE",   label: "Maintenance",    icon: "🏗",  color: "text-orange-600" },
  { value: "MISCELLANEOUS", label: "Miscellaneous",  icon: "📦", color: "text-gray-600" },
];

export const EXPENSE_CATEGORY_COLORS = {
  FOOD_PURCHASE: "#22c55e",
  UTILITIES:     "#f59e0b",
  SALARY:        "#3b82f6",
  EQUIPMENT:     "#8b5cf6",
  MAINTENANCE:   "#f97316",
  MISCELLANEOUS: "#94a3b8",
};

export const EARNING_CATEGORIES = [
  { value: "MEAL_PAYMENT", label: "Meal Payment",  icon: "🍽", color: "text-green-600" },
  { value: "DEPOSIT",      label: "Deposit",       icon: "💰", color: "text-blue-600" },
  { value: "GRANT",        label: "Grant",         icon: "🏛",  color: "text-purple-600" },
  { value: "OTHER",        label: "Other",         icon: "📋", color: "text-gray-600" },
];

export const EARNING_CATEGORY_COLORS = {
  MEAL_PAYMENT: "#22c55e",
  DEPOSIT:      "#3b82f6",
  GRANT:        "#8b5cf6",
  OTHER:        "#94a3b8",
};

export const REPORT_PERIODS = [
  { value: "daily",   label: "Daily" },
  { value: "weekly",  label: "Weekly" },
  { value: "monthly", label: "Monthly" },
  { value: "yearly",  label: "Yearly" },
];

export const AUDIT_ACTIONS = [
  "USER_CREATED", "USER_DELETED", "USER_SUSPENDED", "USER_ACTIVATED",
  "ROLE_CHANGED", "PASSWORD_RESET", "LOGIN_SUCCESS", "LOGIN_FAILED",
  "MEAL_ADDED", "MEAL_CANCELLED", "MEAL_CANCELLED_BY_MANAGER",
  "MENU_CREATED", "MENU_UPDATED", "MENU_CANCELLED",
  "EXPENSE_CREATED", "EXPENSE_UPDATED", "EXPENSE_DELETED",
  "REQUEST_SUBMITTED", "REQUEST_APPROVED", "REQUEST_REJECTED",
  "CUSTOMER_ADDED", "CUSTOMER_REMOVED",
  "MANAGER_ASSIGNED", "MANAGER_REMOVED",
  "SETTINGS_UPDATED", "REPORT_GENERATED",
];

// Permission matrix used by usePermissions hook
export const ROLE_PERMISSIONS = {
  PROVOST: [
    "VIEW_USERS", "CREATE_USER", "UPDATE_USER", "DELETE_USER",
    "SUSPEND_USER", "ACTIVATE_USER", "ASSIGN_MANAGER", "REMOVE_MANAGER",
    "VIEW_AUDIT_LOGS", "VIEW_REPORTS", "MANAGE_SETTINGS",
    "MANAGE_SCHEDULES", "MANAGE_MENUS", "MANAGE_EXPENSES",
    "MANAGE_CUSTOMERS", "REVIEW_REQUESTS",
  ],
  DINING_MANAGER: [
    "VIEW_REPORTS", "MANAGE_SCHEDULES", "MANAGE_MENUS",
    "MANAGE_EXPENSES", "MANAGE_CUSTOMERS", "REVIEW_REQUESTS",
  ],
  CUSTOMER: [
    "VIEW_SCHEDULE", "VIEW_MENU", "ADD_MEAL", "CANCEL_MEAL",
    "VIEW_MEAL_HISTORY", "VIEW_MEAL_SUMMARY",
  ],
  NON_CUSTOMER: [
    "VIEW_SCHEDULE", "VIEW_MENU", "SUBMIT_REQUEST",
    "VIEW_MY_REQUESTS", "VIEW_PAYMENT_HISTORY",
  ],
};

// Sidebar navigation — what each role sees
export const NAV_LINKS = {
  PROVOST: [
    { href: "/dashboard",  label: "Dashboard",   icon: "LayoutDashboard" },
    { href: "/users",      label: "Users",       icon: "Users" },
    { href: "/dining",     label: "Dining",      icon: "UtensilsCrossed" },
    { href: "/payments",   label: "Payments",    icon: "Receipt" },
    { href: "/expenses",   label: "Expenses",    icon: "CreditCard" },
    { href: "/earnings",   label: "Earnings",    icon: "TrendingUp" },
    { href: "/reports",    label: "Reports",     icon: "BarChart3" },
    { href: "/audit",      label: "Audit Logs",  icon: "Shield" },
    { href: "/settings",   label: "Settings",    icon: "Settings" },
  ],
  DINING_MANAGER: [
    { href: "/dashboard",          label: "Dashboard",   icon: "LayoutDashboard" },
    { href: "/dining",             label: "Dining",      icon: "UtensilsCrossed" },
    { href: "/dining/customers",   label: "Customers",   icon: "UserCheck" },
    { href: "/payments",           label: "Payments",    icon: "Receipt" },
    { href: "/requests",           label: "Requests",    icon: "ClipboardList" },
    { href: "/expenses",           label: "Expenses",    icon: "CreditCard" },
    { href: "/earnings",           label: "Earnings",    icon: "TrendingUp" },
    { href: "/reports",            label: "Reports",     icon: "BarChart3" },
  ],
  CUSTOMER: [
    { href: "/dashboard",      label: "Dashboard",    icon: "LayoutDashboard" },
    { href: "/meals",          label: "My Meals",     icon: "UtensilsCrossed" },
    { href: "/meals/history",  label: "Meal History", icon: "CalendarDays" },
    { href: "/meals/summary",  label: "Summary",      icon: "PieChart" },
    { href: "/payments",       label: "My Payments",  icon: "Receipt" },
  ],
  NON_CUSTOMER: [
    { href: "/dashboard",  label: "Dashboard",  icon: "LayoutDashboard" },
    { href: "/requests",   label: "My Requests", icon: "ClipboardList" },
  ],
};

export const PER_PAGE_OPTIONS = [10, 20, 50, 100];
export const DEFAULT_PER_PAGE = 20;

export const CURRENCY_SYMBOL = "৳";
export const DATE_FORMAT = "MMM d, yyyy";
export const DATETIME_FORMAT = "MMM d, yyyy HH:mm";
