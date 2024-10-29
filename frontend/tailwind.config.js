/** @type {import('tailwindcss').Config} */
module.exports = { 
  content: [
    "./src/**/*.{html,js,ts,jsx,tsx}",
    "./index.html"
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#007bff',
        'secondary': '#6c757d',
        'success': '#28a745',
        'info': '#17a2b8',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'light': '#f8f9fa',
        'dark': '#343a40',
        'white': '#fff',
        'black': '#000',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
};
