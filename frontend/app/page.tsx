"use client"

import Header from "@/components/header"
import LegalHero from "@/components/legal-hero"
import LegalQueryForm from "@/components/legal-query-form"
import LegalAreasGrid from "@/components/legal-areas-grid"
import ShaderBackground from "@/components/shader-background"
import AccessibilitySkipLinks from "@/components/accessibility-skip-links"

export default function LegalSystemHome() {
  return (
    <ShaderBackground>
      <AccessibilitySkipLinks />

      <Header />

      <main id="main-content" className="relative z-10" role="main">
        {/* Hero Section with Enhanced Container */}
        <div className="container mx-auto px-4 py-12">
          <LegalHero />
        </div>
        
        {/* Areas Grid with Full Width Background */}
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-white/5 to-transparent"></div>
          <div className="container mx-auto px-4 py-8 relative z-10">
            <LegalAreasGrid />
          </div>
        </div>

        {/* Call to Action Section */}
        <div className="container mx-auto px-4 py-16">
          <div className="text-center">
            <div className="relative inline-block group">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/30 via-green-500/30 to-purple-500/30 rounded-2xl blur-lg opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
              <div className="relative bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 shadow-2xl">
                <h3 className="text-2xl font-bold text-white mb-4">
                  ¿Listo para comenzar?
                </h3>
                <p className="text-white/90 mb-6 max-w-md mx-auto">
                  Inicia tu primera consulta legal y obtén respuestas precisas en segundos
                </p>
                <a
                  href="/chat"
                  className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 hover:from-blue-700 hover:via-blue-800 hover:to-blue-900 text-white px-8 py-3 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl group"
                >
                  <span>Comenzar Ahora</span>
                  <svg className="w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </div>
      </main>
    </ShaderBackground>
  )
}
