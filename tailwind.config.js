/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        base: "#0b0e14",
        panel: "#141922",
        panel2: "#1b212d",
        edge: "#232b39",
        brand: "#7c5cff",
        live: "#ff4655",
        accent: "#00c2a8",
      },
      fontFamily: {
        sans: ["var(--font-app)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
