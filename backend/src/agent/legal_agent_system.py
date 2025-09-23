"""
Sistema multiagente para consultas legales colombianas - Refactorizado
Especializado en: Civil, Comercial, Laboral y Tributario
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI

from .types import AgentState, ModelConfig
from .conversation_memory import ConversationMemoryService
from .specialized_agents import LegalAgentFactory
from .workflow_nodes import WorkflowNodes
from .graph_builder import LegalAgentGraphBuilder

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LegalAgentSystem:
    """Sistema multiagente para consultas legales - Versión refactorizada"""
    
    def __init__(
        self, 
        model_name: str = "gpt-4o-mini", 
        temperature: float = 0.1, 
        max_tokens: int = 1500
    ):
        # Configuración del modelo
        self.model_config = ModelConfig(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Instancia única del modelo para reutilizar
        self.model = ChatOpenAI(
            model=self.model_config.model,
            temperature=self.model_config.temperature,
            max_tokens=self.model_config.max_tokens
        )
        
        # Servicios
        self.memory_service = ConversationMemoryService()
        
        # Inicializar agentes
        self.agent_factory = LegalAgentFactory(self.model)
        self.agents = self._initialize_agents()
        
        # Crear workflow nodes
        self.workflow_nodes = WorkflowNodes(self.agents, self.memory_service)
        
        # Crear grafo
        graph_builder = LegalAgentGraphBuilder(self.workflow_nodes)
        self.graph = graph_builder.build_graph()
        
        logger.info("Sistema multiagente inicializado correctamente")
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """Inicializar todos los agentes"""
        return {
            "coordinator": self.agent_factory.create_coordinator_agent(),
            "document_analysis": self.agent_factory.create_document_analysis_agent(),
            "civil": self.agent_factory.create_civil_agent(),
            "comercial": self.agent_factory.create_comercial_agent(),
            "laboral": self.agent_factory.create_laboral_agent(),
            "tributario": self.agent_factory.create_tributario_agent(),
            "constitucional": self.agent_factory.create_constitucional_agent(),
            "administrativo": self.agent_factory.create_administrativo_agent(),
            "evaluator": self.agent_factory.create_evaluator_agent()
        }
    
    async def process_query(
        self,
        question: str,
        context: str = "",
        sources: List[Dict[str, Any]] = None,
        user_id: str = "default",
        session_id: str = None,
        conversation_context: str = ""  # Deprecated, usar session_id
    ) -> Dict[str, Any]:
        """
        Procesar consulta legal a través del sistema multiagente
        
        Args:
            question: Pregunta del usuario
            context: Contexto de documentos relevantes
            sources: Lista de fuentes documentales
            user_id: ID del usuario para seguimiento
            session_id: ID de sesión para memoria de conversación
            conversation_context: Contexto de conversación anterior (deprecated)
            
        Returns:
            Respuesta procesada por el sistema multiagente
        """
        # Validaciones de entrada
        if not question or not question.strip():
            logger.error("Pregunta vacía recibida")
            return self._create_error_response("Por favor, proporciona una pregunta válida.")
        
        # Generar session_id si no se proporciona
        if not session_id:
            session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Detectar si hay documentos específicos del usuario
        has_specific_docs = any(
            source.get("metadata", {}).get("source") == "user_upload" 
            for source in (sources or [])
        )
        
        logger.info(f"🚀 Iniciando procesamiento de consulta para usuario {user_id}, sesión {session_id}")
        logger.info(f"📝 Pregunta: {question[:100]}{'...' if len(question) > 100 else ''}")
        logger.info(f"📄 Documentos específicos: {'Sí' if has_specific_docs else 'No'}")
        
        # Estado inicial
        initial_state = self._create_initial_state(
            question, context, sources, user_id, session_id, 
            conversation_context, has_specific_docs
        )
        
        # Configuración de thread para memoria persistente de LangGraph
        config = {"configurable": {"thread_id": f"legal_query_{session_id}"}}
        
        try:
            # Ejecutar el grafo
            result = await self.graph.ainvoke(initial_state, config=config)
            
            logger.info(f"✅ Consulta procesada exitosamente con confianza {result['confidence']}")
            
            return self._format_final_response(result, session_id)
            
        except Exception as e:
            logger.error(f"❌ Error procesando consulta: {e}")
            return self._create_error_response(
                "Lo siento, ocurrió un error procesando tu consulta. Por favor, intenta nuevamente.",
                session_id=session_id,
                user_id=user_id,
                error=str(e)
            )
    
    def _create_initial_state(
        self,
        question: str,
        context: str,
        sources: List[Dict[str, Any]],
        user_id: str,
        session_id: str,
        conversation_context: str,
        has_specific_docs: bool
    ) -> AgentState:
        """Crear estado inicial para el procesamiento"""
        default_sources = [{
            "title": "Legislación Colombiana", 
            "content": "Documentos legales del sistema", 
            "relevance": 1.0, 
            "filename": "legislacion_colombiana", 
            "metadata": {}
        }]
        
        return AgentState(
            question=question.strip(),
            context=context or "Legislación colombiana aplicable.",
            sources=sources or default_sources,
            legal_area="",
            complexity="",
            responses={},
            final_answer="",
            confidence=0.0,
            suggestions=[],
            metadata={
                "user_id": user_id,
                "conversation_context": conversation_context,
                "timestamp": datetime.now().isoformat(),
                "session_start": datetime.now().isoformat()
            },
            has_specific_documents=has_specific_docs,
            conversation_history=[],
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
    
    def _format_final_response(self, result: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Formatear respuesta final"""
        return {
            "answer": result["final_answer"],
            "confidence": result["confidence"],
            "legal_area": result.get("legal_area", "general"),
            "complexity": result.get("complexity", "medium"),
            "sources": result.get("sources", []),
            "suggestions": result.get("suggestions", []),
            "metadata": {
                **result.get("metadata", {}),
                "session_id": session_id,
                "processing_time": datetime.now().isoformat(),
                "has_conversation_history": len(self.memory_service.conversation_cache.get(session_id, [])) > 0
            }
        }
    
    def _create_error_response(
        self, 
        message: str, 
        session_id: str = None, 
        user_id: str = "default", 
        error: str = None
    ) -> Dict[str, Any]:
        """Crear respuesta de error estandarizada"""
        return {
            "answer": message,
            "confidence": 0.0,
            "legal_area": "error",
            "complexity": "simple",
            "sources": [],
            "suggestions": [
                "Intenta reformular tu pregunta",
                "Verifica que la información esté completa",
                "Contacta soporte si el problema persiste"
            ],
            "metadata": {
                "error": error or "unknown_error",
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "user_id": user_id
            }
        }
    
    # Métodos de gestión de memoria
    def clear_conversation_history(self, session_id: str) -> bool:
        """Limpiar historial de conversación para una sesión específica"""
        return self.memory_service.clear_conversation_history(session_id)
    
    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Obtener resumen del historial de conversación"""
        return self.memory_service.get_conversation_summary(session_id)


# Instancia global del sistema
legal_agent_system = LegalAgentSystem()
