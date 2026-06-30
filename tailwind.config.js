/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        gray: {
          850: '#18202f',
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}

