"use client"

import { useState } from "react"
import Header from "@/components/header"
import ChatInterface from "@/components/chat-interface"
import ChatSidebar from "@/components/chat-sidebar"
import ShaderBackground from "@/components/shader-background"
import AccessibilitySkipLinks from "@/components/accessibility-skip-links"
import { ChatMemoryProvider } from "@/contexts/ChatMemoryContext"

export default function ChatPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <ChatMemoryProvider>
      <ShaderBackground>
        <AccessibilitySkipLinks />
        
        <Header />
        
        <main className="flex flex-1 relative z-10">
          {/* Sidebar */}
          <div className={`transition-all duration-300 ${sidebarOpen ? 'w-80' : 'w-0'} flex-shrink-0 overflow-hidden relative`}>
            <ChatSidebar 
              onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
              sidebarOpen={sidebarOpen}
            />
          </div>
          
          {/* Toggle button area when sidebar is closed */}
          {!sidebarOpen && (
            <div className="w-8 h-full bg-white/10 hover:bg-white/20 transition-colors cursor-pointer z-40 flex-shrink-0 flex items-center justify-center" 
                 onClick={() => setSidebarOpen(true)}
                 title="Mostrar conversaciones">
              <div className="w-1 h-16 bg-white/40 rounded-full"></div>
            </div>
          )}

          {/* Chat Interface */}
          <div className="flex-1 flex flex-col relative">
            <ChatInterface />
          </div>
        </main>
      </ShaderBackground>
    </ChatMemoryProvider>
  )
}
