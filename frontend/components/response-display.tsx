"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import ReactMarkdown from "react-markdown"

interface ResponseDisplayProps {
  response: string
  audioUrl?: string
  isPlaying: boolean
  onPlayToggle: (playing: boolean) => void
}

export default function ResponseDisplay({ response, audioUrl, isPlaying, onPlayToggle }: ResponseDisplayProps) {
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const audioRef = useRef<HTMLAudioElement>(null)

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const updateTime = () => setCurrentTime(audio.currentTime)
    const updateDuration = () => setDuration(audio.duration)
    const handleEnded = () => onPlayToggle(false)

    audio.addEventListener("timeupdate", updateTime)
    audio.addEventListener("loadedmetadata", updateDuration)
    audio.addEventListener("ended", handleEnded)

    return () => {
      audio.removeEventListener("timeupdate", updateTime)
      audio.removeEventListener("loadedmetadata", updateDuration)
      audio.removeEventListener("ended", handleEnded)
    }
  }, [onPlayToggle])

  const handlePlayPause = () => {
    const audio = audioRef.current
    if (!audio) return

    if (isPlaying) {
      audio.pause()
      onPlayToggle(false)
    } else {
      audio.play()
      onPlayToggle(true)
    }
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const audio = audioRef.current
    if (!audio) return

    const newTime = Number.parseFloat(e.target.value)
    audio.currentTime = newTime
    setCurrentTime(newTime)
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, "0")}`
  }

  return (
    <Card className="backdrop-blur-md bg-white/15 border border-white/30">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          Respuesta Legal
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Audio player - Extra grande y fácil de usar */}
        {audioUrl && (
          <div className="bg-gradient-to-br from-blue-600/20 to-purple-600/20 backdrop-blur-sm rounded-xl p-8 border border-white/30 space-y-6 shadow-xl">
            {/* Header del reproductor */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="relative">
                  <Button
                    onClick={handlePlayPause}
                    size="lg"
                    className="bg-blue-600/90 hover:bg-blue-600 backdrop-blur-sm border-2 border-blue-400/50 text-white w-16 h-16 rounded-full audio-control-btn shadow-lg"
                  >
                    {isPlaying ? (
                      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6" />
                      </svg>
                    ) : (
                      <svg className="w-8 h-8 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h8m2-10v.01M3 3h18v18H3V3z" />
                      </svg>
                    )}
                  </Button>
                  {isPlaying && (
                    <div className="absolute -inset-1 rounded-full border-2 border-blue-400 animate-pulse"></div>
                  )}
                </div>
                <div className="text-white">
                  <div className="text-xl font-semibold">Respuesta de Audio</div>
                  <div className="text-base text-white/80">Síntesis de voz legal profesional</div>
                </div>
              </div>
              <div className="text-right text-white/90">
                <div className="text-2xl font-mono font-bold">{formatTime(currentTime)}</div>
                <div className="text-base text-white/70">de {formatTime(duration)}</div>
              </div>
            </div>

            {/* Barra de progreso extra grande */}
            <div className="space-y-4">
              <div className="relative py-2">
                <input
                  id="audio-seek-bar"
                  name="audio-seek"
                  type="range"
                  min="0"
                  max={duration || 0}
                  value={currentTime}
                  onChange={handleSeek}
                  className="w-full h-6 bg-white/20 rounded-full appearance-none cursor-pointer slider-thumb"
                  aria-label="Barra de progreso del audio"
                />
                {/* Indicador de progreso visual mejorado */}
                <div 
                  className="absolute top-2 left-0 h-6 bg-gradient-to-r from-blue-500 to-blue-400 rounded-full pointer-events-none transition-all duration-200 shadow-md"
                  style={{ width: `${(currentTime / duration) * 100}%` }}
                />
                {/* Marcador de posición actual */}
                <div 
                  className="absolute top-1 w-8 h-8 bg-white rounded-full shadow-lg border-2 border-blue-500 pointer-events-none transition-all duration-200"
                  style={{ left: `calc(${(currentTime / duration) * 100}% - 16px)` }}
                />
              </div>
              
              {/* Controles adicionales más grandes */}
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-6">
                  <button 
                    onClick={() => {
                      const audio = audioRef.current
                      if (audio) {
                        audio.currentTime = Math.max(0, audio.currentTime - 10)
                      }
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white hover:text-white transition-all duration-200 border border-white/20"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0019 16V8a1 1 0 00-1.6-.8l-5.333 4zM4.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0011 16V8a1 1 0 00-1.6-.8l-5.334 4z" />
                    </svg>
                    <span className="font-medium">-10s</span>
                  </button>
                  <button 
                    onClick={() => {
                      const audio = audioRef.current
                      if (audio) {
                        audio.currentTime = Math.min(duration, audio.currentTime + 10)
                      }
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white hover:text-white transition-all duration-200 border border-white/20"
                  >
                    <span className="font-medium">+10s</span>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.933 12.8a1 1 0 000-1.6L6.6 7.2A1 1 0 005 8v8a1 1 0 001.6.8l5.333-4zM19.933 12.8a1 1 0 000-1.6l-5.333-4A1 1 0 0013 8v8a1 1 0 001.6.8l5.333-4z" />
                    </svg>
                  </button>
                  <button 
                    onClick={() => {
                      const audio = audioRef.current
                      if (audio) {
                        audio.currentTime = 0
                      }
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white hover:text-white transition-all duration-200 border border-white/20"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    <span className="font-medium">Reiniciar</span>
                  </button>
                </div>
                <div className="flex flex-col items-end">
                  <div className="text-lg font-bold text-white">
                    {duration > 0 ? `${Math.round((currentTime / duration) * 100)}%` : '0%'}
                  </div>
                  <div className="text-sm text-white/70">Progreso</div>
                </div>
              </div>
            </div>

            <audio ref={audioRef} src={audioUrl} preload="metadata" />
          </div>
        )}

        {/* Response content */}
        <div className="max-w-none text-white leading-relaxed">
          <ReactMarkdown
            components={{
              h1: ({ children }) => <h1 className="text-2xl font-bold text-white mb-4">{children}</h1>,
              h2: ({ children }) => <h2 className="text-xl font-semibold text-white mb-3 mt-6">{children}</h2>,
              h3: ({ children }) => <h3 className="text-lg font-medium text-white mb-2 mt-4">{children}</h3>,
              p: ({ children }) => <p className="text-white/90 mb-4 leading-relaxed">{children}</p>,
              ul: ({ children }) => <ul className="list-disc list-inside text-white/90 mb-4 space-y-1">{children}</ul>,
              ol: ({ children }) => (
                <ol className="list-decimal list-inside text-white/90 mb-4 space-y-1">{children}</ol>
              ),
              li: ({ children }) => <li className="text-white/90">{children}</li>,
              strong: ({ children }) => <strong className="text-white font-semibold">{children}</strong>,
              em: ({ children }) => <em className="text-blue-300">{children}</em>,
              blockquote: ({ children }) => (
                <blockquote className="border-l-4 border-blue-400/50 pl-4 py-2 bg-blue-500/10 rounded-r-lg mb-4">
                  {children}
                </blockquote>
              ),
              code: ({ children }) => (
                <code className="bg-white/10 px-2 py-1 rounded text-cyan-300 font-mono text-sm">{children}</code>
              ),
            }}
          >
            {response}
          </ReactMarkdown>
        </div>
      </CardContent>
    </Card>
  )
}
