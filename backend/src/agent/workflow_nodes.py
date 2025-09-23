"""
Nodos del workflow para el sistema multiagente legal
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

from .types import AgentState, AgentResponse
from .conversation_memory import ConversationMemoryService

logger = logging.getLogger(__name__)


class WorkflowNodes:
    """Contenedor para todos los nodos del workflow"""
    
    def __init__(self, agents: Dict[str, Any], memory_service: ConversationMemoryService):
        self.agents = agents
        self.memory_service = memory_service
    
    def format_sources_for_prompt(self, sources: list) -> str:
        """Formatear fuentes para uso en prompts"""
        if not sources:
            return "No hay fuentes documentales disponibles."
        
        formatted_sources = []
        for i, source in enumerate(sources, 1):
            title = source.get("title", "Documento sin título")
            content = source.get("content", "")
            if len(content) > 150:
                content = content[:150] + "..."
            relevance = source.get("relevance", 0.0)
            
            formatted_sources.append(
                f"{i}. {title} (Relevancia: {relevance:.2f})\n   Contenido: {content}"
            )
        
        return "\n\n".join(formatted_sources)
    
    def coordinator_node(self, state: AgentState) -> AgentState:
        """Nodo coordinador"""
        try:
            session_id = state.get("session_id", "default")
            conversation_context = self.memory_service.get_conversation_context(session_id)
            
            logger.info(f"🎯 Coordinador procesando pregunta: {state['question'][:100]}...")
            
            response = self.agents["coordinator"].invoke({
                "question": state["question"],
                "conversation_context": conversation_context
            })
            
            # Parsear respuesta JSON con manejo de errores mejorado
            if not response.content or not response.content.strip():
                logger.warning("⚠️ Respuesta vacía del coordinador, usando fallback")
                coordination = {
                    "legal_area": "civil",
                    "complexity": "medium", 
                    "requires_multiple_areas": False,
                    "secondary_areas": [],
                    "reasoning": "Respuesta vacía de OpenAI, usando configuración por defecto",
                    "relates_to_previous": False
                }
            else:
                try:
                    coordination = json.loads(response.content)
                except json.JSONDecodeError as json_error:
                    logger.warning(f"⚠️ Error JSON en coordinador: {json_error}")
                    logger.warning(f"📝 Contenido recibido: '{response.content[:200]}...'")
                    # Intentar extraer información básica del texto
                    content = response.content.lower()
                    if "comercial" in content:
                        area = "comercial"
                    elif "laboral" in content:
                        area = "laboral"
                    elif "tributario" in content:
                        area = "tributario"
                    else:
                        area = "civil"
                    
                    coordination = {
                        "legal_area": area,
                        "complexity": "medium",
                        "requires_multiple_areas": False,
                        "secondary_areas": [],
                        "reasoning": f"Extraído del texto: {response.content[:100]}",
                        "relates_to_previous": False
                    }
            
            state["legal_area"] = coordination["legal_area"]
            state["complexity"] = coordination["complexity"]
            state["metadata"]["coordination"] = coordination
            
            logger.info(
                f"✅ Coordinación completada - Área: {coordination['legal_area']}, "
                f"Complejidad: {coordination['complexity']}"
            )
            
            return state
        except Exception as e:
            logger.error(f"❌ Error en coordinador: {e}")
            # Fallback en caso de error
            state["legal_area"] = "civil"
            state["complexity"] = "medium"
            state["metadata"]["coordination"] = {"error": str(e), "fallback": True}
            return state
    
    def document_analysis_node(self, state: AgentState) -> AgentState:
        """Nodo agente de análisis de documentos"""
        try:
            logger.info(f"🔍 Análisis de documento - Pregunta: {state['question'][:100]}...")
            logger.info(f"📄 Longitud del contexto: {len(state.get('context', ''))}")
            
            response = self.agents["document_analysis"].invoke({
                "question": state["question"],
                "context": state.get("context", "")
            })
            
            logger.info("🤖 Respuesta del análisis generada exitosamente")
            
            # Crear respuesta unificada
            agent_response = AgentResponse(
                content=response.content,
                confidence=0.9,
                suggestions=[
                    "¿Hay alguna cláusula específica que te interese?",
                    "¿Necesitas más detalles sobre algún aspecto del documento?",
                    "¿Quieres que analice otra parte del contrato?"
                ],
                citations=[],
                metadata={"analysis_type": "document_specific", "timestamp": datetime.now().isoformat()}
            )
            
            state["responses"]["document_analysis"] = agent_response.__dict__
            
            logger.info("✅ Análisis de documento completado exitosamente")
            return state
        except Exception as e:
            logger.error(f"❌ Error en análisis de documento: {e}")
            error_response = AgentResponse(
                content="Error al analizar el documento específico. Por favor, intenta nuevamente.",
                confidence=0.1,
                suggestions=[
                    "Intenta reformular tu pregunta", 
                    "Verifica que el documento se haya cargado correctamente"
                ],
                citations=[],
                metadata={"error": str(e), "timestamp": datetime.now().isoformat()}
            )
            state["responses"]["document_analysis"] = error_response.__dict__
            return state
    
    def _create_legal_area_node(self, area_name: str, area_emoji: str, suggestions: list):
        """Factory method para crear nodos de áreas legales"""
        def legal_area_node(state: AgentState) -> AgentState:
            try:
                logger.info(f"{area_emoji} Procesando consulta con agente {area_name}")
                
                formatted_sources = self.format_sources_for_prompt(state.get("sources", []))
                response = self.agents[area_name].invoke({
                    "question": state["question"],
                    "context": state.get("context", ""),
                    "formatted_sources": formatted_sources
                })
                
                agent_response = AgentResponse(
                    content=response.content,
                    confidence=0.8,
                    suggestions=suggestions,
                    citations=[],
                    metadata={"area": area_name, "timestamp": datetime.now().isoformat()}
                )
                
                state["responses"][area_name] = agent_response.__dict__
                logger.info(f"✅ Consulta {area_name} procesada exitosamente")
                return state
            except Exception as e:
                logger.error(f"❌ Error en agente {area_name}: {e}")
                error_response = AgentResponse(
                    content=f"Error procesando consulta {area_name}. Intenta nuevamente.",
                    confidence=0.1,
                    suggestions=["Reformula tu pregunta", f"Sé más específico sobre el tema {area_name}"],
                    citations=[],
                    metadata={
                        "error": str(e), 
                        "area": area_name, 
                        "timestamp": datetime.now().isoformat()
                    }
                )
                state["responses"][area_name] = error_response.__dict__
                return state
        
        return legal_area_node
    
    def civil_node(self, state: AgentState) -> AgentState:
        """Nodo agente civil"""
        return self._create_legal_area_node(
            "civil", 
            "⚖️",
            [
                "¿Necesitas información sobre procedimientos específicos?",
                "¿Te interesa conocer los plazos legales aplicables?",
                "¿Requieres información sobre documentos necesarios?"
            ]
        )(state)
    
    def comercial_node(self, state: AgentState) -> AgentState:
        """Nodo agente comercial"""
        return self._create_legal_area_node(
            "comercial",
            "🏢",
            [
                "¿Necesitas información sobre constitución de empresas?",
                "¿Te interesa conocer sobre tipos societarios?",
                "¿Requieres información sobre registro mercantil?"
            ]
        )(state)
    
    def laboral_node(self, state: AgentState) -> AgentState:
        """Nodo agente laboral"""
        return self._create_legal_area_node(
            "laboral",
            "👷",
            [
                "¿Necesitas calcular prestaciones sociales?",
                "¿Te interesa información sobre contratos laborales?",
                "¿Requieres información sobre despidos?"
            ]
        )(state)
    
    def tributario_node(self, state: AgentState) -> AgentState:
        """Nodo agente tributario"""
        return self._create_legal_area_node(
            "tributario",
            "💰",
            [
                "¿Necesitas información sobre declaraciones de impuestos?",
                "¿Te interesa conocer sobre el régimen tributario?",
                "¿Requieres información sobre la DIAN?"
            ]
        )(state)
    
    def evaluator_node(self, state: AgentState) -> AgentState:
        """Nodo evaluador"""
        try:
            session_id = state.get("session_id", "default")
            conversation_context = self.memory_service.get_conversation_context(session_id)
            
            logger.info("🎓 Evaluando respuestas y consolidando resultado final")
            
            # Si hay documentos específicos, usar directamente la respuesta del análisis de documentos
            if state.get("has_specific_documents", False) and "document_analysis" in state["responses"]:
                doc_analysis = state["responses"]["document_analysis"]
                state["final_answer"] = doc_analysis["content"]
                state["confidence"] = doc_analysis["confidence"]
                state["suggestions"] = doc_analysis.get("suggestions", [])
                state["metadata"]["evaluation"] = {
                    "source": "document_analysis_only",
                    "document_citations": doc_analysis.get("citations", []),
                    "timestamp": datetime.now().isoformat()
                }
                logger.info("📄 Usando respuesta de análisis de documento únicamente")
                
                # Guardar en memoria de conversación
                self.memory_service.save_conversation_exchange(
                    session_id, 
                    state["question"], 
                    state["final_answer"], 
                    "document_analysis", 
                    state["metadata"]
                )
                
                return state
            
            # Si no hay documentos específicos, usar el evaluador normal
            response = self.agents["evaluator"].invoke({
                "question": state["question"],
                "agent_responses": state["responses"],
                "conversation_context": conversation_context,
                "has_specific_documents": state.get("has_specific_documents", False)
            })
            
            # Parsear respuesta JSON con manejo de errores mejorado
            if not response.content or not response.content.strip():
                logger.warning("⚠️ Respuesta vacía del evaluador, usando fallback")
                evaluation = {
                    "final_answer": "Lo siento, hubo un problema técnico al procesar tu consulta. Por favor, intenta de nuevo.",
                    "confidence": 0.5,
                    "suggestions": ["Intenta reformular tu pregunta", "Verifica que la consulta sea clara"],
                    "relates_to_previous": False,
                    "context_summary": "Error técnico en evaluación"
                }
            else:
                try:
                    evaluation = json.loads(response.content)
                except json.JSONDecodeError as json_error:
                    logger.warning(f"⚠️ Error JSON en evaluador: {json_error}")
                    logger.warning(f"📝 Contenido recibido: '{response.content[:200]}...'")
                    # Usar el contenido como respuesta directa si no es JSON válido
                    evaluation = {
                        "final_answer": response.content,
                        "confidence": 0.7,
                        "suggestions": ["¿Necesitas más detalles sobre este tema?", "¿Hay algo específico que te interese?"],
                        "relates_to_previous": False,
                        "context_summary": "Respuesta procesada sin formato JSON"
                    }
            
            state["final_answer"] = evaluation["final_answer"]
            state["confidence"] = evaluation["confidence"]
            state["suggestions"] = evaluation.get("suggestions", [])
            state["metadata"]["evaluation"] = evaluation
            state["metadata"]["evaluation"]["timestamp"] = datetime.now().isoformat()
            
            logger.info("✅ Evaluación completada exitosamente")
            
            # Guardar en memoria de conversación
            self.memory_service.save_conversation_exchange(
                session_id, 
                state["question"], 
                state["final_answer"], 
                state.get("legal_area", "general"), 
                state["metadata"]
            )
            
            return state
        except Exception as e:
            logger.error(f"❌ Error en evaluador: {e}")
            # Fallback: usar la respuesta del área principal
            primary_area = state.get("legal_area", "")
            if primary_area and primary_area in state.get("responses", {}):
                primary_response = state["responses"][primary_area]
                state["final_answer"] = primary_response.get("content", "Error procesando consulta")
                state["confidence"] = primary_response.get("confidence", 0.5)
                state["suggestions"] = primary_response.get("suggestions", [])
            else:
                state["final_answer"] = (
                    "Lo siento, no pude procesar tu consulta correctamente. "
                    "Por favor, intenta reformular tu pregunta."
                )
                state["confidence"] = 0.1
                state["suggestions"] = [
                    "Intenta ser más específico", 
                    "Reformula tu pregunta", 
                    "Verifica la información proporcionada"
                ]
            
            state["metadata"]["evaluation"] = {
                "source": "fallback",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            return state
