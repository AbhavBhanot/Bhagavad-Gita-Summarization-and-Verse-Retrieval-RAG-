/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        spiritual: {
          50: '#fdf7f0',
          100: '#faeee1',
          200: '#f4d6b7',
          300: '#edb788',
          400: '#e59556',
          500: '#de7c2d',
          600: '#cf6823',
          700: '#ac541f',
          800: '#894420',
          900: '#6f3a1d',
          950: '#3c1d0e',
        },
        saffron: {
          50: '#fff9ed',
          100: '#fef2d6',
          200: '#fce1ac',
          300: '#f9ca77',
          400: '#f5a940',
          500: '#f2911a',
          600: '#e37510',
          700: '#bc5a0f',
          800: '#964614',
          900: '#7a3b14',
          950: '#421c08',
        }
      },
      fontFamily: {
        'sanskrit': ['Noto Sans Devanagari', 'serif'],
        'elegant': ['Playfair Display', 'serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-soft': 'pulseSoft 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        }
      }
    },
  },
  plugins: [],
}

