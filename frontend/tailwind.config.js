/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        panel: "#0f172a",
        card: "#111827",
        mint: "#6ee7b7",
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(148,163,184,0.2), 0 20px 40px rgba(2,6,23,0.5)",
      },
    },
  },
  plugins: [],
};
