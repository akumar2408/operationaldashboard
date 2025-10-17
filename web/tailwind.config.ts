import type { Config } from 'tailwindcss'
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      borderRadius: { '2xl': '1.25rem' },
      boxShadow: { 'soft': '0 10px 30px -12px rgba(0,0,0,0.45)' }
    }
  },
  plugins: []
} satisfies Config
