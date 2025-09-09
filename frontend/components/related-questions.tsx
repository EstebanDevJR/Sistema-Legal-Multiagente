"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

interface RelatedQuestionsProps {
  questions: string[]
  onQuestionSelect?: (question: string) => void
}

export default function RelatedQuestions({ questions, onQuestionSelect }: RelatedQuestionsProps) {
  const handleQuestionClick = (question: string) => {
    if (onQuestionSelect) {
      onQuestionSelect(question)
    }
  }

  return (
    <Card className="backdrop-blur-md bg-white/15 border border-white/30">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          Preguntas Relacionadas
        </CardTitle>
      </CardHeader>
      <CardContent>
        {questions.length > 0 ? (
          <div className="space-y-3">
            {questions.map((question, index) => (
              <Button
                key={index}
                variant="outline"
                onClick={() => handleQuestionClick(question)}
                className="w-full text-left justify-start h-auto p-4 bg-white/10 border-white/30 text-white hover:bg-white/20 backdrop-blur-sm"
              >
                <div className="flex items-start gap-3">
                  <svg
                    className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  <span className="text-sm leading-relaxed">{question}</span>
                </div>
              </Button>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <p className="text-gray-400">No hay preguntas relacionadas disponibles</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
