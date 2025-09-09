"""
API para envío de emails con conversaciones
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formatdate
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email", tags=["Email Services"])

class ChatMessage(BaseModel):
    id: str
    type: str  # 'user' | 'assistant'
    content: str
    timestamp: str
    audioUrl: Optional[str] = None
    audio_url: Optional[str] = None  # Para compatibilidad
    transcription: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = []
    confidence: Optional[float] = None
    area: Optional[str] = None
    
    class Config:
        # Permitir campos extra para flexibilidad
        extra = "ignore"

class SendConversationRequest(BaseModel):
    recipient_email: EmailStr
    messages: List[ChatMessage]
    session_title: str
    timestamp: str

def create_email_template(messages: List[ChatMessage], session_title: str, timestamp: str) -> str:
    """Crear template HTML para el email"""
    
    # Formatear fecha
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        formatted_date = dt.strftime("%d de %B de %Y a las %H:%M")
    except:
        formatted_date = datetime.now().strftime("%d de %B de %Y a las %H:%M")
    
    # Contar mensajes
    user_messages = len([m for m in messages if m.type == 'user'])
    assistant_messages = len([m for m in messages if m.type == 'assistant'])
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{session_title}</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f8fafc;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 12px;
                text-align: center;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header h1 {{
                margin: 0 0 10px 0;
                font-size: 28px;
                font-weight: 700;
            }}
            .header p {{
                margin: 0;
                opacity: 0.9;
                font-size: 16px;
            }}
            .stats {{
                display: flex;
                justify-content: space-around;
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            .stat {{
                text-align: center;
            }}
            .stat-number {{
                font-size: 24px;
                font-weight: bold;
                color: #667eea;
                display: block;
            }}
            .stat-label {{
                font-size: 14px;
                color: #64748b;
                margin-top: 5px;
            }}
            .conversation {{
                background: white;
                border-radius: 12px;
                padding: 0;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            .message {{
                padding: 20px;
                border-bottom: 1px solid #e2e8f0;
            }}
            .message:last-child {{
                border-bottom: none;
            }}
            .message-user {{
                background-color: #f1f5f9;
                border-left: 4px solid #667eea;
            }}
            .message-assistant {{
                background-color: #ffffff;
                border-left: 4px solid #10b981;
            }}
            .message-header {{
                display: flex;
                align-items: center;
                margin-bottom: 12px;
            }}
            .message-avatar {{
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                color: white;
                margin-right: 12px;
                font-size: 14px;
            }}
            .avatar-user {{
                background-color: #667eea;
            }}
            .avatar-assistant {{
                background-color: #10b981;
            }}
            .message-time {{
                font-size: 12px;
                color: #64748b;
                margin-left: auto;
            }}
            .message-content {{
                font-size: 15px;
                line-height: 1.6;
                white-space: pre-wrap;
            }}
            .message-meta {{
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid #e2e8f0;
            }}
            .confidence {{
                display: inline-block;
                background-color: #f0f9ff;
                color: #0369a1;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
                margin-right: 8px;
            }}
            .area {{
                display: inline-block;
                background-color: #f0fdf4;
                color: #166534;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
            }}
            .sources {{
                margin-top: 10px;
            }}
            .source {{
                font-size: 12px;
                color: #64748b;
                background-color: #f8fafc;
                padding: 6px 10px;
                border-radius: 4px;
                margin: 4px 0;
                border-left: 2px solid #cbd5e1;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding: 20px;
                color: #64748b;
                font-size: 14px;
            }}
            .footer a {{
                color: #667eea;
                text-decoration: none;
            }}
            .audio-note {{
                background-color: #fef3c7;
                color: #92400e;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 13px;
                margin-top: 10px;
                display: inline-block;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>⚖️ {session_title}</h1>
            <p>Conversación generada el {formatted_date}</p>
        </div>
        
        <div class="stats">
            <div class="stat">
                <span class="stat-number">{len(messages)}</span>
                <div class="stat-label">Total mensajes</div>
            </div>
            <div class="stat">
                <span class="stat-number">{user_messages}</span>
                <div class="stat-label">Consultas</div>
            </div>
            <div class="stat">
                <span class="stat-number">{assistant_messages}</span>
                <div class="stat-label">Respuestas</div>
            </div>
        </div>
        
        <div class="conversation">
    """
    
    # Agregar mensajes
    for i, message in enumerate(messages):
        # Formatear timestamp del mensaje
        try:
            msg_dt = datetime.fromisoformat(message.timestamp.replace('Z', '+00:00'))
            msg_time = msg_dt.strftime("%H:%M")
        except:
            msg_time = "00:00"
        
        avatar_class = "avatar-user" if message.type == 'user' else "avatar-assistant"
        message_class = "message-user" if message.type == 'user' else "message-assistant"
        avatar_text = "👤" if message.type == 'user' else "🤖"
        sender_name = "Usuario" if message.type == 'user' else "Asistente Legal"
        
        html_content += f"""
            <div class="message {message_class}">
                <div class="message-header">
                    <div class="message-avatar {avatar_class}">{avatar_text}</div>
                    <strong>{sender_name}</strong>
                    <span class="message-time">{msg_time}</span>
                </div>
                <div class="message-content">{message.content}</div>
        """
        
        # Agregar metadatos si es un mensaje del asistente
        if message.type == 'assistant':
            meta_items = []
            
            if message.confidence:
                confidence_percent = int(message.confidence * 100)
                meta_items.append(f'<span class="confidence">Confianza: {confidence_percent}%</span>')
            
            if message.area:
                meta_items.append(f'<span class="area">Área: {message.area}</span>')
            
            if meta_items:
                html_content += f'<div class="message-meta">{"".join(meta_items)}</div>'
            
            # Agregar fuentes si las hay
            if message.sources:
                html_content += '<div class="sources">'
                for j, source in enumerate(message.sources[:3]):  # Máximo 3 fuentes
                    source_title = source.get('title', source.get('source', f'Fuente {j+1}'))
                    html_content += f'<div class="source">📄 {source_title}</div>'
                html_content += '</div>'
        
        # Nota de audio si existe
        if message.audioUrl:
            html_content += '<div class="audio-note">🔊 Esta respuesta incluía audio</div>'
        
        html_content += '</div>'
    
    # Footer
    html_content += f"""
        </div>
        
        <div class="footer">
            <p>Este email fue generado automáticamente por el <strong>Sistema Legal Multiagente</strong></p>
            <p>Desarrollado con ❤️ por <a href="https://linkedin.com/in/esteban-ortiz">Esteban Ortiz</a></p>
            <p style="margin-top: 20px; font-size: 12px; color: #94a3b8;">
                📧 Para consultas adicionales, puedes continuar tu conversación en nuestra plataforma web.
            </p>
        </div>
    </body>
    </html>
    """
    
    return html_content

