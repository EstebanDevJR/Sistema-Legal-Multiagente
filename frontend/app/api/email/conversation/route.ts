import { NextRequest, NextResponse } from 'next/server'
import { ChatMessage } from '@/hooks/use-chat-memory'

interface EmailRequest {
  email: string
  messages: ChatMessage[]
  sessionTitle: string
}

export async function POST(request: NextRequest) {
  try {
    const body: EmailRequest = await request.json()
    const { email, messages, sessionTitle } = body

    // Validar email
    if (!email || !email.includes('@')) {
      return NextResponse.json(
        { error: 'Email inválido' },
        { status: 400 }
      )
    }

    // Validar que hay mensajes
    if (!messages || messages.length === 0) {
      return NextResponse.json(
        { error: 'No hay mensajes para enviar' },
        { status: 400 }
      )
    }

    // Llamar al backend de Python para enviar el email (usando endpoint flexible para debug)
    const backendResponse = await fetch('http://localhost:8000/email/send-conversation-flexible', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        recipient_email: email,
        messages: messages,
        session_title: sessionTitle,
        timestamp: new Date().toISOString()
      }),
    }).catch(error => {
      console.error('Network error calling backend:', error)
      throw new Error('No se pudo conectar con el servidor de email')
    })

    if (!backendResponse.ok) {
      const errorData = await backendResponse.json().catch(() => ({}))
      throw new Error(errorData.message || 'Error en el servidor')
    }

    const result = await backendResponse.json()

    return NextResponse.json({
      success: true,
      message: 'Email enviado exitosamente',
      data: result
    })

  } catch (error) {
    console.error('Error sending email:', error)
    return NextResponse.json(
      { 
        error: 'Error interno del servidor',
        details: error instanceof Error ? error.message : 'Error desconocido'
      },
      { status: 500 }
    )
  }
}
