"use client"

import React, { createContext, useContext, ReactNode } from 'react'
import { useChatMemory } from '@/hooks/use-chat-memory'

// Create the context
const ChatMemoryContext = createContext<ReturnType<typeof useChatMemory> | null>(null)

// Provider component
export function ChatMemoryProvider({ children }: { children: ReactNode }) {
  const chatMemory = useChatMemory()
  
  return (
    <ChatMemoryContext.Provider value={chatMemory}>
      {children}
    </ChatMemoryContext.Provider>
  )
}

// Custom hook to use the context
export function useChatMemoryContext() {
  const context = useContext(ChatMemoryContext)
  if (!context) {
    throw new Error('useChatMemoryContext must be used within a ChatMemoryProvider')
  }
  return context
}
