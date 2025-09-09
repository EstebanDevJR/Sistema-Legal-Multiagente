"use client"

import { useState, useCallback } from "react"
import { apiClient } from "@/lib/api-client"
import type { LegalQueryResponse } from "@/lib/api-types"

export function useVoiceQuery() {
  const [isProcessing, setIsProcessing] = useState(false)
  const [transcription, setTranscription] = useState<string>("")
  const [error, setError] = useState<string | null>(null)

  const transcribeAudio = useCallback(async (audioBlob: Blob): Promise<string> => {
    setIsProcessing(true)
    setError(null)

    try {
      console.log("[v0] Transcribing audio blob:", audioBlob.size, "bytes")
      const response = await apiClient.speechToText(audioBlob)
      console.log("[v0] Transcription received:", response.transcription)

      setTranscription(response.transcription)
      return response.transcription
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Error al transcribir el audio"
      console.error("[v0] Transcription failed:", err)
      setError(errorMessage)
      throw err
    } finally {
      setIsProcessing(false)
    }
  }, [])

  const submitVoiceQuery = useCallback(async (audioBlob: Blob, responseMode: string = "text", documentIds?: string[]): Promise<LegalQueryResponse> => {
    setIsProcessing(true)
    setError(null)

    try {
      console.log("[v0] useVoiceQuery.submitVoiceQuery called with:")
      console.log("  - audioBlob.size:", audioBlob.size, "bytes")
      console.log("  - audioBlob.type:", audioBlob.type)
      console.log("  - audioBlob constructor:", audioBlob.constructor.name)
      console.log("  - responseMode:", responseMode)
      
      const response = await apiClient.submitVoiceQuery(audioBlob, undefined, responseMode, documentIds)
      console.log("[v0] Voice query response:", response)
      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Error al procesar la consulta de voz"
      console.error("[v0] Voice query failed:", err)
      setError(errorMessage)
      throw err
    } finally {
      setIsProcessing(false)
    }
  }, [])

  const generateSpeech = useCallback(async (text: string): Promise<string> => {
    try {
      console.log("[v0] Generating speech for text:", text.substring(0, 50) + "...")
      const response = await apiClient.textToSpeech(text)
      return response.audioUrl
    } catch (err) {
      console.error("[v0] Speech generation failed:", err)
      throw err
    }
  }, [])

  const reset = useCallback(() => {
    setTranscription("")
    setError(null)
    setIsProcessing(false)
  }, [])

  return {
    transcribeAudio,
    submitVoiceQuery,
    generateSpeech,
    reset,
    isProcessing,
    transcription,
    error,
  }
}
