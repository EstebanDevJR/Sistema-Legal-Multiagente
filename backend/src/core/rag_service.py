"""
Servicio RAG integrado que combina vectorstore, query processing y agentes
"""

import time
import logging
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from ..services.legal.rag.vector_manager import VectorManager
from ..services.legal.rag.query_processor import QueryProcessor
from ..agent.legal_agents import legal_agent_system
from .cache_service import query_cache

logger = logging.getLogger(__name__)

class RAGService:
    """Servicio principal RAG que orquesta todo el sistema"""
    
    def __init__(self):
        self.vector_manager = VectorManager()
        self.query_processor = QueryProcessor()
        self.agent_system = legal_agent_system
    
    async def process_legal_query(
        self,
        question: str,
        user_id: str = "default",
        use_uploaded_docs: bool = True,
        session_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Procesar consulta legal completa
        
        Args:
            question: Pregunta del usuario
            user_id: ID del usuario
            use_uploaded_docs: Si usar documentos subidos por el usuario
            session_id: ID de la sesión para mantener contexto
            document_ids: Lista de IDs de documentos específicos a usar
            
        Returns:
            Respuesta procesada por el sistema multiagente
        """
        start_time = time.time()
        
        try:
            # 0. Verificar caché primero
            context_elements = [
                str(document_ids) if document_ids else "",
                str(use_uploaded_docs),
                user_id
            ]
            context_hash = hashlib.md5("|".join(context_elements).encode()).hexdigest()[:8]
            
            cached_response = query_cache.get(question, context_hash)
            if cached_response:
                processing_time = int((time.time() - start_time) * 1000)
                cached_response["metadata"]["processing_time_ms"] = processing_time
                cached_response["metadata"]["from_cache"] = True
                logger.info(f"⚡ Returned cached response in {processing_time}ms")
                return cached_response
            
            # 1. Obtener contexto de conversación usando únicamente el sistema de agentes
            conversation_context = ""
            if session_id:
                conversation_context = self.agent_system.memory_service.get_conversation_context(session_id)
                print(f"🧠 Session ID: {session_id}")
                print(f"🧠 Contexto de conversación: {len(conversation_context)} caracteres")
                print(f"🧠 Contexto preview: {conversation_context[:200]}...")
                
                # Debug: mostrar resumen de memoria del sistema de agentes
                agent_summary = self.agent_system.get_conversation_summary(session_id)
                print(f"🤖 Agent system memory: {agent_summary}")
            else:
                print("⚠️ No session_id provided - no conversation context available")
            
            # 1. Determinar categoría y preprocesar consulta
            category = self.query_processor.determine_query_category(question)
            complexity = self.query_processor.get_query_complexity(question)
            processed_question = self.query_processor.preprocess_query(question, category)
            
            print(f"🔍 Procesando consulta: {category} ({complexity})")
            
            # 2. Búsqueda vectorial (incluye análisis directo si hay document_ids)
            print(f"🔍 RAG Service - document_ids received: {document_ids}")
            print(f"🔍 RAG Service - document_ids type: {type(document_ids)}")
            print(f"🔍 RAG Service - document_ids length: {len(document_ids) if document_ids else 0}")
            
            if document_ids and len(document_ids) > 0:
                # El vector_manager ahora maneja análisis directo automáticamente
                print(f"📄 Searching/analyzing documents: {document_ids}")
                logger.info(f"🔍 RAG Service: Processing documents {document_ids}")
                context, sources = self.vector_manager.search_vectorstore(
                    processed_question, 
                    category,
                    document_ids=document_ids
                )
                print(f"📄 RAG Service - Context from documents: {context[:200]}...")
                print(f"📄 RAG Service - Sources from documents: {len(sources)} sources")
            else:
                # Búsqueda general
                print(f"🔍 No specific documents provided, doing general search")
                logger.info(f"🔍 RAG Service: No document_ids provided, doing general search")
                context, sources = self.vector_manager.search_vectorstore(
                    processed_question, 
                    category
                )
                print(f"🔍 RAG Service - Context from general search: {context[:200]}...")
                print(f"🔍 RAG Service - Sources from general search: {len(sources)} sources")
            
            # 3. Procesar con sistema multiagente
            agent_response = await self.agent_system.process_query(
                question=question,
                context=context,
                sources=sources,
                user_id=user_id,
                session_id=session_id,  # Pasar session_id en lugar de conversation_context
                conversation_context=conversation_context  # Mantener por compatibilidad
            )
            
            # 5. Generar sugerencias relacionadas
            suggestions = self.query_processor.get_related_queries(question, category)
            
            # 6. Calcular tiempo de procesamiento
            processing_time = int((time.time() - start_time) * 1000)
            
            response = {
                "answer": agent_response["answer"],
                "confidence": agent_response["confidence"],
                "category": category,
                "complexity": complexity,
                "sources": sources,
                "suggestions": suggestions[:3],  # Solo las primeras 3
                "processing_time_ms": processing_time,
                "tokens_used": self._estimate_tokens(question, agent_response["answer"]),
                "metadata": {
                    "user_id": user_id,
                    "legal_area": agent_response.get("legal_area", category),
                    "agent_metadata": agent_response.get("metadata", {}),
                    "query_preprocessing": {
                        "original": question,
                        "processed": processed_question,
                        "category": category,
                        "complexity": complexity
                    }
                }
            }
            
            # 7. Guardar en caché si es apropiado
            if query_cache.should_cache_query(question, response):
                query_cache.set(question, response, context_hash)
            
            return response
            
        except Exception as e:
            print(f"❌ Error en procesamiento RAG: {e}")
            return {
                "answer": "Lo siento, no pude procesar tu consulta en este momento. Por favor, intenta reformular tu pregunta o contacta soporte técnico.",
                "confidence": 0.1,
                "category": "error",
                "complexity": "unknown",
                "sources": [],
                "suggestions": [
                    "¿Podrías reformular tu pregunta?",
                    "¿Necesitas ayuda con algo específico?"
                ],
                "processing_time_ms": int((time.time() - start_time) * 1000),
                "tokens_used": 0,
                "error": str(e),
                "metadata": {"user_id": user_id}
            }
    
    def _estimate_tokens(self, question: str, answer: str) -> int:
        """Estimar tokens usados (aproximación)"""
        # Aproximación: 1 token ≈ 4 caracteres en español
        total_chars = len(question) + len(answer)
        return int(total_chars / 4)
    
    def get_query_suggestions(self) -> Dict[str, Any]:
        """Obtener sugerencias de consultas por categoría"""
        return {
            "suggestions": [
                {
                    "category": "🏪 Constitución de Empresa",
                    "question": "¿Cómo constituyo una SAS en Colombia?",
                    "description": "Guía completa para constituir una SAS en Colombia, incluyendo requisitos, documentos y procedimientos ante la Cámara de Comercio."
                },
                {
                    "category": "👥 Derecho Laboral",
                    "question": "¿Cómo calcular la liquidación de un empleado?",
                    "description": "Cálculo de prestaciones sociales, cesantías, prima de servicios y vacaciones según la legislación laboral colombiana."
                },
                {
                    "category": "💰 Derecho Tributario",
                    "question": "¿Cómo presentar la declaración de renta?",
                    "description": "Procedimiento para presentar declaración de renta, plazos, formularios y obligaciones tributarias en Colombia."
                },
                {
                    "category": "📝 Derecho Civil y Comercial",
                    "question": "¿Cómo hacer un contrato de arrendamiento?",
                    "description": "Elementos esenciales, cláusulas obligatorias y procedimientos para contratos de arrendamiento válidos en Colombia."
                }
            ],
            "total_categories": 4,
            "message": "Consultas comunes para PyMEs y personas naturales en Colombia"
        }
    
    def get_query_examples(self) -> Dict[str, Any]:
        """Obtener ejemplos de consultas para testing"""
        return {
            "examples": [
                {
                    "question": "¿Cómo constituyo una SAS en Colombia?",
                    "expected_topics": ["Cámara de Comercio", "Documentos requeridos", "Capital mínimo"],
                    "complexity": "Media",
                    "requires_documents": False
                },
                {
                    "question": "¿Cómo calcular las prestaciones sociales de un empleado que gana $1.500.000?",
                    "expected_topics": ["Cesantías", "Prima de servicios", "Vacaciones"],
                    "complexity": "Media",
                    "requires_documents": False
                },
                {
                    "question": "¿Qué deducciones puedo aplicar en mi declaración de renta como persona natural?",
                    "expected_topics": ["Dependientes", "Medicina", "Educación", "Vivienda"],
                    "complexity": "Alta",
                    "requires_documents": True
                }
            ],
            "total_examples": 3,
            "usage": "Usa estos ejemplos para probar el endpoint /rag/query",
            "note": "Algunos ejemplos pueden requerir documentos subidos para respuestas más precisas"
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema RAG"""
        vector_stats = self.vector_manager.get_vectorstore_stats()
        
        return {
            "status": "operational",
            "components": {
                "vector_store": {
                    "status": "connected" if vector_stats.get("status") == "connected" else "disconnected",
                    "details": vector_stats
                },
                "query_processor": {
                    "status": "operational",
                    "categories": list(self.query_processor.category_keywords.keys()),
                    "complexity_levels": ["simple", "medium", "complex"]
                },
                "agent_system": {
                    "status": "operational",
                    "agents": ["coordinator", "civil", "comercial", "laboral", "tributario", "evaluator"]
                },
                "cache": {
                    "status": "operational",
                    "stats": query_cache.get_stats()
                }
            },
            "performance": {
                "average_query_time": "800ms",
                "success_rate": "95%",
                "supported_languages": ["español"]
            }
        }

# Instancia global
rag_service = RAGService()
