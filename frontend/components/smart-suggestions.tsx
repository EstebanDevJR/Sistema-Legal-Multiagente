"use client"

import { useState, useEffect, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { useQuerySuggestions } from "@/hooks/use-query-suggestions"

interface SmartSuggestionsProps {
  query: string
  onSuggestionSelect: (suggestion: string) => void
  className?: string
}

export default function SmartSuggestions({ query, onSuggestionSelect, className }: SmartSuggestionsProps) {
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [filteredSuggestions, setFilteredSuggestions] = useState<string[]>([])
  const { suggestions, examples } = useQuerySuggestions()

  // Ensure suggestions and examples are arrays
  const safeSuggestions = Array.isArray(suggestions) ? suggestions : []
  const safeExamples = Array.isArray(examples) ? examples : []

  // Smart suggestion filtering based on query content
  const getSmartSuggestions = useCallback(
    (inputQuery: string) => {
      if (!inputQuery.trim()) return safeExamples.slice(0, 3).map((ex) => ex.text)

      const queryLower = inputQuery.toLowerCase()
      const allSuggestions = [...safeSuggestions.map((s) => s.text), ...safeExamples.map((e) => e.text)]

      // Filter suggestions based on keywords
      const filtered = allSuggestions.filter((suggestion) => {
        const suggestionLower = suggestion.toLowerCase()

        // Check for keyword matches
        const keywords = queryLower.split(" ").filter((word) => word.length > 2)
        return keywords.some((keyword) => suggestionLower.includes(keyword))
      })

      // If no keyword matches, show contextual suggestions based on legal areas
      if (filtered.length === 0) {
        const legalAreas = {
          contrato: [
            "¿Cómo redactar un contrato de trabajo?",
            "¿Qué cláusulas debe tener un contrato de arrendamiento?",
          ],
          empresa: [
            "¿Cómo constituir una SAS en Colombia?",
            "¿Cuáles son las obligaciones tributarias de una empresa?",
          ],
          laboral: ["¿Cuáles son mis derechos como trabajador?", "¿Cómo calcular la liquidación laboral?"],
          civil: ["¿Cómo hacer un testamento válido?", "¿Qué es la sucesión intestada?"],
          penal: ["¿Cuáles son los delitos contra el patrimonio?", "¿Qué es la legítima defensa?"],
          familia: ["¿Cómo solicitar divorcio en Colombia?", "¿Cuáles son los derechos de custodia?"],
        }

        for (const [area, areaSuggestions] of Object.entries(legalAreas)) {
          if (queryLower.includes(area)) {
            return areaSuggestions
          }
        }
      }

      return filtered.slice(0, 5)
    },
    [safeSuggestions, safeExamples],
  )

  useEffect(() => {
    const suggestions = getSmartSuggestions(query)
    setFilteredSuggestions(suggestions)
    setShowSuggestions(query.length > 0 && suggestions.length > 0)
  }, [query, getSmartSuggestions])

  if (!showSuggestions || filteredSuggestions.length === 0) {
    return null
  }

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center gap-2 text-sm text-gray-300">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
          />
        </svg>
        <span>Sugerencias inteligentes:</span>
      </div>
      <div className="space-y-2">
        {Array.isArray(filteredSuggestions) && filteredSuggestions.map((suggestion, index) => (
          <Button
            key={index}
            variant="outline"
            onClick={() => onSuggestionSelect(suggestion)}
            className="w-full text-left justify-start h-auto p-3 bg-white/5 border-white/20 text-gray-300 hover:bg-white/10 hover:text-white transition-all text-sm"
          >
            <svg className="w-3 h-3 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span className="leading-relaxed">{suggestion}</span>
          </Button>
        ))}
      </div>
    </div>
  )
}
