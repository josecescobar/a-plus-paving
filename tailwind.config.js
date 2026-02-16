/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./*.html", "./blog/*.html"],
  theme: {
    extend: {
      colors: {
        'custom-green': '#5BA83A',
      },
    },
  },
  plugins: [],
}

