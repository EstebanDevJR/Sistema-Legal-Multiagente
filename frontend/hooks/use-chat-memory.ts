"use client"

import { useState, useEffect, useCallback } from "react"
import { apiClient } from '@/lib/api-client'

export interface ChatMessage {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  audioUrl?: string
  transcription?: string
  audioTranscription?: string // Transcripción del audio de respuesta del asistente
  sources?: any[]
  confidence?: number
  area?: string
}

export interface ChatSession {
  id: string
  title: string
  messageCount: number
  createdAt: Date
  updatedAt: Date
}

export function useChatMemory() {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [currentMessages, setCurrentMessages] = useState<ChatMessage[]>([])
  const [isInitialized, setIsInitialized] = useState(false)
  const [isLoadingSession, setIsLoadingSession] = useState(false)


  const loadSessions = useCallback(async () => {
    try {
      const sessions = await apiClient.getChatSessions()
      // Convert date strings to Date objects and snake_case to camelCase
      const sessionsWithDates = sessions.map(session => ({
        ...session,
        messageCount: session.message_count,
        createdAt: new Date(session.created_at),
        updatedAt: new Date(session.updated_at)
      }))
      setSessions(sessionsWithDates)
    } catch (error) {
      console.error('Error loading sessions from backend:', error)
    }
  }, [])

  // Load sessions from backend on mount - only once
  useEffect(() => {
    if (!isInitialized) {
      loadSessions()
      setIsInitialized(true)
    }
  }, [isInitialized, loadSessions])

  const createNewSession = useCallback(async () => {
    try {
      const newSession = await apiClient.createChatSession('Nueva consulta legal')
      // Convert date strings to Date objects and snake_case to camelCase
      const sessionWithDates = {
        ...newSession,
        messageCount: newSession.message_count,
        createdAt: new Date(newSession.created_at),
        updatedAt: new Date(newSession.updated_at)
      }
      setSessions(prev => [sessionWithDates, ...prev.slice(0, 9)]) // Max 10 sessions
      setCurrentSessionId(newSession.id)
      setCurrentMessages([]) // Clear current messages
      
      // Add welcome message
      const welcomeMessage: ChatMessage = {
        id: 'welcome',
        type: 'assistant',
        content: '¡Hola! Soy tu asistente legal. Puedes hacerme consultas por texto, voz o subir documentos. ¿En qué puedo ayudarte?',
        timestamp: new Date()
      }
      setCurrentMessages([welcomeMessage])
      
      return sessionWithDates
    } catch (error) {
      console.error('Error creating new session:', error)
    }
  }, [])

  const addMessage = useCallback(async (message: Omit<ChatMessage, 'id' | 'timestamp'>, sessionId?: string) => {
    const targetSessionId = sessionId || currentSessionId
    
    if (!targetSessionId) {
      console.error('addMessage called without sessionId - this should not happen')
      return
    }

    try {
      const newMessage = await apiClient.addChatMessage(targetSessionId, {
        type: message.type,
        content: message.content,
        audio_url: message.audioUrl,
        transcription: message.transcription,
        audio_transcription: message.audioTranscription,
        sources: message.sources,
        confidence: message.confidence,
        area: message.area
      })
      
      // Convert date string to Date object and snake_case to camelCase
      const messageWithDate = {
        ...newMessage,
        audioUrl: newMessage.audio_url, // Convert snake_case to camelCase
        audioTranscription: newMessage.audio_transcription,
        timestamp: new Date(newMessage.timestamp)
      }
      
      // Add to current messages (UI only)
      setCurrentMessages(prev => [...prev, messageWithDate])

      // Update sessions metadata locally instead of reloading
      setSessions(prev => prev.map(session => 
        session.id === targetSessionId 
          ? { ...session, messageCount: session.messageCount + 1, updatedAt: new Date() }
          : session
      ))

      return messageWithDate
    } catch (error) {
      console.error('Error adding message:', error)
    }
  }, [currentSessionId, createNewSession])

  const updateMessage = useCallback(async (messageId: string, updates: Partial<ChatMessage>, sessionId?: string) => {
    const targetSessionId = sessionId || currentSessionId
    
    if (!targetSessionId) {
      console.error('updateMessage called without sessionId')
      return
    }

    // Update locally first for immediate UI feedback
    setCurrentMessages(prev => prev.map(msg => 
      msg.id === messageId ? { ...msg, ...updates } : msg
    ))

    // Then persist to backend
    try {
      // Only send fields that have values
      const updateData: any = {}
      if (updates.type !== undefined) updateData.type = updates.type
      if (updates.content !== undefined) updateData.content = updates.content
      if (updates.audioUrl !== undefined) updateData.audio_url = updates.audioUrl
      if (updates.transcription !== undefined) updateData.transcription = updates.transcription
      if (updates.audioTranscription !== undefined) updateData.audio_transcription = updates.audioTranscription
      if (updates.sources !== undefined) updateData.sources = updates.sources
      if (updates.confidence !== undefined) updateData.confidence = updates.confidence
      if (updates.area !== undefined) updateData.area = updates.area
      
      await apiClient.updateChatMessage(targetSessionId, messageId, updateData)
      console.log(`✅ Message ${messageId} updated successfully in backend`)
    } catch (error) {
      console.error('❌ Error updating message in backend:', error)
      // Could implement retry logic or show error to user
    }
  }, [currentSessionId])

  const switchToSession = useCallback(async (sessionId: string) => {
    // Prevent multiple simultaneous calls
    if (isLoadingSession || currentSessionId === sessionId) {
      console.log(`⏭️ Skipping session switch - already loading or same session: ${sessionId}`)
      return
    }

    try {
      setIsLoadingSession(true)
      
      const messages = await apiClient.getChatMessages(sessionId)
      
      if (!messages || messages.length === 0) {
        setCurrentSessionId(sessionId)
        setCurrentMessages([])
        setIsLoadingSession(false)
        return
      }
      
      // Convert date strings to Date objects and snake_case to camelCase
      const messagesWithDates = messages.map(message => ({
        ...message,
        audioUrl: message.audio_url, // Convert snake_case to camelCase
        audioTranscription: message.audio_transcription,
        timestamp: new Date(message.timestamp)
      }))
      
      // Set both state updates in a single batch
      setCurrentSessionId(sessionId)
      setCurrentMessages(messagesWithDates)
      
    } catch (error) {
      console.error('❌ Error loading session messages:', error)
      console.error('Error details:', error)
      setCurrentSessionId(sessionId)
      setCurrentMessages([])
    } finally {
      setIsLoadingSession(false)
    }
  }, [isLoadingSession, currentSessionId])

  const deleteSession = useCallback(async (sessionId: string) => {
    try {
      await apiClient.deleteChatSession(sessionId)
      setSessions(prev => prev.filter(s => s.id !== sessionId))
      
      if (currentSessionId === sessionId) {
        const remainingSessions = sessions.filter(s => s.id !== sessionId)
        setCurrentSessionId(remainingSessions.length > 0 ? remainingSessions[0]?.id || null : null)
        setCurrentMessages([])
      }
    } catch (error) {
      console.error('Error deleting session:', error)
    }
  }, [sessions, currentSessionId])

  const clearAllSessions = useCallback(() => {
    setSessions([])
    setCurrentSessionId(null)
    setCurrentMessages([])
  }, [])


  return {
    sessions,
    currentSessionId,
    currentMessages,
    isLoadingSession,
    createNewSession,
    addMessage,
    updateMessage,
    switchToSession,
    deleteSession,
    clearAllSessions
  }
}
