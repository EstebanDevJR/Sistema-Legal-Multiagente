"use client"

import { useEffect, useState } from "react"

export default function LegalHero() {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    setIsVisible(true)
  }, [])

  return (
    <section className="text-center py-20 px-4 relative">
      <div className="max-w-5xl mx-auto">
        {/* Animated Title */}
        <div className={`transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <h1 className="text-6xl md:text-7xl font-bold text-white mb-6 leading-tight">
            <span className="relative inline-block">
              <span className="relative z-10 bg-gradient-to-r from-white via-white to-white/90 bg-clip-text text-transparent">
                Sistema Legal
              </span>
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-green-500/20 blur-lg opacity-50"></div>
            </span>
            <br />
            <span className="relative inline-block mt-2">
              <span className="relative z-10 bg-gradient-to-r from-blue-300 via-green-300 to-cyan-300 bg-clip-text text-transparent">
                Multiagente
              </span>
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/30 to-green-500/30 blur-lg opacity-60"></div>
            </span>
          </h1>
        </div>

        {/* Animated Subtitle */}
        <div className={`transition-all duration-1000 delay-300 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <p className="text-xl md:text-2xl mb-12 leading-relaxed max-w-3xl mx-auto text-white/90 font-medium">
            Obtén respuestas precisas sobre derecho colombiano con inteligencia artificial especializada. 
            <span className="block mt-2 text-lg text-white/80">
              Consulta por texto, voz o documentos de manera rápida y confiable.
            </span>
          </p>
        </div>

        {/* Enhanced Features Grid */}
        <div className={`transition-all duration-1000 delay-500 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6 max-w-4xl mx-auto">
            {[
              { icon: "⚖️", text: "Derecho Civil", delay: "delay-700" },
              { icon: "🏢", text: "Derecho Comercial", delay: "delay-800" },
              { icon: "👥", text: "Derecho Laboral", delay: "delay-900" },
              { icon: "💰", text: "Derecho Tributario", delay: "delay-1000" }
            ].map((item, index) => (
              <div 
                key={index}
                className={`group transition-all duration-700 ${item.delay} ${isVisible ? 'opacity-100 scale-100' : 'opacity-0 scale-95'}`}
              >
                <div className="relative bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-4 hover:bg-white/15 hover:border-white/30 transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-xl">
                  <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <div className="relative">
                    <div className="text-3xl mb-2 group-hover:scale-110 transition-transform duration-300">
                      {item.icon}
                    </div>
                    <div className="flex items-center justify-center gap-2">
                      <svg className="w-4 h-4 text-green-400 opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-sm font-medium text-white group-hover:text-white transition-colors">
                        {item.text}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Floating Elements */}
        <div className="absolute top-10 left-10 w-20 h-20 bg-blue-500/10 rounded-full blur-xl animate-pulse"></div>
        <div className="absolute top-20 right-16 w-16 h-16 bg-green-500/10 rounded-full blur-xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        <div className="absolute bottom-10 left-20 w-12 h-12 bg-purple-500/10 rounded-full blur-xl animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>
    </section>
  )
}
