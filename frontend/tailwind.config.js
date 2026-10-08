/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#0F1B33",
          900: "#16233F",
          800: "#1E2E4F",
          700: "#2A3F63",
          600: "#3B5480",
        },
        parchment: {
          50: "#FAF9F6",
          100: "#F3F1EA",
        },
        gold: {
          500: "#C9A227",
          600: "#AD8A1E",
        },
        slate: {
          500: "#725d5b",
          600: "#454E5C",
        },
      },
      fontFamily: {
        serif: ["'Source Serif 4'", "Georgia", "serif"],
        sans: ["'Inter'", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
