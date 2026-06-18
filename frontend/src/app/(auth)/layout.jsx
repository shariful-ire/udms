import Link from "next/link";

export default function AuthLayout({ children }) {
  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* ── Left panel (branding) — hidden on mobile ── */}
      <div className="hidden lg:flex flex-col justify-between bg-gray-950 text-white p-12 relative overflow-hidden">
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 w-96 h-96 rounded-full bg-primary blur-3xl -translate-x-1/2 -translate-y-1/2" />
          <div className="absolute bottom-0 right-0 w-96 h-96 rounded-full bg-purple-600 blur-3xl translate-x-1/2 translate-y-1/2" />
        </div>

        <div className="relative z-10">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
              <span className="text-white font-bold text-lg">U</span>
            </div>
            <span className="font-semibold text-lg tracking-tight">UDMS</span>
          </div>
        </div>

        <div className="relative z-10 space-y-6">
          <blockquote className="space-y-2">
            <p className="text-2xl font-semibold leading-snug">
              "Streamlining university dining management for a better campus experience."
            </p>
          </blockquote>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center text-white font-semibold">
              P
            </div>
            <div>
              <p className="text-sm font-medium">University Administration</p>
              <p className="text-sm text-white/60">Dining Services Portal</p>
            </div>
          </div>
        </div>

        <div className="relative z-10">
          <p className="text-sm text-white/40">
            © {new Date().getFullYear()} University Dining Management System
          </p>
        </div>
      </div>

      {/* ── Right panel (form) ── */}
      <div className="flex flex-col items-center justify-center p-6 sm:p-10 bg-background">
        {/* Mobile logo */}
        <div className="lg:hidden mb-8 flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-primary flex items-center justify-center">
            <span className="text-white font-bold text-base">U</span>
          </div>
          <span className="font-semibold text-lg">UDMS</span>
        </div>

        <div className="w-full max-w-sm">{children}</div>

        <p className="mt-8 text-xs text-muted-foreground">
          &copy; {new Date().getFullYear()} University Dining Management System
        </p>
      </div>
    </div>
  );
}
