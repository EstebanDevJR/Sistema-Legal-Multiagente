"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import { X, Mail, Send, CheckCircle } from "lucide-react"
import { ChatMessage } from "@/hooks/use-chat-memory"

interface EmailConversationModalProps {
  isOpen: boolean
  onClose: () => void
  messages: ChatMessage[]
  sessionTitle?: string
}

export default function EmailConversationModal({ 
  isOpen, 
  onClose, 
  messages, 
  sessionTitle = "Conversación Legal" 
}: EmailConversationModalProps) {
  const [email, setEmail] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isSent, setIsSent] = useState(false)
  const [isTestingConnection, setIsTestingConnection] = useState(false)
  const { toast } = useToast()

  const testConnection = async () => {
    setIsTestingConnection(true)
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const response = await fetch(`${API_BASE_URL}/email/test`)
      const result = await response.json()
      
      if (response.ok) {
        toast({
          title: "✅ Conexión exitosa",
          description: result.message || "El servicio de email está funcionando",
        })
      } else {
        throw new Error(result.error || "Error en el test")
      }
    } catch (error) {
      console.error('Connection test failed:', error)
      toast({
        title: "❌ Error de conexión",
        description: "No se pudo conectar con el servidor de email. Verifica que el backend esté funcionando correctamente.",
        variant: "destructive"
      })
    } finally {
      setIsTestingConnection(false)
    }
  }


  const handleSendEmail = async () => {
    if (!email.trim()) {
      toast({
        title: "Email requerido",
        description: "Por favor ingresa un email válido",
        variant: "destructive"
      })
      return
    }

    if (!email.includes("@") || !email.includes(".")) {
      toast({
        title: "Email inválido",
        description: "Por favor ingresa un email válido",
        variant: "destructive"
      })
      return
    }

    setIsLoading(true)

    try {
      // Llamada a la API route de Next.js
      const response = await fetch('/api/email/conversation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email,
          messages,
          sessionTitle
        })
      })

      const result = await response.json()

      if (!response.ok) {
        throw new Error(result.error || result.details || 'Error al enviar el email')
      }

      setIsSent(true)
      toast({
        title: "¡Email enviado!",
        description: `Tu conversación ha sido enviada a ${email}`,
      })

      // Cerrar modal después de 2 segundos
      setTimeout(() => {
        onClose()
        setIsSent(false)
        setEmail("")
      }, 2000)

    } catch (error) {
      console.error('Error sending email:', error)
      const errorMessage = error instanceof Error ? error.message : "Error desconocido"
      
      toast({
        title: "Error al enviar",
        description: errorMessage.includes('conectar') 
          ? "No se pudo conectar con el servidor. Verifica que el backend esté ejecutándose."
          : errorMessage,
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleClose = () => {
    if (!isLoading) {
      onClose()
      setEmail("")
      setIsSent(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={handleClose}
      />
      
      {/* Modal */}
      <Card className="relative w-full max-w-md bg-white/10 backdrop-blur-md border-white/20 shadow-2xl">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-600/20 rounded-full flex items-center justify-center">
                <Mail className="w-5 h-5 text-blue-400" />
              </div>
              <CardTitle className="text-white text-lg">
                Enviar Conversación
              </CardTitle>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClose}
              className="text-white/70 hover:text-white hover:bg-white/10"
              disabled={isLoading}
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {!isSent ? (
            <>
              <div>
                <p className="text-white/90 text-sm mb-3">
                  Recibe tu conversación completa por email para consultarla cuando necesites
                </p>
                <div className="space-y-2">
                  <label htmlFor="email" className="text-sm font-medium text-white/90">
                    Email de destino
                  </label>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="tu@email.com"
                    className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent"
                    disabled={isLoading}
                  />
                </div>
              </div>
              
              <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                <div className="text-xs text-white/70 mb-1">Vista previa:</div>
                <div className="text-sm text-white/90">
                  <div className="font-medium">{sessionTitle}</div>
                  <div className="text-xs text-white/70 mt-1">
                    {messages.length} mensaje{messages.length !== 1 ? 's' : ''} • {new Date().toLocaleDateString('es-ES')}
                  </div>
                </div>
              </div>
              
              <div className="flex gap-2 pt-2">
                <Button
                  variant="outline"
                  onClick={testConnection}
                  disabled={isLoading || isTestingConnection}
                  className="border-white/20 text-white/90 hover:bg-white/10 hover:text-white"
                  title="Probar conexión con el servidor"
                >
                  {isTestingConnection ? (
                    <>
                      <div className="w-4 h-4 border-2 border-gray-300 border-t-transparent rounded-full animate-spin mr-2" />
                      Test...
                    </>
                  ) : (
                    "🔗"
                  )}
                </Button>
                <Button
                  onClick={handleSendEmail}
                  disabled={isLoading || !email.trim() || isTestingConnection}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {isLoading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                      Enviando...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4 mr-2" />
                      Enviar
                    </>
                  )}
                </Button>
                <Button
                  variant="outline"
                  onClick={handleClose}
                  className="border-white/20 text-white/90 hover:bg-white/10 hover:text-white"
                  disabled={isLoading || isTestingConnection}
                >
                  ✕
                </Button>
              </div>
            </>
          ) : (
            <div className="text-center py-6">
              <div className="w-16 h-16 bg-green-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-green-400" />
              </div>
              <h3 className="text-white font-medium mb-2">¡Email Enviado!</h3>
              <p className="text-white/90 text-sm">
                Tu conversación ha sido enviada a<br />
                <span className="text-blue-400 font-medium">{email}</span>
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
