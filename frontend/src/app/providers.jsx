"use client";

import { useEffect } from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { Toaster } from "sonner";
import { queryClient } from "@/lib/queryClient";
import { authApi, getAccessToken } from "@/lib/axios";
import { useAuthStore } from "@/store/authStore";

function SessionHydrator() {
  const { loginSuccess, setHydrated } = useAuthStore();

  useEffect(() => {
    authApi
      .me()
      .then((res) => {
        const { user } = res.data.data;
        const token = getAccessToken();
        loginSuccess(token ?? "", user);
      })
      .catch(() => {
        setHydrated();
      });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return null;
}

export function Providers({ children }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
      <QueryClientProvider client={queryClient}>
        <SessionHydrator />
        {children}
        <Toaster position="top-right" richColors closeButton />
      </QueryClientProvider>
    </ThemeProvider>
  );
}
