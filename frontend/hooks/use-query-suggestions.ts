"use client"

import { useState, useEffect, useCallback } from "react"
import { apiClient } from "@/lib/api-client"
import type { QuerySuggestion } from "@/lib/api-types"

export function useQuerySuggestions(area?: string) {
  const [suggestions, setSuggestions] = useState<QuerySuggestion[]>([])
  const [examples, setExamples] = useState<QuerySuggestion[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadSuggestions = useCallback(async (selectedArea?: string) => {
    setIsLoading(true)
    setError(null)

    try {
      const [suggestionsData, examplesData] = await Promise.all([
        apiClient.getQuerySuggestions(selectedArea),
        apiClient.getExampleQueries(selectedArea),
      ])

      // Ensure we always have arrays
      setSuggestions(Array.isArray(suggestionsData) ? suggestionsData : [])
      setExamples(Array.isArray(examplesData) ? examplesData : [])
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Error al cargar sugerencias"
      setError(errorMessage)
      console.error("[v0] Failed to load suggestions:", err)
      
      // Set empty arrays on error to prevent crashes
      setSuggestions([])
      setExamples([])
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadSuggestions(area)
  }, [area, loadSuggestions])

  return {
    suggestions,
    examples,
    isLoading,
    error,
    reload: () => loadSuggestions(area),
  }
}
