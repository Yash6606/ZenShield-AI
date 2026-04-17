export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#0a0c10",
                surface: "#11141b",
                primary: "#3b82f6",
                secondary: "#8b5cf6",
                danger: "#ef4444",
                warning: "#f59e0b",
                success: "#10b981",
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                display: ['Outfit', 'sans-serif'],
            },
            animation: {
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            }
        },
    },
    plugins: [],
}