@router.post("/send-conversation-flexible")
async def send_conversation_flexible(request_data: dict):
    """
    Enviar conversación por email (versión flexible para debugging)
    """
    try:
        # Extraer datos manualmente para mejor control
        recipient_email = request_data.get('recipient_email')
        messages_raw = request_data.get('messages', [])
        session_title = request_data.get('session_title', 'Conversación Legal')
        timestamp = request_data.get('timestamp', datetime.now().isoformat())
        
        logger.info(f"📧 Flexible sending conversation to {recipient_email}")
        logger.info(f"📊 Request data: session_title='{session_title}', messages_count={len(messages_raw)}")
        
        # Debug: Verificar configuración SMTP
        SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
        SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        SENDER_EMAIL = os.getenv("SENDER_EMAIL", "noreply@legalsystem.com")
        SENDER_NAME = os.getenv("SENDER_NAME", "Sistema Legal Multiagente")
        
        logger.info(f"🔧 SMTP Debug - Server: {SMTP_SERVER}:{SMTP_PORT}")
        logger.info(f"🔧 SMTP Debug - Sender: {SENDER_EMAIL}")
        logger.info(f"🔧 SMTP Debug - Name: {SENDER_NAME}")
        logger.info(f"🔧 SMTP Debug - Has Password: {bool(SENDER_PASSWORD)} (length: {len(SENDER_PASSWORD) if SENDER_PASSWORD else 0})")
        
        # Validar datos esenciales
        if not recipient_email or '@' not in recipient_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email inválido o faltante"
            )
        
        if not messages_raw:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay mensajes para enviar"
            )
        
        # Convertir mensajes a objetos simples para el template
        messages_for_template = []
        for msg in messages_raw:
            clean_msg = {
                'id': msg.get('id', ''),
                'type': msg.get('type', 'user'),
                'content': msg.get('content', ''),
                'timestamp': msg.get('timestamp', timestamp),
                'audioUrl': msg.get('audioUrl') or msg.get('audio_url'),
                'transcription': msg.get('transcription'),
                'sources': msg.get('sources', []),
                'confidence': msg.get('confidence'),
                'area': msg.get('area')
            }
            messages_for_template.append(clean_msg)
        
        # Para desarrollo, simular envío si no hay contraseña
        if not SENDER_PASSWORD:
            logger.warning("⚠️ SMTP not configured, simulating email send")
            
            import asyncio
            await asyncio.sleep(1)
            
            return {
                "success": True,
                "message": "Email simulado enviado exitosamente (modo desarrollo)",
                "recipient": recipient_email,
                "messages_count": len(messages_for_template),
                "note": "Este es un envío simulado. Configura SMTP para envíos reales."
            }
        
        # Envío SMTP real
        logger.info("📧 Iniciando envío SMTP real...")
        
        try:
            # Generar contenido HTML del email
            # Convertir diccionarios a objetos ChatMessage
            chat_messages = []
            for msg in messages_for_template:
                try:
                    chat_msg = ChatMessage(
                        id=msg.get('id', ''),
                        type=msg.get('type', 'user'),
                        content=msg.get('content', ''),
                        timestamp=msg.get('timestamp', timestamp),
                        audioUrl=msg.get('audioUrl'),
                        transcription=msg.get('transcription'),
                        sources=msg.get('sources', []),
                        confidence=msg.get('confidence'),
                        area=msg.get('area')
                    )
                    chat_messages.append(chat_msg)
                except Exception as e:
                    logger.warning(f"⚠️ Error converting message {msg.get('id', 'unknown')}: {e}")
                    continue
            
            html_content = create_email_template(
                messages=chat_messages,
                session_title=session_title,
                timestamp=timestamp
            )
            
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"📧 {session_title}"
            msg['From'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
            msg['To'] = recipient_email
            msg['Date'] = formatdate(localtime=True)
            
            # Contenido de texto plano
            text_content = f"""
{session_title}

Conversación generada el {timestamp}

"""
            for message in messages_for_template:
                sender = "Usuario" if message['type'] == 'user' else "Asistente Legal"
                text_content += f"{sender}: {message['content']}\n\n"
            
            text_content += "\n---\nEste email fue generado por el Sistema Legal Multiagente"
            
            # Adjuntar contenido
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Enviar email
            logger.info(f"🔗 Conectando a {SMTP_SERVER}:{SMTP_PORT}...")
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                logger.info("🔒 Iniciando TLS...")
                server.starttls()
                logger.info(f"🔑 Autenticando con {SENDER_EMAIL}...")
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                logger.info(f"📤 Enviando email a {recipient_email}...")
                server.send_message(msg)
            
            logger.info(f"✅ Email sent successfully to {recipient_email}")
            
            return {
                "success": True,
                "message": "Email enviado exitosamente",
                "recipient": recipient_email,
                "messages_count": len(messages_for_template),
                "timestamp": timestamp
            }
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ SMTP Authentication Error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Error de autenticación SMTP. Verifica las credenciales."
            )
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP Error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error SMTP: {str(e)}"
            )
        except Exception as e:
            logger.error(f"❌ Unexpected error sending email: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error inesperado al enviar email: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in flexible send conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar email: {str(e)}"
        )

