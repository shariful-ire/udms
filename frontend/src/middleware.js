import { NextResponse } from "next/server";

/**
 * Route protection middleware.
 *
 * Strategy:
 * - Auth pages (/login, /register, etc.) are publicly accessible
 * - All /dashboard/* routes require a valid session (checked via /api/auth/check)
 * - Role-based sub-route access is enforced per-page via usePermissions() on the client
 *   (server middleware only checks "is logged in", not granular permissions)
 * - Root "/" redirects to /dashboard if authenticated, /login if not
 */

const PUBLIC_PATHS = [
  "/login",
  "/register",
  "/forgot-password",
  "/reset-password",
  "/verify-email",
];

const AUTH_PATHS = [
  "/dashboard",
  "/users",
  "/dining",
  "/meals",
  "/requests",
  "/expenses",
  "/reports",
  "/audit",
  "/settings",
  "/profile",
];

export function middleware(request) {
  const { pathname } = request.nextUrl;

  // Get access token from cookie (set by login response header)
  // Note: the actual access token lives in memory (Zustand), but we set a
  // non-HttpOnly presence flag cookie `udms_session` on login so middleware
  // can detect an active session without exposing the token.
  const sessionFlag = request.cookies.get("udms_session");
  const isAuthenticated = !!sessionFlag;

  // Root redirect
  if (pathname === "/") {
    return NextResponse.redirect(
      new URL(isAuthenticated ? "/dashboard" : "/login", request.url)
    );
  }

  // Redirect authenticated users away from auth pages
  const isPublicPath = PUBLIC_PATHS.some(
    (p) => pathname === p || pathname.startsWith(p + "/")
  );
  if (isPublicPath && isAuthenticated) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  // Redirect unauthenticated users to login from protected routes
  const isProtectedPath = AUTH_PATHS.some(
    (p) => pathname === p || pathname.startsWith(p + "/")
  );
  if (isProtectedPath && !isAuthenticated) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  // Match all paths except Next.js internals and static files
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|images|icons|api).*)",
  ],
};
