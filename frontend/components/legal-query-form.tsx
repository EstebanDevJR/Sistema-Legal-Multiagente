"use client"

import { useState, useEffect, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import VoiceRecorder from "@/components/voice-recorder"
import AutoResizeTextarea from "@/components/auto-resize-textarea"
import SmartSuggestions from "@/components/smart-suggestions"
import { useLegalQuery } from "@/hooks/use-legal-query"
import { useVoiceQuery } from "@/hooks/use-voice-query"
import { useToast } from "@/components/toast-provider"
import { useDocuments } from "@/contexts/DocumentContext"
import { useRouter, useSearchParams } from "next/navigation"
import { Badge } from "@/components/ui/badge"
import ResponseDisplay from "@/components/response-display"
import LegalSources from "@/components/legal-sources"
import RelatedQuestions from "@/components/related-questions"
import ResultActions from "@/components/result-actions"

export default function LegalQueryForm() {
  const [activeTab, setActiveTab] = useState("text")
  const [query, setQuery] = useState("")
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const [currentResult, setCurrentResult] = useState<any>(null)
  const router = useRouter()
  const searchParams = useSearchParams()
  const legalQuery = useLegalQuery()
  const voiceQuery = useVoiceQuery()
  const { addToast } = useToast()
  const { uploadedDocumentIds } = useDocuments()

  useEffect(() => {
    const urlQuery = searchParams.get("q")
    if (urlQuery) {
      setQuery(decodeURIComponent(urlQuery))
      setActiveTab("text")
    }
  }, [searchParams])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+Enter to submit
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault()
        if (query.trim() && !legalQuery.isLoading) {
          handleSubmitQuery()
        }
      }

      // Escape to hide suggestions
      if (e.key === "Escape") {
        setShowSuggestions(false)
      }
    }

    document.addEventListener("keydown", handleKeyDown)
    return () => document.removeEventListener("keydown", handleKeyDown)
  }, [query, legalQuery.isLoading])

  const handleSubmitQuery = async () => {
    if (!query.trim()) {
      addToast({
        type: "warning",
        title: "Consulta vacía",
        description: "Por favor escribe tu consulta legal antes de enviar.",
      })
      return
    }

    try {
      addToast({
        type: "info",
        title: "Procesando consulta",
        description: "Analizando tu consulta con IA especializada en derecho colombiano...",
      })

      console.log("🔍 Sending query with document IDs:", uploadedDocumentIds)
      const response = await legalQuery.submitQuery({
        query: query.trim(),
        method: "text",
        documentIds: uploadedDocumentIds.length > 0 ? uploadedDocumentIds : undefined,
      })

      console.log("[v0] Response received:", response)
      console.log("[v0] Response type:", typeof response)
      console.log("[v0] Response keys:", Object.keys(response))

      addToast({
        type: "success",
        title: "Consulta procesada",
        description: "Tu consulta ha sido analizada exitosamente.",
      })

      // Set result and show results instead of redirecting
      setCurrentResult(response)
      setShowResults(true)
    } catch (error) {
      console.error("[v0] Query submission failed:", error)
      addToast({
        type: "error",
        title: "Error al procesar consulta",
        description: "Hubo un problema al procesar tu consulta. Inténtalo nuevamente.",
      })
    }
  }

  const handleVoiceQuerySubmit = async (audioBlob: Blob) => {
    try {
      addToast({
        type: "info",
        title: "Procesando audio",
        description: "Transcribiendo y analizando tu consulta de voz...",
      })

      // Use the voice query hook to send audio directly to /voice/voice-query endpoint
      const response = await voiceQuery.submitVoiceQuery(audioBlob)

      addToast({
        type: "success",
        title: "Consulta de voz procesada",
        description: "Tu consulta de voz ha sido analizada exitosamente.",
      })

      // Set result and show results instead of redirecting
      setCurrentResult(response)
      setShowResults(true)
    } catch (error) {
      console.error("[v0] Voice query submission failed:", error)
      addToast({
        type: "error",
        title: "Error en consulta de voz",
        description: "No se pudo procesar tu consulta de voz. Inténtalo nuevamente.",
      })
    }
  }

  const handleVoiceTranscription = (transcription: string) => {
    setQuery(transcription)
    setActiveTab("text") // Switch to text tab to show transcription
    addToast({
      type: "success",
      title: "Audio transcrito",
      description: "Tu audio ha sido convertido a texto exitosamente.",
    })
  }

  const handleSuggestionSelect = useCallback(
    (suggestion: string) => {
      setQuery(suggestion)
      setShowSuggestions(false)
      addToast({
        type: "info",
        title: "Sugerencia aplicada",
        description: "La consulta sugerida ha sido cargada.",
      })
    },
    [addToast],
  )

  const handleNewQuery = () => {
    setShowResults(false)
    setCurrentResult(null)
    setQuery("")
  }

  const handleRelatedQuestionSelect = (question: string) => {
    setQuery(question)
    setShowResults(false)
    setCurrentResult(null)
    addToast({
      type: "info",
      title: "Pregunta relacionada seleccionada",
      description: "La pregunta relacionada ha sido cargada para una nueva consulta.",
    })
  }

  // If showing results, render the results page
  if (showResults && currentResult) {
    console.log("[v0] Rendering results with:", currentResult)
    console.log("[v0] Result type:", typeof currentResult)
    console.log("[v0] Result keys:", Object.keys(currentResult))
    
    // Validate that we have the required fields
    if (!currentResult.response) {
      console.error("[v0] Missing response field:", currentResult)
      return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 relative">
          <div className="relative z-10 container mx-auto px-4 py-8">
            <div className="max-w-4xl mx-auto">
              <Card className="backdrop-blur-md bg-red-500/20 border border-red-400/30">
                <CardContent className="p-12 text-center">
                  <h2 className="text-xl font-semibold text-white mb-2">Error en la respuesta</h2>
                  <p className="text-red-200 mb-4">La respuesta del servidor no tiene el formato esperado</p>
                  <p className="text-red-200 mb-4 text-sm">Campos disponibles: {Object.keys(currentResult).join(", ")}</p>
                  <Button onClick={handleNewQuery} className="bg-blue-600/80 hover:bg-blue-600/90">
                    Nueva Consulta
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      )
    }

    // Start with a simple version to debug
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 relative">
        <div className="relative z-10 container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto space-y-6">
            {/* Simple header */}
            <div className="bg-white/15 backdrop-blur-md border border-white/30 rounded-lg p-6">
              <h2 className="text-2xl text-white mb-4">Respuesta Legal</h2>
              <div className="text-white mb-4">
                <strong>Área:</strong> {currentResult.area || "General"} | 
                <strong> Confianza:</strong> {currentResult.confidence || 0}%
              </div>
            </div>

            {/* Simple response */}
            <div className="bg-white/15 backdrop-blur-md border border-white/30 rounded-lg p-6">
              <h3 className="text-xl text-white mb-4">Respuesta:</h3>
              <div className="text-white/90 whitespace-pre-wrap">{currentResult.response}</div>
            </div>

            {/* Back button */}
            <div className="text-center">
              <Button
                onClick={handleNewQuery}
                variant="outline"
                className="bg-white/10 border-white/30 text-white hover:bg-white/20 backdrop-blur-sm"
              >
                ← Nueva Consulta
              </Button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const getCharacterCountColor = () => {
    const length = query.length
    if (length > 1800) return "text-red-400"
    if (length > 1500) return "text-yellow-400"
    return "text-white/70"
  }

  return (
    <section className="py-12">
      <Card className="max-w-4xl mx-auto shadow-2xl backdrop-blur-md bg-white/20 border border-white/30">
        <CardHeader>
          <CardTitle className="text-2xl text-center text-white">¿En qué podemos ayudarte hoy?</CardTitle>
          {uploadedDocumentIds.length > 0 && (
            <div className="mt-4 text-center">
              <Badge variant="secondary" className="bg-green-500/20 text-green-200 border-green-400/30">
                📄 {uploadedDocumentIds.length} documento(s) cargado(s) - Las consultas usarán estos documentos
              </Badge>
            </div>
          )}
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <div className="w-full px-2 mb-6">
              <TabsList
                className="grid w-full grid-cols-3 bg-white/15 backdrop-blur-sm border-white/30 rounded-lg p-2 max-w-full border h-16"
                role="tablist"
              >
                <TabsTrigger
                  value="text"
                  className="flex items-center justify-center space-x-2 data-[state=active]:bg-white/25 data-[state=active]:text-white text-white/80 rounded-md px-4 py-3 text-base font-medium transition-all min-w-0"
                  role="tab"
                  aria-label="Consulta por texto"
                >
                  <svg
                    className="w-5 h-5 flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    />
                  </svg>
                  <span className="hidden sm:inline truncate">Texto</span>
                </TabsTrigger>
                <TabsTrigger
                  value="voice"
                  className="flex items-center justify-center space-x-2 data-[state=active]:bg-white/25 data-[state=active]:text-white rounded-md px-4 py-3 text-base font-medium transition-all min-w-0 text-white"
                  role="tab"
                  aria-label="Consulta por voz"
                >
                  <svg
                    className="w-5 h-5 flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 016 0v6a3 3 0 01-3 3z"
                    />
                  </svg>
                  <span className="hidden sm:inline truncate">Voz</span>
                </TabsTrigger>
                <TabsTrigger
                  value="document"
                  className="flex items-center justify-center space-x-2 data-[state=active]:bg-white/25 data-[state=active]:text-white text-white/80 rounded-md px-4 py-3 text-base font-medium transition-all min-w-0"
                  role="tab"
                  aria-label="Consulta por documento"
                >
                  <svg
                    className="w-5 h-5 flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path className="text-white"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  <span className="hidden sm:inline truncate text-white">Documento</span>
                </TabsTrigger>
              </TabsList>
            </div>

            <TabsContent value="text" className="space-y-4" role="tabpanel">
              <div className="space-y-2">
                <AutoResizeTextarea
                  id="legal-query-input"
                  name="legal-query"
                  placeholder="Escribe tu consulta legal aquí... Por ejemplo: '¿Cuáles son los requisitos para constituir una SAS en Colombia?'"
                  value={query}
                  onChange={(e) => {
                    setQuery(e.target.value)
                    setShowSuggestions(e.target.value.length > 2)
                  }}
                  className="text-base bg-white/15 backdrop-blur-sm border-white/30 text-white placeholder:text-white/90 focus:bg-white/20 focus:border-white/40"
                  minRows={3}
                  maxRows={8}
                  aria-label="Campo de consulta legal"
                  aria-describedby="character-count query-help"
                />

                <div className="flex justify-between items-center text-sm text-white">
                  <span id="character-count" className={getCharacterCountColor()}>
                    {query.length}/2000 caracteres
                  </span>
                  <span id="query-help" className="text-white">
                    Presiona Ctrl+Enter para enviar
                  </span>
                </div>
              </div>

              {showSuggestions && (
                <SmartSuggestions
                  query={query}
                  onSuggestionSelect={handleSuggestionSelect}
                  className="animate-in slide-in-from-top-2 duration-200"
                />
              )}

              <Button
                onClick={handleSubmitQuery}
                disabled={!query.trim() || legalQuery.isLoading}
                className="w-full py-3 text-base bg-blue-600/80 hover:bg-blue-600/90 backdrop-blur-sm border border-blue-500/30 text-white disabled:opacity-50 transition-all"
                aria-label="Enviar consulta legal"
              >
                {legalQuery.isLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-black rounded-full animate-spin" />
                    <span>Procesando...</span>
                  </div>
                ) : (
                  "Enviar Consulta"
                )}
              </Button>
            </TabsContent>

            <TabsContent value="voice" className="space-y-6" role="tabpanel">
              <VoiceRecorder onTranscription={handleVoiceTranscription} onQuerySubmit={handleVoiceQuerySubmit} />
            </TabsContent>

            <TabsContent value="document" className="space-y-4" role="tabpanel">
              <div className="border-2 border-dashed border-white/30 rounded-lg p-8 text-center hover:border-blue-400/50 transition-colors bg-white/10 backdrop-blur-sm">
                <svg
                  className="w-12 h-12 text-white/70 mx-auto mb-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
                <p className="text-lg font-medium text-white mb-2">
                  Arrastra documentos aquí o haz clic para seleccionar
                </p>
                <p className="text-sm text-white/80 mb-4">Soportamos PDF, DOC, DOCX hasta 10MB</p>
                <Button
                  variant="outline"
                  className="bg-white/15 border-white/30 text-white hover:bg-white/25 backdrop-blur-sm"
                  aria-label="Seleccionar archivos para consulta"
                >
                  Seleccionar Archivos
                </Button>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </section>
  )
}
