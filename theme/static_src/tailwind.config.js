/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    '../../templates/**/*.html',
    '../../apps/**/*.py',
    '../../static/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: '#0B1E3D',
          mid: '#132952',
          dark: '#060F1E',
        },
        gold: {
          DEFAULT: '#C9A84C',
          muted: 'rgba(201,168,76,0.15)',
        },
        'brand-red': '#C0392B',
        'off-white': '#F4F6FA',
        'muted-blue': '#8A9BB5',
        'navy-text': '#7A9AC5',
        'body-text': '#5A6E8C',
        'border-light': '#D8E0EE',
        'footer-link': '#3A5070',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      maxWidth: {
        content: '1200px',
      },
    },
  },
  plugins: [],
}
