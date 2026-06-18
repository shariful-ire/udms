import { redirect } from "next/navigation";

// The middleware handles the redirect, but this is a server-side fallback.
export default function RootPage() {
  redirect("/login");
}
