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
        {/* Audio player */}
        {audioUrl && (
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
            <div className="flex items-center gap-4">
              <Button
                onClick={handlePlayPause}
                size="sm"
                className="bg-blue-600/80 hover:bg-blue-600/90 backdrop-blur-sm border border-blue-500/30 text-white"
              >
                {isPlaying ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h8m2-10v.01M3 3h18v18H3V3z"
                    />
                  </svg>
                )}
              </Button>

              <div className="flex-1">
                <input
                  id="audio-seek-bar"
                  name="audio-seek"
                  type="range"
                  min="0"
                  max={duration || 0}
                  value={currentTime}
                  onChange={handleSeek}
                  className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer"
                  aria-label="Barra de progreso del audio"
                />
                <div className="flex justify-between text-xs text-white/70 mt-1">
                  <span>{formatTime(currentTime)}</span>
                  <span>{formatTime(duration)}</span>
                </div>
              </div>

              <audio ref={audioRef} src={audioUrl} preload="metadata" />
            </div>
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
