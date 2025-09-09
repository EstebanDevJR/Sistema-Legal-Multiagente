"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  Plus, 
  MessageSquare, 
  Trash2, 
  MoreVertical,
  Bot,
  User,
  Mic,
  FileText,
  PanelLeft,
  PanelLeftClose
} from "lucide-react"
import { ChatSession } from "@/hooks/use-chat-memory"
import { useChatMemoryContext } from "@/contexts/ChatMemoryContext"

interface ChatSidebarProps {
  className?: string
  onToggleSidebar?: () => void
  sidebarOpen?: boolean
}

export default function ChatSidebar({ className, onToggleSidebar, sidebarOpen }: ChatSidebarProps) {
  const {
    sessions,
    currentSessionId,
    createNewSession,
    switchToSession,
    deleteSession,
    clearAllSessions
  } = useChatMemoryContext()

  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null)
  const [currentTime, setCurrentTime] = useState<Date | null>(null)

  // Update current time on client side only
  useEffect(() => {
    setCurrentTime(new Date())
    const interval = setInterval(() => {
      setCurrentTime(new Date())
    }, 60000) // Update every minute

    return () => clearInterval(interval)
  }, [])

  const formatTime = (date: Date) => {
    if (!currentTime) return 'Cargando...'
    
    const diff = currentTime.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 1) return 'Ahora'
    if (minutes < 60) return `${minutes}m`
    if (hours < 24) return `${hours}h`
    return `${days}d`
  }

  const getMessagePreview = (session: ChatSession) => {
    if (session.messageCount === 0) return 'Sin mensajes'
    return `${session.messageCount} mensaje${session.messageCount !== 1 ? 's' : ''}`
  }

  const getMessageTypeIcon = (session: ChatSession) => {
    // Simple icon based on message count
    if (session.messageCount === 0) return <MessageSquare className="w-4 h-4" />
    return <MessageSquare className="w-4 h-4" />
  }

  const handleDeleteSession = (sessionId: string) => {
    deleteSession(sessionId)
    setShowDeleteConfirm(null)
  }

  return (
    <div className={`w-full h-full bg-gradient-to-b from-white/10 to-white/5 backdrop-blur-md border-r border-white/20 flex flex-col shadow-2xl ${className}`}>
      {/* Redesigned Creative Header */}
      <div className="px-6 py-5 border-b border-white/20 bg-gradient-to-br from-white/8 via-white/5 to-white/8 backdrop-blur-sm">
        {/* Main Header Row */}
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="absolute inset-0 bg-green-400/30 rounded-full animate-ping"></div>
              <div className="relative w-3 h-3 bg-green-400 rounded-full animate-pulse shadow-lg shadow-green-400/50"></div>
            </div>
            <div>
              <h2 className="text-xl font-bold text-transparent bg-gradient-to-r from-white via-white/90 to-white/80 bg-clip-text">
                Conversaciones
              </h2>
              <p className="text-xs text-white/60 font-medium">Gestiona tus consultas legales</p>
            </div>
          </div>
          
          {onToggleSidebar && (
            <Button
              onClick={onToggleSidebar}
              variant="outline"
              size="sm"
              className="bg-white/8 border-white/20 text-white/80 hover:bg-white/15 hover:text-white rounded-xl transition-all duration-300 hover:scale-105 shadow-lg group"
              title={sidebarOpen ? "Ocultar conversaciones" : "Mostrar conversaciones"}
            >
              {sidebarOpen ? (
                <PanelLeftClose className="w-4 h-4 transition-transform duration-300 group-hover:rotate-180" />
              ) : (
                <PanelLeft className="w-4 h-4 transition-transform duration-300 group-hover:rotate-180" />
              )}
            </Button>
          )}
        </div>
        
        {/* Action Buttons Row */}
        <div className="flex items-center gap-3">
          {/* Enhanced New Chat Button */}
          <Button
            onClick={createNewSession}
            size="sm"
            className="flex-1 relative overflow-hidden bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 hover:from-blue-700 hover:via-blue-800 hover:to-blue-900 rounded-xl transition-all duration-300 transform hover:scale-[1.02] shadow-lg hover:shadow-xl group py-2.5"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-blue-400/20 via-purple-400/20 to-cyan-400/20 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700 ease-out"></div>
            <div className="relative flex items-center justify-center gap-2">
              <Plus className="w-4 h-4 transition-transform duration-300 group-hover:rotate-90" />
              <span className="font-semibold">Nueva Consulta</span>
            </div>
          </Button>
        </div>
        
        {/* Clear All Button - Only show when there are sessions */}
        {sessions.length > 0 && (
          <div className="mt-4 pt-4 border-t border-white/10">
            <Button
              onClick={clearAllSessions}
              variant="outline"
              size="sm"
              className="w-full border-red-400/30 text-red-300 hover:bg-red-500/20 hover:border-red-400/50 rounded-xl transition-all duration-300 hover:scale-[0.98] group shadow-lg"
            >
              <Trash2 className="w-4 h-4 mr-2 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-12" />
              <span className="font-medium">Limpiar Todo</span>
            </Button>
          </div>
        )}
      </div>

      {/* Creative Sessions List */}
      <div className="flex-1 overflow-y-auto p-3">
        {sessions.length === 0 ? (
          <div className="text-center py-12">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-green-500/20 rounded-full blur-lg"></div>
              <MessageSquare className="relative w-16 h-16 text-white/70 mx-auto mb-4 animate-bounce" />
            </div>
            <p className="text-white/90 text-sm font-medium mb-2">¡Comienza tu primera consulta!</p>
            <p className="text-white/60 text-xs">Crea una nueva conversación para empezar</p>
          </div>
        ) : (
          <div className="space-y-3">
            {sessions.map((session) => (
              <Card
                key={session.id}
                className={`group cursor-pointer transition-all duration-300 hover:bg-white/15 hover:scale-[1.02] hover:shadow-lg rounded-2xl ${
                  currentSessionId === session.id 
                    ? 'bg-gradient-to-r from-blue-600/30 to-blue-700/20 border-blue-400/40 shadow-lg shadow-blue-500/20' 
                    : 'bg-white/8 border-white/15 hover:border-white/30'
                }`}
                onClick={() => switchToSession(session.id)}
              >
                <CardContent className="p-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        {getMessageTypeIcon(session)}
                        <h3 className="text-sm font-medium text-white truncate">
                          {session.title}
                        </h3>
                      </div>
                      
                      <p className="text-xs text-white/70 truncate mb-2">
                        {getMessagePreview(session)}
                      </p>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-white/60">
                          {formatTime(session.updatedAt)}
                        </span>
                        <Badge variant="secondary" className="text-xs">
                          {session.messageCount} msgs
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-1 ml-2">
                      <Button
                        onClick={(e) => {
                          e.stopPropagation()
                          setShowDeleteConfirm(session.id)
                        }}
                        variant="ghost"
                        size="sm"
                        className="h-8 w-8 p-0 text-white/60 hover:text-red-400 hover:bg-red-500/20 rounded-lg transition-all duration-300 opacity-0 group-hover:opacity-100 hover:scale-110"
                        title="Eliminar conversación"
                      >
                        <Trash2 className="w-3 h-3 transition-transform duration-300 hover:scale-125" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Creative Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 animate-fadeIn">
          <Card className="w-80 bg-gradient-to-br from-white/15 to-white/5 backdrop-blur-md border border-white/30 rounded-2xl shadow-2xl animate-scaleIn">
            <CardHeader className="pb-3">
              <CardTitle className="text-white text-lg font-bold flex items-center gap-2">
                <div className="w-8 h-8 bg-red-500/20 rounded-full flex items-center justify-center">
                  <Trash2 className="w-4 h-4 text-red-400" />
                </div>
                Confirmar eliminación
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-white/90 mb-6 leading-relaxed">
                ¿Estás seguro de que quieres eliminar esta conversación? Esta acción no se puede deshacer.
              </p>
              <div className="flex gap-3">
                <Button
                  onClick={() => setShowDeleteConfirm(null)}
                  variant="outline"
                  className="flex-1 border-white/30 text-white hover:bg-white/10 rounded-xl transition-all duration-300 hover:scale-105"
                >
                  Cancelar
                </Button>
                <Button
                  onClick={() => handleDeleteSession(showDeleteConfirm)}
                  className="flex-1 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 rounded-xl transition-all duration-300 hover:scale-105 shadow-lg"
                >
                  Eliminar
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
