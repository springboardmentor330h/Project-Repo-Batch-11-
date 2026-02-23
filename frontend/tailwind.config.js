/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#09090b",
                foreground: "#fafafa",
                primary: "#3b82f6",
                secondary: "#18181b",
                accent: "#a1a1aa",
            },
            backdropBlur: {
                xs: '2px',
            }
        },
    },
    plugins: [],
}
