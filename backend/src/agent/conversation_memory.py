"""
Servicio de memoria de conversación para el sistema multiagente legal
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ConversationMemoryService:
    """Servicio para manejar la memoria de conversaciones"""
    
    def __init__(self, max_history_per_session: int = 20):
        self.conversation_cache: Dict[str, List[Dict[str, Any]]] = {}
        self.max_history_per_session = max_history_per_session
    
    def get_conversation_context(self, session_id: str, max_history: int = 5) -> str:
        """Obtener contexto de conversación anterior"""
        try:
            if session_id not in self.conversation_cache:
                return "Nueva conversación iniciada."
            
            history = self.conversation_cache[session_id][-max_history:]
            context_parts = []
            
            for i, exchange in enumerate(history, 1):
                context_parts.append(f"Intercambio {i}:")
                context_parts.append(f"Pregunta: {exchange['question']}")
                context_parts.append(f"Respuesta: {exchange['answer'][:200]}...")
                context_parts.append(f"Área legal: {exchange.get('legal_area', 'N/A')}")
                context_parts.append("---")
            
            return "\n".join(context_parts)
        except Exception as e:
            logger.error(f"Error obteniendo contexto de conversación: {e}")
            return "Error al recuperar historial de conversación."
    
    def save_conversation_exchange(
        self, 
        session_id: str, 
        question: str, 
        answer: str, 
        legal_area: str, 
        metadata: Dict[str, Any]
    ) -> None:
        """Guardar intercambio de conversación en cache"""
        try:
            if session_id not in self.conversation_cache:
                self.conversation_cache[session_id] = []
            
            exchange = {
                "timestamp": datetime.now().isoformat(),
                "question": question,
                "answer": answer,
                "legal_area": legal_area,
                "metadata": metadata
            }
            
            self.conversation_cache[session_id].append(exchange)
            
            # Mantener solo los últimos intercambios para evitar memoria excesiva
            if len(self.conversation_cache[session_id]) > self.max_history_per_session:
                self.conversation_cache[session_id] = (
                    self.conversation_cache[session_id][-self.max_history_per_session:]
                )
                
            logger.info(f"Intercambio guardado para sesión {session_id}")
        except Exception as e:
            logger.error(f"Error guardando intercambio: {e}")
    
    def clear_conversation_history(self, session_id: str) -> bool:
        """Limpiar historial de conversación para una sesión específica"""
        try:
            if session_id in self.conversation_cache:
                del self.conversation_cache[session_id]
                logger.info(f"🧹 Historial de conversación limpiado para sesión {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error limpiando historial: {e}")
            return False
    
    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Obtener resumen del historial de conversación"""
        try:
            if session_id not in self.conversation_cache:
                return {"exchanges": 0, "topics": [], "last_activity": None}
            
            history = self.conversation_cache[session_id]
            topics = list(set([exchange.get("legal_area", "general") for exchange in history]))
            
            return {
                "exchanges": len(history),
                "topics": topics,
                "last_activity": history[-1]["timestamp"] if history else None,
                "session_id": session_id
            }
        except Exception as e:
            logger.error(f"Error obteniendo resumen: {e}")
            return {"error": str(e)}