@router.post("/send-conversation")
async def send_conversation(request: SendConversationRequest):
    """
    Enviar conversación por email
    """
    try:
        logger.info(f"📧 Sending conversation to {request.recipient_email}")
        logger.info(f"📊 Request data: session_title='{request.session_title}', messages_count={len(request.messages)}")
        logger.debug(f"📝 Full request: {request.dict()}")
        
        # Configuración del servidor SMTP (usar variables de entorno en producción)
        SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        SENDER_EMAIL = os.getenv("SENDER_EMAIL", "noreply@legalsystem.com")
        SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
        SENDER_NAME = os.getenv("SENDER_NAME", "Sistema Legal Multiagente")
        
        # Para desarrollo, simular envío exitoso si no hay configuración SMTP
        if not SENDER_PASSWORD:
            logger.warning("⚠️ SMTP not configured, simulating email send")
            
            # Simular un pequeño delay para hacer más realista
            import asyncio
            await asyncio.sleep(1)
            
            return {
                "success": True,
                "message": "Email simulado enviado exitosamente (modo desarrollo)",
                "recipient": request.recipient_email,
                "messages_count": len(request.messages),
                "note": "Este es un envío simulado. Configura SMTP para envíos reales."
            }
        
        # Crear el mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"📋 {request.session_title}"
        msg['From'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        msg['To'] = request.recipient_email
        
        # Crear contenido HTML
        html_content = create_email_template(
            request.messages, 
            request.session_title, 
            request.timestamp
        )
        
        # Crear texto plano como fallback
        text_content = f"""
{request.session_title}

Conversación generada el {request.timestamp}

"""
        for message in request.messages:
            sender = "Usuario" if message.type == 'user' else "Asistente Legal"
            text_content += f"{sender}: {message.content}\n\n"
        
        text_content += "\n---\nEste email fue generado por el Sistema Legal Multiagente"
        
        # Adjuntar contenido
        text_part = MIMEText(text_content, 'plain', 'utf-8')
        html_part = MIMEText(html_content, 'html', 'utf-8')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Enviar email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"✅ Email sent successfully to {request.recipient_email}")
        
        return {
            "success": True,
            "message": "Email enviado exitosamente",
            "recipient": request.recipient_email,
            "messages_count": len(request.messages),
            "timestamp": request.timestamp
        }
        
    except Exception as e:
        logger.error(f"❌ Error sending email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar email: {str(e)}"
        )

