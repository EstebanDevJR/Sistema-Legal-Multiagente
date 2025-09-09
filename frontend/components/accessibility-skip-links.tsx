"use client"

export default function AccessibilitySkipLinks() {
  return (
    <div className="sr-only focus-within:not-sr-only">
      <a
        href="#main-content"
        className="fixed top-4 left-4 z-50 bg-blue-600 text-white px-4 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
      >
        Saltar al contenido principal
      </a>
      <a
        href="#navigation"
        className="fixed top-4 left-32 z-50 bg-blue-600 text-white px-4 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
      >
        Saltar a navegación
      </a>
    </div>
  )
}
