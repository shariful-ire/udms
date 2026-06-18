"use client";

import { useState } from "react";
import { cn, getInitials } from "@/lib/utils";

const sizeMap = {
  xs: "h-6 w-6 text-[10px]",
  sm: "h-8 w-8 text-xs",
  md: "h-10 w-10 text-sm",
  lg: "h-12 w-12 text-base",
  xl: "h-16 w-16 text-lg",
  "2xl": "h-24 w-24 text-2xl",
};

/**
 * Avatar
 *
 * Displays a user avatar image with a graceful fallback to initials.
 *
 * @param {string} src - Image URL
 * @param {string} name - User's full name (used for initials fallback + alt text)
 * @param {string} size - "xs" | "sm" | "md" | "lg" | "xl" | "2xl"
 * @param {string} className
 */
export function Avatar({ src, name, size = "md", className }) {
  const [imgError, setImgError] = useState(false);
  const initials = getInitials(name);
  const sizeClass = sizeMap[size] ?? sizeMap.md;

  const baseClass = cn(
    "relative inline-flex shrink-0 items-center justify-center rounded-full",
    "font-semibold select-none overflow-hidden",
    sizeClass,
    className
  );

  if (src && !imgError) {
    return (
      <div className={baseClass}>
        <img
          src={src}
          alt={name ?? "User avatar"}
          className="h-full w-full object-cover"
          onError={() => setImgError(true)}
        />
      </div>
    );
  }

  // Deterministic background colour from name
  const colors = [
    "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
    "bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300",
    "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
    "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
    "bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300",
    "bg-teal-100 text-teal-700 dark:bg-teal-900/40 dark:text-teal-300",
    "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300",
    "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300",
  ];
  const colorIndex =
    name
      ? Array.from(name).reduce((acc, c) => acc + c.charCodeAt(0), 0) % colors.length
      : 0;
  const colorClass = colors[colorIndex];

  return (
    <div className={cn(baseClass, colorClass)}>
      {initials}
    </div>
  );
}

export default Avatar;
