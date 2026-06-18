/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,jsx}",
    "./src/components/**/*.{js,jsx}",
    "./src/app/**/*.{js,jsx}",
    "./src/lib/**/*.{js,jsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: { "2xl": "1400px" },
    },
    extend: {
      // ─── Color system ────────────────────────────────────────────────
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // Brand colors
        brand: {
          50:  "hsl(221, 100%, 97%)",
          100: "hsl(221, 96%, 94%)",
          200: "hsl(221, 92%, 87%)",
          300: "hsl(221, 88%, 78%)",
          400: "hsl(221, 86%, 67%)",
          500: "hsl(221, 83%, 53%)",  // Primary brand
          600: "hsl(221, 80%, 45%)",
          700: "hsl(221, 76%, 38%)",
          800: "hsl(221, 70%, 30%)",
          900: "hsl(221, 64%, 22%)",
          950: "hsl(221, 60%, 14%)",
        },
        // Semantic status colors
        success: {
          DEFAULT: "hsl(153, 60%, 45%)",
          light: "hsl(153, 60%, 95%)",
          dark: "hsl(153, 60%, 25%)",
        },
        warning: {
          DEFAULT: "hsl(38, 95%, 50%)",
          light: "hsl(38, 95%, 95%)",
          dark: "hsl(38, 95%, 30%)",
        },
        danger: {
          DEFAULT: "hsl(0, 72%, 51%)",
          light: "hsl(0, 72%, 96%)",
          dark: "hsl(0, 72%, 30%)",
        },
        info: {
          DEFAULT: "hsl(221, 83%, 53%)",
          light: "hsl(221, 83%, 96%)",
          dark: "hsl(221, 83%, 30%)",
        },
      },

      // ─── Typography ──────────────────────────────────────────────────
      fontFamily: {
        sans: ["var(--font-geist-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-geist-mono)", "monospace"],
      },
      fontSize: {
        "2xs": ["0.625rem", { lineHeight: "1rem" }],   // 10px
        xs:    ["0.75rem",  { lineHeight: "1rem" }],    // 12px
        sm:    ["0.875rem", { lineHeight: "1.25rem" }], // 14px
        base:  ["1rem",     { lineHeight: "1.5rem" }],  // 16px
        lg:    ["1.125rem", { lineHeight: "1.75rem" }], // 18px
        xl:    ["1.25rem",  { lineHeight: "1.75rem" }], // 20px
        "2xl": ["1.5rem",   { lineHeight: "2rem" }],    // 24px
        "3xl": ["1.875rem", { lineHeight: "2.25rem" }], // 30px
        "4xl": ["2.25rem",  { lineHeight: "2.5rem" }],  // 36px
        "5xl": ["3rem",     { lineHeight: "1" }],       // 48px
      },

      // ─── Border radius ───────────────────────────────────────────────
      borderRadius: {
        sm:   "6px",
        DEFAULT: "8px",
        md:   "8px",
        lg:   "12px",
        xl:   "16px",
        "2xl": "24px",
        "3xl": "32px",
        full: "9999px",
      },

      // ─── Spacing (4px base) ──────────────────────────────────────────
      spacing: {
        0.5: "2px",
        1:   "4px",
        1.5: "6px",
        2:   "8px",
        2.5: "10px",
        3:   "12px",
        3.5: "14px",
        4:   "16px",
        5:   "20px",
        6:   "24px",
        7:   "28px",
        8:   "32px",
        9:   "36px",
        10:  "40px",
        11:  "44px",
        12:  "48px",
        14:  "56px",
        16:  "64px",
        20:  "80px",
        24:  "96px",
        28:  "112px",
        32:  "128px",
        36:  "144px",
        40:  "160px",
        44:  "176px",
        48:  "192px",
        52:  "208px",
        56:  "224px",
        60:  "240px",
        64:  "256px",
        72:  "288px",
        80:  "320px",
        96:  "384px",
      },

      // ─── Shadows ─────────────────────────────────────────────────────
      boxShadow: {
        sm:   "0 1px 2px rgba(0,0,0,0.05)",
        DEFAULT: "0 2px 4px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)",
        md:   "0 4px 8px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.04)",
        lg:   "0 8px 16px rgba(0,0,0,0.08), 0 4px 8px rgba(0,0,0,0.04)",
        xl:   "0 16px 32px rgba(0,0,0,0.10), 0 8px 16px rgba(0,0,0,0.04)",
        "2xl": "0 24px 48px rgba(0,0,0,0.12), 0 12px 24px rgba(0,0,0,0.05)",
        card:  "0 0 0 1px hsl(var(--border)), 0 2px 8px rgba(0,0,0,0.06)",
        "card-hover": "0 0 0 1px hsl(var(--border)), 0 8px 24px rgba(0,0,0,0.10)",
        brand: "0 4px 14px rgba(37, 99, 235, 0.3)",
        none:  "none",
      },

      // ─── Animations ──────────────────────────────────────────────────
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        "fade-in": {
          from: { opacity: "0", transform: "translateY(8px)" },
          to:   { opacity: "1", transform: "translateY(0)" },
        },
        "slide-in-right": {
          from: { opacity: "0", transform: "translateX(100%)" },
          to:   { opacity: "1", transform: "translateX(0)" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        "count-up": {
          from: { opacity: "0", transform: "translateY(12px)" },
          to:   { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up":   "accordion-up 0.2s ease-out",
        "fade-in":        "fade-in 0.3s ease-out",
        "slide-in-right": "slide-in-right 0.3s ease-out",
        "shimmer":        "shimmer 1.5s infinite linear",
        "count-up":       "count-up 0.4s ease-out",
      },

      // ─── Breakpoints ─────────────────────────────────────────────────
      screens: {
        xs:   "375px",
        sm:   "640px",
        md:   "768px",
        lg:   "1024px",
        xl:   "1280px",
        "2xl": "1536px",
      },

      // ─── Sidebar widths ──────────────────────────────────────────────
      width: {
        sidebar: "240px",
        "sidebar-collapsed": "64px",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
