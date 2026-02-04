/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    '../templates/**/*.html',
    '../../templates/**/*.html',
    '../../**/templates/**/*.html',
    '../../**/*.py',
  ],
  theme: {
    extend: {
      colors: {
        'jcm-blue': '#1e40af',
        'jcm-green': '#059669',
        'jcm-red': '#dc2626',
        'jcm-orange': '#ea580c',
        'jcm-gray': '#6b7280',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}