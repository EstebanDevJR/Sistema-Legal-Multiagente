"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"

export default function OfflineIndicator() {
  const [isOnline, setIsOnline] = useState(true)
  const [showOfflineMessage, setShowOfflineMessage] = useState(false)
  const [isHydrated, setIsHydrated] = useState(false)

  useEffect(() => {
    setIsHydrated(true)
    const handleOnline = () => {
      setIsOnline(true)
      setShowOfflineMessage(false)
    }

    const handleOffline = () => {
      setIsOnline(false)
      setShowOfflineMessage(true)
    }

    // Set initial state
    setIsOnline(navigator.onLine)

    window.addEventListener("online", handleOnline)
    window.addEventListener("offline", handleOffline)

    return () => {
      window.removeEventListener("online", handleOnline)
      window.removeEventListener("offline", handleOffline)
    }
  }, [])

  // Auto-hide offline message after 5 seconds when back online
  useEffect(() => {
    if (isOnline && showOfflineMessage) {
      const timer = setTimeout(() => {
        setShowOfflineMessage(false)
      }, 3000)
      return () => clearTimeout(timer)
    }
    return undefined
  }, [isOnline, showOfflineMessage])

  if (!isHydrated || (!showOfflineMessage && isOnline)) return null

  return (
    <Card
      className={`fixed top-4 left-1/2 transform -translate-x-1/2 z-50 backdrop-blur-md border animate-in slide-in-from-top-full ${
        isOnline ? "bg-green-500/20 border-green-400/30" : "bg-red-500/20 border-red-400/30"
      }`}
    >
      <CardContent className="p-3">
        <div className="flex items-center gap-2">
          {isOnline ? (
            <>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-green-300 text-sm font-medium">Conexión restaurada</span>
            </>
          ) : (
            <>
              <div className="w-2 h-2 bg-red-400 rounded-full animate-pulse" />
              <span className="text-red-300 text-sm font-medium">Sin conexión a internet</span>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
