/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './index.html',
        './src/**/*.{ts,tsx,js,jsx}',
    ],
    theme: {
        extend: {
            colors: {
                '0g': {
                    purple: '#6B46C1',
                    cyan: '#00D9FF',
                    dark: '#0A0A0A',
                    surface: '#1A1A2E',
                },
            },
        },
    },
    plugins: [],
}
