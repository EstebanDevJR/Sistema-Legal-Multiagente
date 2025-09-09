"""
Servicio de memoria para conversaciones de chat
"""

import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ChatMemoryService:
    """Servicio para mantener memoria de conversaciones"""
    
    def __init__(self):
        # En producción, esto debería ser una base de datos
        self.memory_store: Dict[str, Dict[str, Any]] = {}
        self.max_messages_per_session = 20
        self.session_ttl_hours = 24
    
    def get_session_memory(self, session_id: str) -> List[Dict[str, Any]]:
        """Obtener memoria de una sesión específica"""
        if session_id not in self.memory_store:
            return []
        
        session = self.memory_store[session_id]
        
        # Verificar si la sesión ha expirado
        if self._is_session_expired(session):
            del self.memory_store[session_id]
            return []
        
        return session.get("messages", [])
    
    def add_message(self, session_id: str, message: Dict[str, Any]) -> None:
        """Agregar mensaje a la memoria de una sesión"""
        if session_id not in self.memory_store:
            self.memory_store[session_id] = {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "messages": []
            }
        
        session = self.memory_store[session_id]
        session["last_updated"] = datetime.now().isoformat()
        
        # Agregar mensaje
        message_with_timestamp = {
            **message,
            "timestamp": datetime.now().isoformat()
        }
        
        session["messages"].append(message_with_timestamp)
        
        # Mantener solo los últimos N mensajes
        if len(session["messages"]) > self.max_messages_per_session:
            session["messages"] = session["messages"][-self.max_messages_per_session:]
        
        logger.info(f"Added message to session {session_id}. Total messages: {len(session['messages'])}")
    
    def get_conversation_context(self, session_id: str, max_messages: int = 10) -> str:
        """Obtener contexto de conversación para el LLM"""
        messages = self.get_session_memory(session_id)
        
        if not messages:
            return ""
        
        # Tomar los últimos N mensajes
        recent_messages = messages[-max_messages:]
        
        context_parts = []
        for msg in recent_messages:
            role = "Usuario" if msg.get("type") == "user" else "Asistente"
            content = msg.get("content", "")
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    def _is_session_expired(self, session: Dict[str, Any]) -> bool:
        """Verificar si una sesión ha expirado"""
        last_updated = datetime.fromisoformat(session["last_updated"])
        expiry_time = last_updated + timedelta(hours=self.session_ttl_hours)
        return datetime.now() > expiry_time
    
    def cleanup_expired_sessions(self) -> int:
        """Limpiar sesiones expiradas"""
        expired_sessions = []
        for session_id, session in self.memory_store.items():
            if self._is_session_expired(session):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.memory_store[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de las sesiones"""
        total_sessions = len(self.memory_store)
        total_messages = sum(len(session.get("messages", [])) for session in self.memory_store.values())
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "max_messages_per_session": self.max_messages_per_session,
            "session_ttl_hours": self.session_ttl_hours
        }

# Instancia global del servicio
chat_memory_service = ChatMemoryService()
