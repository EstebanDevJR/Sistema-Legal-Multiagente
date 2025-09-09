"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import type { LegalSource } from "@/lib/api-types"

interface LegalSourcesProps {
  sources: LegalSource[]
}

export default function LegalSources({ sources }: LegalSourcesProps) {
  const [expandedSource, setExpandedSource] = useState<string | null>(null)

  const getSourceTypeColor = (type: string) => {
    switch (type) {
      case "ley":
        return "bg-blue-500/20 text-blue-300 border-blue-400/30"
      case "decreto":
        return "bg-green-500/20 text-green-300 border-green-400/30"
      case "jurisprudencia":
        return "bg-purple-500/20 text-purple-300 border-purple-400/30"
      case "doctrina":
        return "bg-orange-500/20 text-orange-300 border-orange-400/30"
      default:
        return "bg-gray-500/20 text-gray-300 border-gray-400/30"
    }
  }

  const getSourceTypeText = (type: string) => {
    switch (type) {
      case "ley":
        return "Ley"
      case "decreto":
        return "Decreto"
      case "jurisprudencia":
        return "Jurisprudencia"
      case "doctrina":
        return "Doctrina"
      default:
        return type
    }
  }

  const getRelevanceColor = (relevance: number) => {
    if (relevance >= 80) return "text-green-400"
    if (relevance >= 60) return "text-yellow-400"
    return "text-red-400"
  }

  const sortedSources = [...sources].sort((a, b) => b.relevance - a.relevance)

  return (
    <Card className="backdrop-blur-md bg-white/15 border border-white/30">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
            />
          </svg>
          Fuentes Normativas ({sources.length})
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {sortedSources.map((source) => (
          <div
            key={source.id}
            className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20 hover:bg-white/15 transition-all"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-white mb-2 leading-tight">{source.title}</h4>
                <div className="flex flex-wrap gap-2 mb-2">
                  <Badge className={getSourceTypeColor(source.type)}>{getSourceTypeText(source.type)}</Badge>
                  {source.article && (
                    <Badge variant="outline" className="bg-white/10 border-white/30 text-gray-300">
                      Art. {source.article}
                    </Badge>
                  )}
                </div>
              </div>
              <div className="text-right ml-4">
                <div className={`text-sm font-medium ${getRelevanceColor(source.relevance)}`}>
                  {source.relevance}% relevante
                </div>
              </div>
            </div>

            <p className="text-gray-300 text-sm leading-relaxed mb-3">
              {expandedSource === source.id ? source.excerpt : `${source.excerpt.substring(0, 200)}...`}
            </p>

            <div className="flex items-center justify-between">
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setExpandedSource(expandedSource === source.id ? null : source.id)}
                  className="bg-white/10 border-white/30 text-white hover:bg-white/20 text-xs"
                >
                  {expandedSource === source.id ? "Ver menos" : "Ver más"}
                </Button>
                {source.url && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => window.open(source.url, "_blank")}
                    className="bg-blue-500/20 border-blue-400/30 text-blue-300 hover:bg-blue-500/30 text-xs"
                  >
                    Ver fuente
                  </Button>
                )}
              </div>
            </div>
          </div>
        ))}

        {sources.length === 0 && (
          <div className="text-center py-8">
            <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
              />
            </svg>
            <p className="text-gray-400">No hay fuentes disponibles</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
