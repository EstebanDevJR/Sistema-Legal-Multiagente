"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { useVoiceRecorder } from "@/hooks/use-voice-recorder"
import { useVoiceQuery } from "@/hooks/use-voice-query"

interface VoiceRecorderProps {
  onTranscription?: (text: string) => void
  onQuerySubmit?: (audioBlob: Blob) => void
  className?: string
}

export default function VoiceRecorder({ onTranscription, onQuerySubmit, className }: VoiceRecorderProps) {
  const recorder = useVoiceRecorder()
  const voiceQuery = useVoiceQuery()
  const [waveform, setWaveform] = useState<number[]>([])

  // Simulate waveform animation during recording
  useEffect(() => {
    let interval: NodeJS.Timeout

    if (recorder.isRecording && !recorder.isPaused) {
      interval = setInterval(() => {
        setWaveform((prev) => {
          const newWave = Array.from({ length: 20 }, () => Math.random() * 100)
          return newWave
        })
      }, 100)
    } else {
      setWaveform([])
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [recorder.isRecording, recorder.isPaused])

  const handleStartRecording = async () => {
    voiceQuery.reset()
    await recorder.startRecording()
  }

  const handleStopRecording = () => {
    recorder.stopRecording()
  }

  const handleTranscribe = async () => {
    if (recorder.audioBlob) {
      try {
        const transcription = await voiceQuery.transcribeAudio(recorder.audioBlob)
        onTranscription?.(transcription)
      } catch (error) {
        console.error("[v0] Transcription error:", error)
      }
    }
  }

  const handleSubmitQuery = async () => {
    if (recorder.audioBlob && onQuerySubmit) {
      onQuerySubmit(recorder.audioBlob)
    }
  }

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, "0")}`
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Recording Interface */}
      <div className="text-center space-y-4">
        <div className="relative w-32 h-32 mx-auto">
          {/* Outer ring with pulse animation */}
          <div
            className={`absolute inset-0 bg-gradient-to-br from-white/80 to-gray-200/80 backdrop-blur-sm rounded-full border border-black/30 ${
              recorder.isRecording ? "animate-pulse" : ""
            }`}
          >
            {/* Waveform visualization */}
            {recorder.isRecording && (
              <div className="absolute inset-4 flex items-center justify-center space-x-1">
                {waveform.map((height, i) => (
                  <div
                    key={i}
                    className="w-1 bg-white/70 rounded-full transition-all duration-100"
                    style={{ height: `${Math.max(4, height * 0.4)}px` }}
                  />
                ))}
              </div>
            )}

            {/* Main record button */}
            <button
              onClick={recorder.isRecording ? handleStopRecording : handleStartRecording}
              disabled={voiceQuery.isProcessing}
              className="absolute inset-2 bg-white rounded-full flex items-center justify-center hover:scale-105 transition-transform disabled:opacity-50"
            >
              {recorder.isRecording ? (
                <div className="w-8 h-8 bg-red-500 rounded-sm"></div>
              ) : (
                <svg className="w-12 h-12 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                  />
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Status and duration */}
        <div>
          <p className="text-lg font-medium text-white">
            {recorder.isRecording
              ? recorder.isPaused
                ? "Pausado"
                : "Grabando..."
              : recorder.audioBlob
                ? "Grabación lista"
                : "Toca para grabar"}
          </p>
          <p className="text-sm text-gray-300">
            {recorder.isRecording || recorder.audioBlob
              ? `Duración: ${formatDuration(recorder.duration)}`
              : "Haz tu consulta por voz"}
          </p>
        </div>
      </div>

      {/* Recording controls */}
      {recorder.isRecording && (
        <div className="flex justify-center space-x-4">
          <Button
            onClick={recorder.isPaused ? recorder.resumeRecording : recorder.pauseRecording}
            variant="outline"
            className="bg-white/15 border-white/30 text-white hover:bg-white/25 backdrop-blur-sm"
          >
            {recorder.isPaused ? "Reanudar" : "Pausar"}
          </Button>
        </div>
      )}

      {/* Audio playback and actions */}
      {recorder.audioBlob && !recorder.isRecording && (
        <div className="space-y-4">
          <audio controls src={recorder.audioUrl || undefined} className="w-full bg-white/10 rounded-lg" />

          <div className="flex flex-col sm:flex-row gap-3">
            <Button
              onClick={handleTranscribe}
              disabled={voiceQuery.isProcessing}
              className="flex-1 bg-blue-600/80 hover:bg-blue-600/90 backdrop-blur-sm border border-blue-500/30 text-white"
            >
              {voiceQuery.isProcessing ? "Transcribiendo..." : "Transcribir"}
            </Button>

            <Button
              onClick={handleSubmitQuery}
              disabled={voiceQuery.isProcessing}
              className="flex-1 bg-green-600/80 hover:bg-green-600/90 backdrop-blur-sm border border-green-500/30 text-white"
            >
              Enviar Consulta
            </Button>

            <Button
              onClick={recorder.reset}
              variant="outline"
              className="bg-white/15 border-white/30 text-white hover:bg-white/25 backdrop-blur-sm"
            >
              Nueva Grabación
            </Button>
          </div>
        </div>
      )}

      {/* Transcription display */}
      {voiceQuery.transcription && (
        <div className="p-4 bg-white/10 backdrop-blur-sm rounded-lg border border-white/20">
          <h4 className="text-sm font-medium text-gray-300 mb-2">Transcripción:</h4>
          <p className="text-white">{voiceQuery.transcription}</p>
        </div>
      )}

      {/* Error display */}
      {(recorder.error || voiceQuery.error) && (
        <div className="p-4 bg-red-500/20 backdrop-blur-sm rounded-lg border border-red-400/30">
          <p className="text-red-200">{recorder.error || voiceQuery.error}</p>
        </div>
      )}
    </div>
  )
}
