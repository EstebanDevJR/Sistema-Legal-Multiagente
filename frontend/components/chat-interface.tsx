"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useToast } from "@/hooks/use-toast"
import { useVoiceRecorder } from "@/hooks/use-voice-recorder"
import { useVoiceQuery } from "@/hooks/use-voice-query"
import { useLegalQuery } from "@/hooks/use-legal-query"
import { ChatMessage } from "@/hooks/use-chat-memory"
import { useChatMemoryContext } from "@/contexts/ChatMemoryContext"
import { useDocuments } from "@/contexts/DocumentContext"
import type { LegalQueryResponse } from "@/lib/api-types"
import { apiClient } from "@/lib/api-client"
import EmailConversationModal from "@/components/email-conversation-modal"
import { 
  Mic, 
  MicOff, 
  Send, 
  Paperclip, 
  Volume2, 
  VolumeX,
  Bot,
  User,
  FileText,
  MessageSquare,
  Copy,
  Check,
  Plus,
  Mail
} from "lucide-react"

interface ChatInterfaceProps {
  className?: string
}

export default function ChatInterface({ className }: ChatInterfaceProps) {
  const [inputText, setInputText] = useState("")
  const [responseMode, setResponseMode] = useState<'text' | 'audio'>('text')
  const [isProcessing, setIsProcessing] = useState(false)
  const [copiedMessages, setCopiedMessages] = useState<Set<string>>(new Set())
  const [isEmailModalOpen, setIsEmailModalOpen] = useState(false)
  const [streamingMessage, setStreamingMessage] = useState<string>("")
  const [isStreaming, setIsStreaming] = useState(false)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  const { toast } = useToast()
  const { uploadedDocuments, uploadedDocumentIds, addDocument, clearDocuments } = useDocuments()

  const copyToClipboard = async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedMessages(prev => new Set(prev).add(messageId))
      
      toast({
        title: "Texto copiado",
        description: "La respuesta ha sido copiada al portapapeles.",
        duration: 2000
      })
      
      // Reset the copied state after 2 seconds
      setTimeout(() => {
        setCopiedMessages(prev => {
          const newSet = new Set(prev)
          newSet.delete(messageId)
          return newSet
        })
      }, 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
      toast({
        title: "Error al copiar",
        description: "No se pudo copiar el texto al portapapeles.",
        variant: "destructive"
      })
    }
  }

  const voiceRecorder = useVoiceRecorder()
  const voiceQuery = useVoiceQuery()
  const legalQuery = useLegalQuery()
  const { 
    currentMessages, 
    currentSessionId,
    isLoadingSession,
    addMessage, 
    updateMessage, 
    createNewSession 
  } = useChatMemoryContext()



  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [currentMessages, streamingMessage])

  // Simulate streaming effect for text - smooth with variable speed
  const simulateStreaming = (text: string): Promise<void> => {
    return new Promise((resolve) => {
      setIsStreaming(true)
      setStreamingMessage("")
      
      const characters = text.split('')
      let currentIndex = 0
      
      const streamNextChar = () => {
        if (currentIndex < characters.length) {
          const char = characters[currentIndex]
          setStreamingMessage(prev => prev + char)
          currentIndex++
          
          // Variable speed based on character type
          let delay = 25 // Base speed
          if (char === '.' || char === '!' || char === '?') {
            delay = 150 // Pause at sentence endings
          } else if (char === ',' || char === ';' || char === ':') {
            delay = 80 // Pause at punctuation
          } else if (char === ' ') {
            delay = 35 // Slightly slower for spaces
          } else if (char === '\n') {
            delay = 100 // Pause at line breaks
          }
          
          setTimeout(streamNextChar, delay)
        } else {
          setIsStreaming(false)
          setStreamingMessage("")
          resolve()
        }
      }
      
      streamNextChar()
    })
  }

  // Don't auto-create sessions - let user start conversations manually

  const handleTextSubmit = async () => {
    if (!inputText.trim() || isProcessing) return

    // Create session if none exists and wait for it to complete
    let sessionId = currentSessionId
    if (!sessionId) {
      const newSession = await createNewSession()
      sessionId = newSession?.id || null
      
      if (!sessionId) {
        console.error('Failed to create session')
        return
      }
    }

    const userMessage = await addMessage({
      type: 'user',
      content: inputText.trim()
    }, sessionId)

    if (!userMessage) {
      console.error('Failed to add user message')
      return
    }

    setInputText("")
    setIsProcessing(true)

    // Add the "analyzing" message immediately
    const tempMessage = await addMessage({
      type: 'assistant',
      content: "🤖 Analizando tu consulta legal...",
      confidence: undefined,
      area: undefined
    }, sessionId)

    try {
      toast({
        title: "Procesando consulta",
        description: "Analizando tu consulta legal..."
      })

      console.log("🔍 Sending query with document IDs:", uploadedDocumentIds)
      const queryData = {
        query: userMessage.content,
        method: "text" as const,
        area: "general",
        sessionId: sessionId || undefined,
        documentIds: uploadedDocumentIds || []
      }
      console.log("🔍 Query data being sent:", queryData)
      const response = await legalQuery.submitQuery(queryData) as any

      let assistantMessage = tempMessage;

      if (responseMode === 'audio' && response.response) {
        // For audio mode, generate audio first and update message
        try {
          const audioResponse = await voiceQuery.generateSpeech(response.response)
          
          // Update the temporary message with audio
          if (tempMessage) {
            console.log("🔄 Updating message with audio response")
            await updateMessage(tempMessage.id, {
              content: "🔊 Respuesta de audio",
              audioUrl: audioResponse
            }, sessionId)
            console.log("✅ Audio message update completed")
          }
        } catch (error) {
          console.error("Error generating audio:", error)
          // Fallback to text if audio generation fails
          if (tempMessage) {
            // Simulate streaming for fallback text
            await simulateStreaming(response.response)
            console.log("🔄 Updating fallback message with text response")
            await updateMessage(tempMessage.id, {
              content: response.response
            }, sessionId)
            console.log("✅ Fallback message update completed")
          }
        }
      } else {
        // For text mode, simulate streaming effect
        if (tempMessage) {
          await simulateStreaming(response.response)
          console.log("🔄 Updating message with response:", response.response.substring(0, 100))
          await updateMessage(tempMessage.id, {
            content: response.response
          }, sessionId)
          console.log("✅ Message update completed")
        }
      }

      toast({
        title: "Consulta procesada",
        description: "Tu consulta ha sido analizada exitosamente."
      })

    } catch (error) {
      console.error("Error processing text query:", error)
      addMessage({
        type: 'assistant',
        content: "Lo siento, hubo un error al procesar tu consulta. Por favor, inténtalo de nuevo."
      }, sessionId)
      
      toast({
        title: "Error en consulta",
        description: "No se pudo procesar tu consulta. Inténtalo nuevamente.",
        variant: "destructive"
      })
    } finally {
      setIsProcessing(false)
    }
  }

  const handleVoiceSubmit = async () => {
    if (!voiceRecorder.audioBlob || isProcessing) return

    // Create session if none exists and wait for it to complete
    let sessionId = currentSessionId
    if (!sessionId) {
      const newSession = await createNewSession()
      sessionId = newSession?.id || null
      
      if (!sessionId) {
        console.error('Failed to create session')
        return
      }
    }

    const userMessage = await addMessage({
      type: 'user',
      content: "🎤 Consulta por voz",
      transcription: "Grabación de audio"
    }, sessionId)

    setIsProcessing(true)

    // Add the "analyzing" message immediately
    const tempMessage = await addMessage({
      type: 'assistant',
      content: "🤖 Analizando tu consulta legal...",
      confidence: undefined,
      area: undefined
    }, sessionId)

    try {
      toast({
        title: "Procesando audio",
        description: "Transcribiendo y analizando tu consulta de voz..."
      })

      const response = await voiceQuery.submitVoiceQuery(voiceRecorder.audioBlob, responseMode, uploadedDocumentIds)

      // Update user message with transcription
      const transcription = (response.metadata as any)?.transcription
      updateMessage(userMessage.id, {
        content: transcription || "Consulta por voz",
        transcription: transcription
      })

      // Simulate streaming and update message
      if (tempMessage) {
        if (responseMode === 'audio' && response.audioUrl) {
          // For audio mode, just update with audio
          updateMessage(tempMessage.id, {
            content: "🔊 Respuesta de audio",
            audioUrl: response.audioUrl
          })
        } else {
          // For text mode, simulate streaming
          await simulateStreaming(response.response)
          updateMessage(tempMessage.id, {
            content: response.response
          })
        }
      }

      toast({
        title: "Consulta de voz procesada",
        description: "Tu consulta de voz ha sido analizada exitosamente."
      })

    } catch (error) {
      console.error("Error processing voice query:", error)
      addMessage({
        type: 'assistant',
        content: "Lo siento, hubo un error al procesar tu consulta de voz. Por favor, inténtalo de nuevo."
      }, sessionId)
      
      toast({
        title: "Error en consulta de voz",
        description: "No se pudo procesar tu consulta de voz. Inténtalo nuevamente.",
        variant: "destructive"
      })
    } finally {
      setIsProcessing(false)
      voiceRecorder.reset()
    }
  }

  const handleDocumentUpload = async (files: FileList) => {
    const fileArray = Array.from(files)
    
    try {
      toast({
        title: "Subiendo documentos",
        description: "Procesando archivos..."
      })

      // Subir cada archivo al backend
      const uploadPromises = fileArray.map(async (file) => {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('user_id', 'chat_user')
        formData.append('document_type', 'legal_document')
        formData.append('description', `Documento subido desde chat: ${file.name}`)

        const response = await fetch('http://localhost:8000/documents/upload', {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          throw new Error(`Error subiendo ${file.name}`)
        }

        return response.json()
      })

                const results = await Promise.all(uploadPromises)

          // Extraer IDs de los documentos subidos y agregar al contexto global
          const documentIds = results.map(result => result.document.id)
          
          // Agregar cada documento al contexto global
          fileArray.forEach((file, index) => {
            addDocument(file, documentIds[index])
          })

          toast({
            title: "Documentos subidos",
            description: `${fileArray.length} documento(s) subido(s) exitosamente.`
          })
    } catch (error) {
      console.error("Error uploading documents:", error)
      toast({
        title: "Error al subir documentos",
        description: "No se pudieron subir algunos archivos. Inténtalo de nuevo."
      })
    }
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('es-ES', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <div className={`flex flex-col h-full min-h-0 ${className}`}>
      {/* Top Content: Header + Messages */}
      <div className="flex-1 flex flex-col min-h-0">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-white/10 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-white">Asistente Legal</h1>
              <p className="text-sm text-white/90">Consulta legal inteligente</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {/* Email button - show only when there are messages */}
            {currentMessages.length > 0 && (
              <Button
                onClick={() => setIsEmailModalOpen(true)}
                variant="outline"
                size="sm"
                className="bg-white/10 border-white/20 text-white hover:bg-white/20 transition-all"
                title="Enviar conversación por email"
              >
                <Mail className="w-4 h-4" />
              </Button>
            )}
            
            {/* Creative Mode Selector */}
            <div className="relative bg-white/5 backdrop-blur-sm rounded-2xl p-1 border border-white/10">
              <div className="flex relative">
                {/* Animated Background Slider */}
                <div 
                  className={`absolute top-1 bottom-1 w-1/2 bg-gradient-to-r rounded-xl transition-all duration-500 ease-out transform ${
                    responseMode === 'text' 
                      ? 'translate-x-0 from-blue-500/80 to-blue-600/80 shadow-lg shadow-blue-500/30' 
                      : 'translate-x-full from-green-500/80 to-green-600/80 shadow-lg shadow-green-500/30'
                  }`}
                />
                
                {/* Text Mode Button */}
                <button
                  onClick={() => setResponseMode('text')}
                  className={`relative z-10 flex items-center justify-center px-6 py-3 rounded-xl transition-all duration-300 ease-out transform hover:scale-105 ${
                    responseMode === 'text'
                      ? 'text-white font-semibold'
                      : 'text-white/70 hover:text-white/90'
                  }`}
                >
                  <MessageSquare className={`w-4 h-4 mr-2 transition-all duration-300 ${
                    responseMode === 'text' ? 'animate-pulse' : ''
                  }`} />
                  <span className="text-sm font-medium">Texto</span>
                </button>
                
                {/* Audio Mode Button */}
                <button
                  onClick={() => setResponseMode('audio')}
                  className={`relative z-10 flex items-center justify-center px-6 py-3 rounded-xl transition-all duration-300 ease-out transform hover:scale-105 ${
                    responseMode === 'audio'
                      ? 'text-white font-semibold'
                      : 'text-white/70 hover:text-white/90'
                  }`}
                >
                  <Volume2 className={`w-4 h-4 mr-2 transition-all duration-300 ${
                    responseMode === 'audio' ? 'animate-pulse' : ''
                  }`} />
                  <span className="text-sm font-medium">Audio</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
        {currentMessages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            {isLoadingSession ? (
              <>
                <div className="w-8 h-8 border-2 border-white border-t-black rounded-full animate-spin mb-4"></div>
                <p className="text-white/90">Cargando conversación...</p>
              </>
            ) : currentSessionId ? (
              <>
                <MessageSquare className="w-12 h-12 text-white/60 mb-4" />
                <p className="text-white/90">Esta conversación está vacía</p>
                <p className="text-white/70 text-sm mt-1">Escribe tu primera consulta legal</p>
              </>
            ) : (
              <>
                <Bot className="w-12 h-12 text-white/60 mb-4" />
                <p className="text-white/90">Selecciona una conversación o crea una nueva</p>
                <p className="text-white/70 text-sm mt-1">Comienza tu consulta legal</p>
              </>
            )}
          </div>
        ) : (
          currentMessages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {message.type === 'assistant' && (
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                <Bot className="w-5 h-5 text-white" />
              </div>
            )}
            
            <div className={`max-w-[80%] ${message.type === 'user' ? 'order-first' : ''}`}>
              <Card className={`${
                message.type === 'user' 
                  ? 'bg-blue-600/80 border-blue-500/30' 
                  : 'bg-white/10 border-white/20'
              } backdrop-blur-sm`}>
                <CardContent className="p-4">
                  <div className="space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-white whitespace-pre-wrap flex-1">
                        {message.content}
                        {message.content.includes("Analizando tu consulta") && (
                          <span className="inline-flex items-center ml-2">
                            <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce mr-1"></span>
                            <span className="w-2 h-2 bg-green-400 rounded-full animate-bounce mr-1" style={{animationDelay: '0.1s'}}></span>
                            <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></span>
                          </span>
                        )}
                      </p>
                      {message.type === 'assistant' && (
                        <Button
                          onClick={() => copyToClipboard(message.content, message.id)}
                          variant="ghost"
                          size="sm"
                          className="flex-shrink-0 h-8 w-8 p-0 text-white/60 hover:text-white hover:bg-white/10 transition-all"
                          title="Copiar respuesta"
                        >
                          {copiedMessages.has(message.id) ? (
                            <Check className="w-4 h-4 text-green-400" />
                          ) : (
                            <Copy className="w-4 h-4" />
                          )}
                        </Button>
                      )}
                    </div>
                    
                    {message.transcription && message.type === 'user' && (
                      <p className="text-sm text-white/80 italic">
                        Transcripción: {message.transcription}
                      </p>
                    )}
                    
                    {message.audioUrl && (
                      <div className="mt-3 p-3 bg-white/5 rounded-lg border border-white/10">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-green-600/20 rounded-full flex items-center justify-center">
                            <Volume2 className="w-5 h-5 text-green-400" />
                          </div>
                          <div className="flex-1">
                            <p className="text-sm text-white/90 mb-1">Respuesta de audio</p>
                            <audio 
                              controls 
                              className="w-full h-8 bg-white/10 rounded-lg [&::-webkit-media-controls-panel]:bg-white/10 [&::-webkit-media-controls-play-button]:bg-white/20 [&::-webkit-media-controls-play-button]:rounded"
                              onError={(e) => {
                                console.error("Audio error:", e)
                                console.error("Audio URL:", message.audioUrl)
                              }}
                              onLoadStart={() => {
                                console.log("Audio loading started:", message.audioUrl)
                              }}
                              onCanPlay={() => {
                                console.log("Audio can play:", message.audioUrl)
                              }}
                            >
                              <source src={message.audioUrl} type="audio/mpeg" />
                              <source src={message.audioUrl} type="audio/wav" />
                              <source src={message.audioUrl} type="audio/webm" />
                              Tu navegador no soporta el elemento de audio.
                            </audio>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    
                    {message.area && (
                      <Badge variant="secondary" className="mt-2">
                        {message.area}
                      </Badge>
                    )}
                  </div>
                </CardContent>
              </Card>
              
              <div className={`text-xs text-white/60 mt-1 ${
                message.type === 'user' ? 'text-right' : 'text-left'
              }`}>
                {formatTime(message.timestamp)}
              </div>
            </div>
            
            {message.type === 'user' && (
              <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center flex-shrink-0">
                <User className="w-5 h-5 text-white" />
              </div>
            )}
          </div>
        ))
        )}
        
        {/* Streaming Message */}
        {isStreaming && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="max-w-[80%]">
              <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
                <CardContent className="p-4">
                  <div className="space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-white whitespace-pre-wrap flex-1">
                        {streamingMessage}
                        <span className="inline-block w-2 h-5 bg-blue-400 ml-1 animate-pulse"></span>
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area - Fixed at bottom */}
      <div className="p-4 mt-auto border-t bg-white/10 backdrop-blur-sm">
        {/* Voice Recording */}
        {voiceRecorder.isRecording && (
          <div className="mb-4 p-3 bg-red-500/20 border border-red-400/30 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                <span className="text-red-200">Grabando... {voiceRecorder.duration}s</span>
              </div>
              <Button
                onClick={voiceRecorder.stopRecording}
                variant="outline"
                size="sm"
                className="border-red-400/30 text-red-200 hover:bg-red-500/20"
              >
                <MicOff className="w-4 h-4 mr-1" />
                Detener
              </Button>
            </div>
          </div>
        )}

        {/* Audio Playback */}
        {voiceRecorder.audioBlob && !voiceRecorder.isRecording && (
          <div className="mb-4 p-3 bg-green-500/20 border border-green-400/30 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-green-200" />
                <span className="text-green-200">Grabación lista ({voiceRecorder.duration}s)</span>
              </div>
              <div className="flex gap-2">
                <div className="flex-1">
                  <audio 
                    controls 
                    className="w-full h-8 bg-white/10 rounded-lg [&::-webkit-media-controls-panel]:bg-white/10 [&::-webkit-media-controls-play-button]:bg-white/20 [&::-webkit-media-controls-play-button]:rounded"
                  >
                    <source src={voiceRecorder.audioUrl || undefined} type="audio/webm" />
                  </audio>
                </div>
                <Button
                  onClick={handleVoiceSubmit}
                  disabled={isProcessing}
                  size="sm"
                  className="bg-green-600 hover:bg-green-700 transition-all"
                >
                  <Send className="w-4 h-4 mr-1" />
                  Enviar
                </Button>
                <Button
                  onClick={voiceRecorder.reset}
                  variant="outline"
                  size="sm"
                  className="border-green-400/30 text-green-200 hover:bg-green-500/20 transition-all"
                >
                  Cancelar
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Creative Input Area */}
        <div className="space-y-4">
          {/* Main Input Container */}
          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 via-green-500/20 to-purple-500/20 rounded-2xl blur-sm opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
            <div className="relative bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-1 shadow-lg">
              <div className="flex items-center gap-2">
                {/* Text Input with Creative Design */}
                <div className="flex-1 relative">
                  <textarea
                    id="chat-message-input"
                    name="chat-message"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey && !isProcessing && !isLoadingSession) {
                        e.preventDefault()
                        handleTextSubmit()
                      }
                    }}
                    placeholder="✨ Escribe tu consulta legal aquí..."
                    disabled={isProcessing || isLoadingSession}
                    className="w-full px-4 py-3 pr-16 bg-transparent text-white placeholder-white/60 resize-none focus:outline-none rounded-xl transition-all duration-300 focus:placeholder-white/80"
                    rows={1}
                    style={{ minHeight: '48px', maxHeight: '120px' }}
                    aria-label="Mensaje de chat"
                  />
                  
                  {/* Animated File Upload Button */}
                  <Button
                    onClick={() => fileInputRef.current?.click()}
                    variant="ghost"
                    size="sm"
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-white/60 hover:text-white hover:bg-white/10 rounded-lg transition-all duration-300 hover:scale-110 group/file"
                    title="Subir archivos"
                  >
                    <Paperclip className="w-4 h-4 transition-transform duration-300 group-hover/file:rotate-12" />
                  </Button>
                </div>
                
                {/* Creative Action Buttons */}
                <div className="flex gap-2">
                  {/* Voice Recording Button */}
                  <Button
                    onClick={voiceRecorder.isRecording ? voiceRecorder.stopRecording : voiceRecorder.startRecording}
                    disabled={isProcessing}
                    variant="outline"
                    className={`relative overflow-hidden px-4 py-2 h-12 rounded-xl transition-all duration-300 transform hover:scale-105 group/mic ${
                      voiceRecorder.isRecording 
                        ? 'bg-red-500/20 border-red-400/30 text-red-200 hover:bg-red-500/30 animate-pulse' 
                        : 'bg-white/10 border-white/20 text-white hover:bg-white/20'
                    }`}
                    title={voiceRecorder.isRecording ? "Detener grabación" : "Iniciar grabación"}
                  >
                    {voiceRecorder.isRecording && (
                      <div className="absolute inset-0 bg-gradient-to-r from-red-500/30 to-red-600/30 animate-pulse"></div>
                    )}
                    <div className="relative">
                      {voiceRecorder.isRecording ? (
                        <MicOff className="w-4 h-4 transition-transform duration-300 group-hover/mic:scale-110" />
                      ) : (
                        <Mic className="w-4 h-4 transition-transform duration-300 group-hover/mic:scale-110" />
                      )}
                    </div>
                  </Button>
                  
                  {/* Send Button with Gradient and Animation */}
                  <Button
                    onClick={handleTextSubmit}
                    disabled={!inputText.trim() || isProcessing || isLoadingSession}
                    className="relative overflow-hidden px-6 py-2 h-12 bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 hover:from-blue-700 hover:via-blue-800 hover:to-blue-900 rounded-xl transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none group/send shadow-lg"
                    title="Enviar mensaje"
                  >
                    {/* Animated Background */}
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-purple-400/20 translate-x-[-100%] group-hover/send:translate-x-[100%] transition-transform duration-700 ease-out"></div>
                    
                    <div className="relative flex items-center">
                      {isProcessing || isLoadingSession ? (
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <Send className="w-4 h-4 transition-transform duration-300 group-hover/send:translate-x-1" />
                      )}
                    </div>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          id="chat-file-input"
          name="chat-files"
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.txt"
          onChange={(e) => e.target.files && handleDocumentUpload(e.target.files)}
          className="hidden"
          aria-label="Subir archivos para el chat"
        />

        {/* Uploaded documents */}
        {uploadedDocuments.length > 0 && (
          <div className="mt-3 p-2 bg-white/5 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-white/90">Documentos cargados:</p>
              <Button
                onClick={() => {
                  clearDocuments()
                }}
                variant="ghost"
                size="sm"
                className="text-xs text-white/70 hover:text-white"
              >
                Limpiar
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {uploadedDocuments.map((doc, index) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  <FileText className="w-3 h-3 mr-1" />
                  {doc.name}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Email Modal */}
      <EmailConversationModal
        isOpen={isEmailModalOpen}
        onClose={() => setIsEmailModalOpen(false)}
        messages={currentMessages}
        sessionTitle={`Consulta Legal - ${new Date().toLocaleDateString('es-ES')}`}
      />
    </div>
  )
}
