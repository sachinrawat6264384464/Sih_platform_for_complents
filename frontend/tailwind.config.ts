import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        nexus: {
          dark: {
            bg: "#0B1730",
            card: "#14233D",
            border: "#1E355B",
            hover: "#1A2E50",
            saffron: "#F28C28",
            saffronLight: "#FFA94D",
            cyan: "#00E5FF",
            emerald: "#10B981",
            crimson: "#EF4444",
          },
          light: {
            bg: "#F1F8FF",
            card: "#FFFFFF",
            border: "#D0E2FF",
            hover: "#E5F0FF",
            primary: "#1686CB",
            saffron: "#D97706",
            emerald: "#059669",
            crimson: "#DC2626",
          }
        }
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      keyframes: {
        floatCloud: {
          "0%": { transform: "translateX(-100%) translateY(0px)", opacity: "0.2" },
          "50%": { transform: "translateX(50vw) translateY(-15px)", opacity: "0.45" },
          "100%": { transform: "translateX(110vw) translateY(0px)", opacity: "0.2" },
        },
        pulseGlow: {
          "0%, 100%": { opacity: "0.4", transform: "scale(1)" },
          "50%": { opacity: "0.8", transform: "scale(1.05)" },
        }
      },
      animation: {
        "cloud-slow": "floatCloud 55s linear infinite",
        "cloud-medium": "floatCloud 40s linear infinite",
        "pulse-glow": "pulseGlow 3s ease-in-out infinite",
      }
    },
  },
  plugins: [],
};
export default config;

