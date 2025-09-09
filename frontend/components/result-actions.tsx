"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { LegalQueryResponse } from "@/lib/api-types"

interface ResultActionsProps {
  result: any // Make it flexible to accept different response structures
  onNewQuery: () => void
}

export default function ResultActions({ result, onNewQuery }: ResultActionsProps) {
  const [copied, setCopied] = useState(false)

  const handleCopyResponse = async () => {
    try {
      await navigator.clipboard.writeText(result.response)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error("[v0] Failed to copy to clipboard:", error)
    }
  }

  const handleShareResult = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: "Consulta Legal - Sistema Multiagente",
          text: result.response.substring(0, 200) + "...",
          url: window.location.href,
        })
      } catch (error) {
        console.error("[v0] Failed to share:", error)
      }
    } else {
      // Fallback: copy URL to clipboard
      await navigator.clipboard.writeText(window.location.href)
      alert("Enlace copiado al portapapeles")
    }
  }

  const handleDownloadPDF = () => {
    // Create a simple text file for now (PDF generation would require additional libraries)
    const content = `
CONSULTA LEGAL - SISTEMA MULTIAGENTE
====================================

Área: ${result.area || "General"}
Confianza: ${result.confidence || 0}%
Fecha: ${new Date(result.metadata?.timestamp || Date.now()).toLocaleString("es-CO")}

RESPUESTA:
${result.response || "Sin respuesta"}

FUENTES CONSULTADAS:
${(result.sources || []).map((source: any, i: number) => `${i + 1}. ${source.title || source.id || "Fuente"} (${source.type || "N/A"})`).join("\n")}

PREGUNTAS RELACIONADAS:
${(result.relatedQuestions || result.suggestions || []).map((q: string, i: number) => `${i + 1}. ${q}`).join("\n")}
    `

    const blob = new Blob([content], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `consulta-legal-${result.id || Date.now()}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleEmailResult = () => {
    const subject = encodeURIComponent("Consulta Legal - Sistema Multiagente")
    const body = encodeURIComponent(
      `Consulta legal procesada:\n\nÁrea: ${result.area || "General"}\nConfianza: ${result.confidence || 0}%\n\nRespuesta:\n${(result.response || "").substring(0, 500)}...\n\nVer resultado completo: ${window.location.href}`,
    )
    window.open(`mailto:?subject=${subject}&body=${body}`)
  }

  return (
    <Card className="backdrop-blur-md bg-white/15 border border-white/30">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4"
            />
          </svg>
          Acciones
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Button
            onClick={handleCopyResponse}
            variant="outline"
            className="bg-white/10 border-white/30 text-white hover:bg-white/20 backdrop-blur-sm"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
              />
            </svg>
            {copied ? "¡Copiado!" : "Copiar"}
          </Button>

          <Button
            onClick={handleShareResult}
            variant="outline"
            className="bg-white/10 border-white/30 text-white hover:bg-white/20 backdrop-blur-sm"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z"
              />
            </svg>
            Compartir
          </Button>

          <Button
            onClick={handleDownloadPDF}
            variant="outline"
            className="bg-white/10 border-white/30 text-white hover:bg-white/20 backdrop-blur-sm"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            Descargar
          </Button>

          <Button
            onClick={handleEmailResult}
            variant="outline"
            className="bg-white/10 border-white/30 text-white hover:bg-white/20 backdrop-blur-sm"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
            Email
          </Button>
        </div>

        <div className="mt-6 pt-4 border-t border-white/20">
          <Button
            onClick={onNewQuery}
            className="w-full bg-blue-600/80 hover:bg-blue-600/90 backdrop-blur-sm border border-blue-500/30 text-white"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Nueva Consulta Legal
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
