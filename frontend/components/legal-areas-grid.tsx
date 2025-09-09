"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useState, useEffect } from "react"

const legalAreas = [
  {
    id: "civil",
    title: "Derecho Civil",
    description: "Contratos, propiedad, familia, sucesiones",
    icon: "👥",
    examples: [
      "¿Cómo redactar un contrato de arrendamiento?",
      "Requisitos para el matrimonio civil",
      "Proceso de sucesión intestada",
    ],
    color: "from-blue-500 to-blue-600",
  },
  {
    id: "comercial",
    title: "Derecho Comercial",
    description: "Sociedades, comercio, títulos valores",
    icon: "🏢",
    examples: ["Constitución de una SAS", "Registro mercantil obligatorio", "Liquidación de sociedades"],
    color: "from-green-500 to-green-600",
  },
  {
    id: "laboral",
    title: "Derecho Laboral",
    description: "Contratos, prestaciones, despidos",
    icon: "⚖️",
    examples: ["Cálculo de liquidación laboral", "Tipos de contrato de trabajo", "Derechos en licencia de maternidad"],
    color: "from-purple-500 to-purple-600",
  },
  {
    id: "tributario",
    title: "Derecho Tributario",
    description: "Impuestos, declaraciones, sanciones",
    icon: "💰",
    examples: [
      "Declaración de renta personas naturales",
      "IVA en servicios digitales",
      "Régimen simple de tributación",
    ],
    color: "from-orange-500 to-orange-600",
  },
]

export default function LegalAreasGrid() {
  const [isVisible, setIsVisible] = useState(false)
  const [hoveredCard, setHoveredCard] = useState<string | null>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
        }
      },
      { threshold: 0.1 }
    )

    const element = document.getElementById('legal-areas-section')
    if (element) observer.observe(element)

    return () => observer.disconnect()
  }, [])

  return (
    <section id="legal-areas-section" className="py-20">
      {/* Enhanced Header */}
      <div className={`text-center mb-16 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
        <div className="relative inline-block mb-6">
          <h2 className="text-4xl md:text-5xl font-bold text-transparent bg-gradient-to-r from-white via-white/90 to-white/80 bg-clip-text">
            Áreas Legales Especializadas
          </h2>
          <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-24 h-1 bg-gradient-to-r from-blue-500 to-green-500 rounded-full"></div>
        </div>
        <p className="text-xl max-w-3xl mx-auto text-white/90 font-medium">
          Nuestro sistema está especializado en las principales áreas del derecho colombiano,
          <span className="block mt-2 text-lg text-white/70">
            brindando respuestas precisas y actualizadas para cada especialidad.
          </span>
        </p>
      </div>

      {/* Enhanced Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        {legalAreas.map((area, index) => (
          <div
            key={area.id}
            className={`transition-all duration-700 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-12'}`}
            style={{ transitionDelay: `${index * 200}ms` }}
            onMouseEnter={() => setHoveredCard(area.id)}
            onMouseLeave={() => setHoveredCard(null)}
          >
            <Card className="group relative overflow-hidden cursor-pointer backdrop-blur-md bg-white/10 border border-white/20 hover:bg-white/20 hover:border-white/40 text-white transition-all duration-500 hover:scale-105 hover:shadow-2xl hover:shadow-white/10 h-full">
              {/* Animated Background */}
              <div className={`absolute inset-0 bg-gradient-to-br ${area.color} opacity-0 group-hover:opacity-10 transition-all duration-500`}></div>
              
              {/* Floating Particles */}
              {hoveredCard === area.id && (
                <>
                  <div className="absolute top-4 right-4 w-2 h-2 bg-white/40 rounded-full animate-ping"></div>
                  <div className="absolute bottom-6 left-6 w-1 h-1 bg-white/30 rounded-full animate-pulse" style={{ animationDelay: '0.5s' }}></div>
                </>
              )}

              <CardHeader className="text-center relative z-10 pb-4">
                <div className="relative mb-6">
                  <div
                    className={`w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br ${area.color} flex items-center justify-center text-3xl mb-4 group-hover:scale-110 group-hover:rotate-6 transition-all duration-500 shadow-lg group-hover:shadow-xl`}
                  >
                    {area.icon}
                  </div>
                  {/* Glow Effect */}
                  <div className={`absolute inset-0 w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br ${area.color} opacity-0 group-hover:opacity-30 blur-lg transition-all duration-500`}></div>
                </div>
                <CardTitle className="text-xl font-bold text-white mb-2 group-hover:text-white transition-colors">
                  {area.title}
                </CardTitle>
                <p className="text-sm text-white/80 font-medium">{area.description}</p>
              </CardHeader>

              <CardContent className="relative z-10">
                <div className="space-y-3">
                  <p className="text-sm font-semibold mb-4 text-white/90 flex items-center gap-2">
                    <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Consultas frecuentes:
                  </p>
                  {area.examples.map((example, exampleIndex) => (
                    <div
                      key={exampleIndex}
                      className={`text-xs bg-white/10 backdrop-blur-sm rounded-xl p-3 hover:bg-white/20 transition-all duration-300 border border-white/20 hover:border-white/30 text-white/90 hover:text-white group-hover:translate-x-1 ${hoveredCard === area.id ? 'animate-fadeIn' : ''}`}
                      style={{ 
                        animationDelay: hoveredCard === area.id ? `${exampleIndex * 100}ms` : '0ms'
                      }}
                    >
                      <div className="flex items-start gap-2">
                        <div className="w-1 h-1 bg-green-400 rounded-full mt-2 flex-shrink-0"></div>
                        <span className="leading-relaxed">{example}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        ))}
      </div>
    </section>
  )
}
