/** @type {import('tailwindcss').Config} */
const colors = require('tailwindcss/colors')
module.exports = {
    darkMode: ['class'],
    content: [
        './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
        './src/components/**/*.{js,ts,jsx,tsx,mdx}',
        './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        container: {
            center: true,
            padding: '2rem',
            screens: {
                '2xl': '1400px',
            },
        },
        extend: {
            keyframes: {
                'accordion-down': {
                    from: { height: 0 },
                    to: { height: 'var(--radix-accordion-content-height)' },
                },
                'accordion-up': {
                    from: { height: 'var(--radix-accordion-content-height)' },
                    to: { height: 0 },
                },
            },
            animation: {
                'accordion-down': 'accordion-down 0.2s ease-out',
                'accordion-up': 'accordion-up 0.2s ease-out',
            },
        colors: {
                'action-move': {
                  ...colors.lime, 
                  DEFAULT: colors.lime[500]
                },
                'action-move-hover' : colors.lime[600],

                'action-tool': {
                  ...colors.amber,
                  DEFAULT: colors.amber[500]
                },
                'action-tool-hover' : colors.amber[600],
                'action-sleep': {
                  ...colors.indigo,
                  DEFAULT: colors.indigo[700]
                },
                'action-sleep-hover' : colors.indigo[800],
                'action-custom': {
                  ...colors.red,
                  DEFAULT: colors.red[500]
                },
                'action-custom-hover' : colors.red[600],
              },
        },
    },
    plugins: [require('tailwindcss-animate')],
};
