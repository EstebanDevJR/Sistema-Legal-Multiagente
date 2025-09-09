"use client"

import { useState, useCallback } from "react"
import { apiClient } from "@/lib/api-client"
import type { LegalQueryRequest, LegalQueryResponse } from "@/lib/api-types"

export function useLegalQuery() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<LegalQueryResponse | null>(null)

  const submitQuery = useCallback(async (queryData: LegalQueryRequest) => {
    setIsLoading(true)
    setError(null)

    try {
      console.log("[v0] Submitting legal query:", queryData)
      const response = await apiClient.submitQuery(queryData)
      console.log("[v0] Query response received:", response)
      setResult(response)
      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Error al procesar la consulta"
      console.error("[v0] Query submission failed:", err)
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const getResult = useCallback(async (id: string) => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await apiClient.getQueryResult(id)
      setResult(response)
      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Error al obtener el resultado"
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const reset = useCallback(() => {
    setResult(null)
    setError(null)
    setIsLoading(false)
  }, [])

  return {
    submitQuery,
    getResult,
    reset,
    isLoading,
    error,
    result,
  }
}
