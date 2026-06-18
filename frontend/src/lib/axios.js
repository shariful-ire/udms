/**
 * Axios instance with:
 * - Auto attach access token to every request
 * - Transparent refresh token rotation on 401
 * - Retry original request after successful refresh
 * - Redirect to /login on refresh failure
 */
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─── Axios instance ─────────────────────────────────────────────────────────
const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
  withCredentials: true, // Required for HttpOnly refresh token cookie
  timeout: 30000,
});

// ─── Token helpers ───────────────────────────────────────────────────────────
let accessToken = null;
let isRefreshing = false;
let refreshSubscribers = [];

const onRefreshed = (token) => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};

const addRefreshSubscriber = (cb) => {
  refreshSubscribers.push(cb);
};

export const setAccessToken = (token) => {
  accessToken = token;
};

export const getAccessToken = () => accessToken;

export const clearTokens = () => {
  accessToken = null;
};

// ─── Request interceptor ─────────────────────────────────────────────────────
api.interceptors.request.use(
  (config) => {
    if (accessToken) {
      config.headers["Authorization"] = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ─── Response interceptor ────────────────────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Only attempt refresh on 401 errors that haven't already been retried
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes("/auth/refresh") &&
      !originalRequest.url?.includes("/auth/login")
    ) {
      if (isRefreshing) {
        // Queue this request until refresh completes
        return new Promise((resolve, reject) => {
          addRefreshSubscriber((token) => {
            originalRequest.headers["Authorization"] = `Bearer ${token}`;
            resolve(api(originalRequest));
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Attempt to refresh — refresh token is in HttpOnly cookie
        const response = await api.post("/auth/refresh");
        const newToken = response.data?.data?.access_token;

        if (!newToken) throw new Error("No access token in refresh response");

        setAccessToken(newToken);

        // Update auth store if available
        if (typeof window !== "undefined") {
          const { useAuthStore } = await import("@/store/authStore");
          useAuthStore.getState().setAccessToken(newToken);
        }

        onRefreshed(newToken);
        isRefreshing = false;

        // Retry original request with new token
        originalRequest.headers["Authorization"] = `Bearer ${newToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        isRefreshing = false;
        refreshSubscribers = [];

        // Clear auth state and redirect to login
        clearTokens();
        if (typeof window !== "undefined") {
          const { useAuthStore } = await import("@/store/authStore").catch(() => ({ useAuthStore: null }));
          if (useAuthStore) useAuthStore.getState().logout();

          // Only redirect if we're on a protected page — never redirect from login/public pages
          // (avoids infinite loop when SessionHydrator runs on unauthenticated first load)
          const publicPaths = ["/login", "/register", "/forgot-password", "/reset-password", "/verify-email"];
          const isOnPublicPage = publicPaths.some((p) => window.location.pathname.startsWith(p));
          if (!isOnPublicPage) {
            window.location.href = "/login?session=expired";
          }
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// ─── API convenience methods ─────────────────────────────────────────────────

export const authApi = {
  register: (data) => api.post("/auth/register", data),
  verifyEmail: (data) => api.post("/auth/verify-email", data),
  resendVerification: (data) => api.post("/auth/resend-verification", data),
  login: (data) => api.post("/auth/login", data),
  refresh: () => api.post("/auth/refresh"),
  logout: () => api.post("/auth/logout"),
  forgotPassword: (data) => api.post("/auth/forgot-password", data),
  verifyOtp: (data) => api.post("/auth/verify-otp", data),
  resetPassword: (data) => api.post("/auth/reset-password", data),
  me: () => api.get("/auth/me"),
};

export const usersApi = {
  list: (params) => api.get("/users", { params }),
  create: (data) => api.post("/users", data),
  get: (id) => api.get(`/users/${id}`),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
  suspend: (id) => api.patch(`/users/${id}/suspend`),
  activate: (id) => api.patch(`/users/${id}/activate`),
  assignManager: (id) => api.patch(`/users/${id}/assign-manager`),
  removeManager: (id) => api.patch(`/users/${id}/remove-manager`),
  stats: () => api.get("/users/stats"),
  recent: (params) => api.get("/users/recent", { params }),
};

export const profileApi = {
  get: () => api.get("/profile"),
  update: (data) => api.put("/profile", data),
  changePassword: (data) => api.post("/profile/change-password", data),
  uploadAvatar: (formData) =>
    api.post("/profile/avatar", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
};

export const diningApi = {
  getSchedules: () => api.get("/dining/schedules"),
  updateSchedule: (mealType, data) => api.put(`/dining/schedules/${mealType}`, data),
  getMenus: (params) => api.get("/dining/menus", { params }),
  getMenuForDate: (date) => api.get(`/dining/menus/${date}`),
  createMenu: (data) => api.post("/dining/menus", data),
  updateMenu: (id, data) => api.put(`/dining/menus/${id}`, data),
  cancelMenu: (id) => api.patch(`/dining/menus/${id}/cancel`),
  deleteMenu: (id) => api.delete(`/dining/menus/${id}`),
};

export const customersApi = {
  list: (params) => api.get("/customers", { params }),
  add: (userId) => api.post(`/customers/${userId}`),
  remove: (userId) => api.delete(`/customers/${userId}`),
};

export const mealsApi = {
  today: () => api.get("/meals/today"),
  add: (data) => api.post("/meals", data),
  cancel: (id) => api.delete(`/meals/${id}`),
  history: (params) => api.get("/meals/history", { params }),
  summary: (params) => api.get("/meals/summary", { params }),
};

export const requestsApi = {
  list: (params) => api.get("/requests", { params }),
  create: (data) => api.post("/requests", data),
  get: (id) => api.get(`/requests/${id}`),
  submitPayment: (id, data) => api.post(`/requests/${id}/payment`, data),
  approve: (id) => api.patch(`/requests/${id}/approve`),
  reject: (id, data) => api.patch(`/requests/${id}/reject`, data),
  cancel: (id) => api.delete(`/requests/${id}`),
};

export const expensesApi = {
  list: (params) => api.get("/expenses", { params }),
  create: (data) => api.post("/expenses", data),
  get: (id) => api.get(`/expenses/${id}`),
  update: (id, data) => api.put(`/expenses/${id}`, data),
  delete: (id) => api.delete(`/expenses/${id}`),
};

export const reportsApi = {
  daily: (params) => api.get("/reports/daily", { params }),
  weekly: (params) => api.get("/reports/weekly", { params }),
  monthly: (params) => api.get("/reports/monthly", { params }),
  yearly: (params) => api.get("/reports/yearly", { params }),
  export: (params) => api.get("/reports/export", { params, responseType: "blob" }),
};

export const auditApi = {
  list: (params) => api.get("/audit", { params }),
  get: (id) => api.get(`/audit/${id}`),
};

export const settingsApi = {
  get: () => api.get("/settings"),
  update: (data) => api.put("/settings", data),
};

export default api;