@router.post("/debug")
async def debug_email_request(request_data: dict):
    """Debug endpoint para ver qué datos llegan"""
    try:
        logger.info("🐛 Debug email request received")
        logger.info(f"📊 Raw data keys: {list(request_data.keys())}")
        logger.info(f"📧 Recipient email: {request_data.get('recipient_email')}")
        logger.info(f"📝 Session title: {request_data.get('session_title')}")
        logger.info(f"📅 Timestamp: {request_data.get('timestamp')}")
        
        messages = request_data.get('messages', [])
        logger.info(f"💬 Messages count: {len(messages)}")
        
        if messages:
            first_msg = messages[0]
            logger.info(f"📄 First message keys: {list(first_msg.keys())}")
            logger.info(f"📄 First message sample: {first_msg}")
        
        return {
            "status": "debug_success",
            "received_keys": list(request_data.keys()),
            "messages_count": len(messages),
            "first_message_keys": list(messages[0].keys()) if messages else [],
            "data_sample": {
                "recipient_email": request_data.get('recipient_email'),
                "session_title": request_data.get('session_title'),
                "timestamp": request_data.get('timestamp')
            }
        }
    except Exception as e:
        logger.error(f"❌ Debug endpoint error: {e}")
        return {"status": "debug_error", "error": str(e)}

@router.get("/test")
async def test_email_service():
    """Test endpoint para verificar el servicio de email"""
    try:
        smtp_configured = bool(os.getenv("SENDER_PASSWORD"))
        
        return {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "smtp_configured": smtp_configured,
            "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            "sender_email": os.getenv("SENDER_EMAIL", "noreply@legalsystem.com"),
            "mode": "production" if smtp_configured else "development",
            "message": "Servicio de email funcionando correctamente" + (" (modo simulación)" if not smtp_configured else "")
        }
    except Exception as e:
        logger.error(f"Error in email test endpoint: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
