"""
Sistema Multiagente para Consultas Legales Colombianas
Especializado en: Civil, Comercial, Laboral y Tributario
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, TypedDict, Union
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from dataclasses import dataclass, field
from enum import Enum

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalArea(Enum):
    CIVIL = "civil"
    COMERCIAL = "comercial"
    LABORAL = "laboral"
    TRIBUTARIO = "tributario"
    DOCUMENT_ANALYSIS = "document_analysis"
    GENERAL = "general"

class QueryComplexity(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"

class AgentState(TypedDict, total=False):
    """Estado compartido entre agentes"""
    question: str
    context: str
    sources: List[Dict[str, Any]]
    legal_area: Optional[str]
    complexity: Optional[str]
    responses: Dict[str, Any]
    final_answer: Optional[str]
    confidence: float
    suggestions: List[str]
    metadata: Dict[str, Any]
    has_specific_documents: bool
    conversation_history: List[Dict[str, Any]]  # Nuevo campo para historial
    session_id: str  # Nuevo campo para sesión
    timestamp: str  # Nuevo campo para timestamp

@dataclass
class AgentResponse:
    """Respuesta unificada de un agente"""
    content: str
    confidence: float
    suggestions: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LegalResponse:
    """Respuesta final del sistema legal"""
    content: str
    confidence: float
    legal_area: str
    sources: List[Dict[str, Any]]
    suggestions: List[str]
    metadata: Dict[str, Any]
    conversation_context: Dict[str, Any] = field(default_factory=dict)

class LegalAgentSystem:
    """Sistema multiagente para consultas legales"""
    
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.1, max_tokens: int = 1500):
        # Configuración del modelo
        self.model_config = {
            "model": model_name,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Instancia única del modelo para reutilizar
        self.model = ChatOpenAI(**self.model_config)
        
        # Cache para conversaciones
        self.conversation_cache = {}
        
        # Memoria persistente
        self.memory = MemorySaver()
        
        # Inicializar agentes
        self.agents = self._initialize_agents()
        
        # Crear grafo
        self.graph = self._create_agent_graph()
        
        logger.info("Sistema multiagente inicializado correctamente")
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """Inicializar todos los agentes de manera lazy"""
        return {
            "coordinator": self._create_coordinator_agent(),
            "document_analysis": self._create_document_analysis_agent(),
            "civil": self._create_civil_agent(),
            "comercial": self._create_comercial_agent(),
            "laboral": self._create_laboral_agent(),
            "tributario": self._create_tributario_agent(),
            "evaluator": self._create_evaluator_agent()
        }
    
    def _get_conversation_context(self, session_id: str, max_history: int = 5) -> str:
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
    
    def _save_conversation_exchange(self, session_id: str, question: str, answer: str, legal_area: str, metadata: Dict[str, Any]):
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
            
            # Mantener solo los últimos 20 intercambios para evitar memoria excesiva
            if len(self.conversation_cache[session_id]) > 20:
                self.conversation_cache[session_id] = self.conversation_cache[session_id][-20:]
                
            logger.info(f"Intercambio guardado para sesión {session_id}")
        except Exception as e:
            logger.error(f"Error guardando intercambio: {e}")
    
    def _format_sources_for_prompt(self, sources: List[Dict[str, Any]]) -> str:
        """Formatear fuentes para uso en prompts"""
        if not sources:
            return "No hay fuentes documentales disponibles."
        
        formatted_sources = []
        for i, source in enumerate(sources, 1):
            title = source.get("title", "Documento sin título")
            content = source.get("content", "")[:150] + "..." if len(source.get("content", "")) > 150 else source.get("content", "")
            relevance = source.get("relevance", 0.0)
            
            formatted_sources.append(f"{i}. {title} (Relevancia: {relevance:.2f})\n   Contenido: {content}")
        
        return "\n\n".join(formatted_sources)
    
    def _create_coordinator_agent(self):
        """Agente coordinador que determina el área legal y complejidad"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un coordinador legal experto en derecho colombiano.

CONTEXTO DE CONVERSACIÓN:
{conversation_context}

Tu función es:
1. Analizar la consulta legal CONSIDERANDO el historial de conversación
2. Determinar el área legal principal (civil, comercial, laboral, tributario)
3. Evaluar la complejidad (simple, medium, complex)
4. Identificar si requiere múltiples áreas legales
5. MANTENER COHERENCIA con consultas anteriores en la misma sesión

Áreas legales:
- CIVIL: Contratos civiles, familia, sucesiones, responsabilidad civil
- COMERCIAL: Constitución de empresas, contratos comerciales, sociedades
- LABORAL: Contratos de trabajo, prestaciones, despidos, seguridad social
- TRIBUTARIO: Impuestos, declaraciones, régimen tributario, DIAN

IMPORTANTE: Si la pregunta se refiere a temas ya discutidos anteriormente, mantén coherencia con el contexto previo.

Responde en formato JSON:
{{
  "legal_area": "civil",
  "complexity": "simple", 
  "requires_multiple_areas": true/false,
  "secondary_areas": ["area1", "area2"],
  "reasoning": "explicación breve considerando el contexto",
  "relates_to_previous": true/false
}}"""),
            ("human", "Consulta actual: {question}\n\nContexto de conversación previa: {conversation_context}")
        ])
        return prompt | self.model
    
    def _create_civil_agent(self):
        """Agente especializado en derecho civil"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un abogado experto en DERECHO CIVIL COLOMBIANO.

Especialidades:
- Contratos civiles (compraventa, arrendamiento, prestación de servicios)
- Derecho de familia (matrimonio, divorcio, alimentos, custodia)
- Sucesiones y herencias
- Responsabilidad civil extracontractual
- Derechos reales (propiedad, posesión, servidumbres)
- Personas naturales y jurídicas

Normativa principal:
- Código Civil Colombiano
- Código General del Proceso
- Ley 1564 de 2012

Instrucciones:
1. Proporciona respuestas precisas basadas en la legislación colombiana
2. Cita artículos específicos cuando sea relevante
3. Incluye procedimientos paso a paso cuando aplique
4. Menciona plazos legales importantes
5. Sugiere documentos necesarios

Contexto disponible: {context}
Fuentes: {formatted_sources}"""),
            ("human", "Consulta civil: {question}\n\nContexto: {context}\n\nFuentes:\n{formatted_sources}")
        ])
        return prompt | self.model
    
    def _create_comercial_agent(self):
        """Agente especializado en derecho comercial"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un abogado experto en DERECHO COMERCIAL COLOMBIANO.

Especialidades:
- Constitución de sociedades (SAS, Ltda, S.A.)
- Contratos comerciales
- Registro mercantil y Cámara de Comercio
- Títulos valores (cheques, pagarés, letras)
- Procedimientos concursales
- Propiedad industrial e intelectual

Normativa principal:
- Código de Comercio (Decreto 410 de 1971)
- Ley 1258 de 2008 (SAS)
- Ley 222 de 1995 (Sociedades)
- Decreto 1074 de 2015

Instrucciones:
1. Enfócate en aspectos prácticos para empresarios
2. Explica diferencias entre tipos societarios
3. Detalla requisitos de constitución y registro
4. Incluye costos aproximados cuando sea relevante
5. Sugiere mejores prácticas empresariales

Contexto disponible: {context}
Fuentes: {formatted_sources}"""),
            ("human", "Consulta comercial: {question}\n\nContexto: {context}\n\nFuentes:\n{formatted_sources}")
        ])
        return prompt | self.model
    
    def _create_laboral_agent(self):
        """Agente especializado en derecho laboral"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un abogado experto en DERECHO LABORAL COLOMBIANO.

Especialidades:
- Contratos de trabajo (término fijo, indefinido, obra/labor)
- Prestaciones sociales (cesantías, prima, vacaciones)
- Liquidación de contratos
- Despidos y terminación laboral
- Seguridad social (EPS, AFP, ARL, CCF)
- Procedimientos ante el Ministerio del Trabajo

Normativa principal:
- Código Sustantivo del Trabajo
- Ley 789 de 2002
- Ley 1010 de 2006 (Acoso laboral)
- Decretos reglamentarios del MinTrabajo

Instrucciones:
1. Calcula prestaciones con fórmulas exactas
2. Explica procedimientos paso a paso
3. Incluye plazos y términos legales
4. Diferencia entre empleados y contratistas
5. Menciona derechos y obligaciones de ambas partes

Contexto disponible: {context}
Fuentes: {formatted_sources}"""),
            ("human", "Consulta laboral: {question}\n\nContexto: {context}\n\nFuentes:\n{formatted_sources}")
        ])
        return prompt | self.model
    
    def _create_tributario_agent(self):
        """Agente especializado en derecho tributario"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un abogado experto en DERECHO TRIBUTARIO COLOMBIANO.

Especialidades:
- Impuesto sobre la renta y complementarios
- IVA (Impuesto al Valor Agregado)
- Retención en la fuente
- Régimen Simple de Tributación (RST)
- Procedimientos ante la DIAN
- Sanciones y procesos tributarios

Normativa principal:
- Estatuto Tributario (Decreto 624 de 1989)
- Ley 2277 de 2022 (Reforma tributaria)
- Código de Procedimiento Tributario
- Resoluciones y conceptos DIAN

Instrucciones:
1. Explica obligaciones tributarias por tipo de contribuyente
2. Calcula impuestos con tarifas actuales
3. Detalla plazos de declaración y pago
4. Incluye beneficios y deducciones aplicables
5. Menciona consecuencias del incumplimiento

Contexto disponible: {context}
Fuentes: {formatted_sources}"""),
            ("human", "Consulta tributaria: {question}\n\nContexto: {context}\n\nFuentes:\n{formatted_sources}")
        ])
        return prompt | self.model
    
    def _create_document_analysis_agent(self):
        """Agente especializado en análisis de documentos específicos"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un abogado experto en análisis de documentos legales. Tu función es analizar documentos específicos subidos por el usuario y responder preguntas basándote ÚNICAMENTE en el contenido de esos documentos.

INSTRUCCIONES CRÍTICAS:
- PRIORIZA SIEMPRE el contenido del documento sobre conocimiento general
- BUSCA ESPECÍFICAMENTE en el texto del documento la información relacionada con la pregunta
- Si encuentras cláusulas, secciones o párrafos relevantes, CÍTALOS LITERALMENTE
- Si el documento contiene información específica sobre la pregunta, úsala como respuesta principal
- Si el documento NO contiene información relevante, indica claramente que no se encontró información específica
- NO mezcles conocimiento general con contenido del documento
- Usa frases como "Según la cláusula X del contrato..." o "El documento establece que..."

PROCESO DE ANÁLISIS OBLIGATORIO:
1. LEE TODO EL CONTENIDO DEL DOCUMENTO línea por línea
2. Busca palabras clave relacionadas con la pregunta (ej: "propiedad intelectual", "derechos de autor", "entregables")
3. Busca cláusulas específicas (ej: "SEXTA", "CLÁUSULA SEXTA", "propiedad intelectual")
4. Si encuentras información relevante, CÍTALA TEXTUALMENTE
5. Si NO encuentras nada, entonces di "No se encontró información específica en el documento"

REGLA CRÍTICA: 
- SOLO puedes responder basándote en el contenido del documento
- NO uses conocimiento general de derecho colombiano
- NO mezcles información del documento con conocimiento general
- Si el documento no tiene la información, di claramente que no la tiene

Para preguntas como "resumen del documento", proporciona un resumen completo basado en el contenido.
Para preguntas específicas, busca la información exacta en el documento.

CONTENIDO DEL DOCUMENTO:
{context}

PREGUNTA DEL USUARIO:
{question}

IMPORTANTE: Responde de manera precisa y específica basándote únicamente en el contenido del documento. Si no encuentras la información en el documento, di claramente que no está disponible en el contenido proporcionado."""),
            ("human", "Analiza el documento y responde: {question}")
        ])
        return prompt | self.model
    
    def _create_evaluator_agent(self):
        """Agente evaluador que consolida respuestas"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un abogado experto en derecho colombiano. Tu función es proporcionar respuestas legales claras, concisas y prácticas.

CONTEXTO DE CONVERSACIÓN PREVIA:
{conversation_context}

INSTRUCCIONES CRÍTICAS PARA MEMORIA:
- SIEMPRE considera el historial de conversación antes de responder
- Si la pregunta se relaciona con temas ya discutidos, haz referencia a ellos
- Mantén coherencia con respuestas anteriores en la misma sesión
- Si hay contradicciones con respuestas previas, acláralas
- Usa frases como "Como mencionamos anteriormente..." cuando sea relevante

INSTRUCCIONES DE FORMATO:
- Responde de manera natural y conversacional
- Evita estructuras rígidas como "1. 2. 3." o listas numeradas
- Sé directo y al grano, máximo 3-4 párrafos
- Usa un lenguaje claro y accesible
- Incluye solo la información más relevante

PRIORIDAD DE RESPUESTAS:
- Si hay respuesta de análisis de documento específico, úsala COMO ÚNICA RESPUESTA
- NO mezcles la respuesta del documento con conocimiento general
- Si el análisis de documento dice "no se encontró información", responde exactamente eso
- Si no hay documento específico, usa las respuestas de los agentes especializados
- NUNCA combines información del documento con conocimiento general

MANEJO DE SEGUIMIENTO:
- Si la pregunta es un seguimiento ("y qué pasa si...", "pero también...", "además..."), 
  conecta tu respuesta con el contexto previo
- Si detectas que la pregunta cambia de tema, indica el cambio de manera natural

Responde en formato JSON:
{{
  "final_answer": "respuesta natural y conversacional que considera el contexto previo",
  "confidence": 0.85,
  "suggestions": ["pregunta1", "pregunta2"],
  "relates_to_previous": true/false,
  "context_summary": "breve resumen de cómo se relaciona con conversaciones anteriores"
}}

Respuestas de agentes: {agent_responses}
Pregunta original: {question}
Contexto de conversación: {conversation_context}
Tiene documentos específicos: {has_specific_documents}"""),
            ("human", "Proporciona una respuesta legal clara y concisa considerando el contexto de conversación para: {question}")
        ])
        return prompt | self.model
    
    def _create_agent_graph(self):
        """Crear el grafo de agentes con LangGraph"""
        workflow = StateGraph(AgentState)
        
        # Agregar nodos
        workflow.add_node("coordinator", self._coordinator_node)
        workflow.add_node("document_analysis", self._document_analysis_node)
        workflow.add_node("civil", self._civil_node)
        workflow.add_node("comercial", self._comercial_node)
        workflow.add_node("laboral", self._laboral_node)
        workflow.add_node("tributario", self._tributario_node)
        workflow.add_node("evaluator", self._evaluator_node)
        
        # Configurar flujo
        workflow.set_entry_point("coordinator")
        
        # Routing condicional desde coordinator
        workflow.add_conditional_edges(
            "coordinator",
            self._route_to_specialists,
            {
                "document_analysis": "document_analysis",
                "civil": "civil",
                "comercial": "comercial", 
                "laboral": "laboral",
                "tributario": "tributario",
                "general": "civil",  # Para casos generales, usar civil
                "multiple": "civil"  # Para casos complejos, empezar con civil
            }
        )
        
        # Todos los especialistas van al evaluador
        workflow.add_edge("document_analysis", "evaluator")
        workflow.add_edge("civil", "evaluator")
        workflow.add_edge("comercial", "evaluator")
        workflow.add_edge("laboral", "evaluator")
        workflow.add_edge("tributario", "evaluator")
        
        # El evaluador termina el flujo
        workflow.add_edge("evaluator", END)
        
        # Compilar con checkpointer para memoria
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    
    def _coordinator_node(self, state: AgentState) -> AgentState:
        """Nodo coordinador"""
        try:
            session_id = state.get("session_id", "default")
            conversation_context = self._get_conversation_context(session_id)
            
            logger.info(f"🎯 Coordinador procesando pregunta: {state['question'][:100]}...")
            
            response = self.agents["coordinator"].invoke({
                "question": state["question"],
                "conversation_context": conversation_context
            })
            
            # Parsear respuesta JSON
            coordination = json.loads(response.content)
            
            state["legal_area"] = coordination["legal_area"]
            state["complexity"] = coordination["complexity"]
            state["metadata"]["coordination"] = coordination
            
            logger.info(f"✅ Coordinación completada - Área: {coordination['legal_area']}, Complejidad: {coordination['complexity']}")
            
            return state
        except Exception as e:
            logger.error(f"❌ Error en coordinador: {e}")
            # Fallback en caso de error
            state["legal_area"] = "civil"
            state["complexity"] = "medium"
            state["metadata"]["coordination"] = {"error": str(e), "fallback": True}
            return state
    
    def _document_analysis_node(self, state: AgentState) -> AgentState:
        """Nodo agente de análisis de documentos"""
        try:
            logger.info(f"🔍 Análisis de documento - Pregunta: {state['question'][:100]}...")
            logger.info(f"📄 Longitud del contexto: {len(state.get('context', ''))}")
            
            response = self.agents["document_analysis"].invoke({
                "question": state["question"],
                "context": state.get("context", "")
            })
            
            logger.info(f"🤖 Respuesta del análisis generada exitosamente")
            
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
                suggestions=["Intenta reformular tu pregunta", "Verifica que el documento se haya cargado correctamente"],
                citations=[],
                metadata={"error": str(e), "timestamp": datetime.now().isoformat()}
            )
            state["responses"]["document_analysis"] = error_response.__dict__
            return state
    
    def _civil_node(self, state: AgentState) -> AgentState:
        """Nodo agente civil"""
        try:
            logger.info("⚖️ Procesando consulta con agente civil")
            
            formatted_sources = self._format_sources_for_prompt(state.get("sources", []))
            response = self.agents["civil"].invoke({
                "question": state["question"],
                "context": state.get("context", ""),
                "formatted_sources": formatted_sources
            })
            
            agent_response = AgentResponse(
                content=response.content,
                confidence=0.8,
                suggestions=[
                    "¿Necesitas información sobre procedimientos específicos?",
                    "¿Te interesa conocer los plazos legales aplicables?",
                    "¿Requieres información sobre documentos necesarios?"
                ],
                citations=[],
                metadata={"area": "civil", "timestamp": datetime.now().isoformat()}
            )
            
            state["responses"]["civil"] = agent_response.__dict__
            logger.info("✅ Consulta civil procesada exitosamente")
            return state
        except Exception as e:
            logger.error(f"❌ Error en agente civil: {e}")
            error_response = AgentResponse(
                content="Error procesando consulta civil. Intenta nuevamente.",
                confidence=0.1,
                suggestions=["Reformula tu pregunta", "Intenta ser más específico"],
                citations=[],
                metadata={"error": str(e), "area": "civil", "timestamp": datetime.now().isoformat()}
            )
            state["responses"]["civil"] = error_response.__dict__
            return state
    
    def _comercial_node(self, state: AgentState) -> AgentState:
        """Nodo agente comercial"""
        try:
            logger.info("🏢 Procesando consulta con agente comercial")
            
            formatted_sources = self._format_sources_for_prompt(state.get("sources", []))
            response = self.agents["comercial"].invoke({
                "question": state["question"],
                "context": state.get("context", ""),
                "formatted_sources": formatted_sources
            })
            
            agent_response = AgentResponse(
                content=response.content,
                confidence=0.8,
                suggestions=[
                    "¿Necesitas información sobre constitución de empresas?",
                    "¿Te interesa conocer sobre tipos societarios?",
                    "¿Requieres información sobre registro mercantil?"
                ],
                citations=[],
                metadata={"area": "comercial", "timestamp": datetime.now().isoformat()}
            )
            
            state["responses"]["comercial"] = agent_response.__dict__
            logger.info("✅ Consulta comercial procesada exitosamente")
            return state
        except Exception as e:
            logger.error(f"❌ Error en agente comercial: {e}")
            error_response = AgentResponse(
                content="Error procesando consulta comercial. Intenta nuevamente.",
                confidence=0.1,
                suggestions=["Reformula tu pregunta", "Sé más específico sobre el tema comercial"],
                citations=[],
                metadata={"error": str(e), "area": "comercial", "timestamp": datetime.now().isoformat()}
            )
            state["responses"]["comercial"] = error_response.__dict__
            return state
    
    def _laboral_node(self, state: AgentState) -> AgentState:
        """Nodo agente laboral"""
        try:
            logger.info("👷 Procesando consulta con agente laboral")
            
            formatted_sources = self._format_sources_for_prompt(state.get("sources", []))
            response = self.agents["laboral"].invoke({
                "question": state["question"],
                "context": state.get("context", ""),
                "formatted_sources": formatted_sources
            })
            
            agent_response = AgentResponse(
                content=response.content,
                confidence=0.8,
                suggestions=[
                    "¿Necesitas calcular prestaciones sociales?",
                    "¿Te interesa información sobre contratos laborales?",
                    "¿Requieres información sobre despidos?"
                ],
                citations=[],
                metadata={"area": "laboral", "timestamp": datetime.now().isoformat()}
            )
            
            state["responses"]["laboral"] = agent_response.__dict__
            logger.info("✅ Consulta laboral procesada exitosamente")
            return state
        except Exception as e:
            logger.error(f"❌ Error en agente laboral: {e}")
            error_response = AgentResponse(
                content="Error procesando consulta laboral. Intenta nuevamente.",
                confidence=0.1,
                suggestions=["Reformula tu pregunta", "Sé más específico sobre el tema laboral"],
                citations=[],
                metadata={"error": str(e), "area": "laboral", "timestamp": datetime.now().isoformat()}
            )
            state["responses"]["laboral"] = error_response.__dict__
            return state
    
    def _tributario_node(self, state: AgentState) -> AgentState:
        """Nodo agente tributario"""
        try:
            logger.info("💰 Procesando consulta con agente tributario")
            
            formatted_sources = self._format_sources_for_prompt(state.get("sources", []))
            response = self.agents["tributario"].invoke({
                "question": state["question"],
                "context": state.get("context", ""),
                "formatted_sources": formatted_sources
            })
            
            agent_response = AgentResponse(
                content=response.content,
                confidence=0.8,
                suggestions=[
                    "¿Necesitas información sobre declaraciones de impuestos?",
                    "¿Te interesa conocer sobre el régimen tributario?",
                    "¿Requieres información sobre la DIAN?"
                ],
                citations=[],
                metadata={"area": "tributario", "timestamp": datetime.now().isoformat()}
            )
            
            state["responses"]["tributario"] = agent_response.__dict__
            logger.info("✅ Consulta tributaria procesada exitosamente")
            return state
        except Exception as e:
            logger.error(f"❌ Error en agente tributario: {e}")
            error_response = AgentResponse(
                content="Error procesando consulta tributaria. Intenta nuevamente.",
                confidence=0.1,
                suggestions=["Reformula tu pregunta", "Sé más específico sobre el tema tributario"],
                citations=[],
                metadata={"error": str(e), "area": "tributario", "timestamp": datetime.now().isoformat()}
            )
            state["responses"]["tributario"] = error_response.__dict__
            return state
    
    def _evaluator_node(self, state: AgentState) -> AgentState:
        """Nodo evaluador"""
        try:
            session_id = state.get("session_id", "default")
            conversation_context = self._get_conversation_context(session_id)
            
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
                self._save_conversation_exchange(
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
            
            # Parsear respuesta JSON
            evaluation = json.loads(response.content)
            
            state["final_answer"] = evaluation["final_answer"]
            state["confidence"] = evaluation["confidence"]
            state["suggestions"] = evaluation.get("suggestions", [])
            state["metadata"]["evaluation"] = evaluation
            state["metadata"]["evaluation"]["timestamp"] = datetime.now().isoformat()
            
            logger.info("✅ Evaluación completada exitosamente")
            
            # Guardar en memoria de conversación
            self._save_conversation_exchange(
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
                state["final_answer"] = "Lo siento, no pude procesar tu consulta correctamente. Por favor, intenta reformular tu pregunta."
                state["confidence"] = 0.1
                state["suggestions"] = ["Intenta ser más específico", "Reformula tu pregunta", "Verifica la información proporcionada"]
            
            state["metadata"]["evaluation"] = {
                "source": "fallback",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            return state
    
    def _route_to_specialists(self, state: AgentState) -> str:
        """Determinar qué especialista usar"""
        # Si hay documentos específicos, priorizar análisis de documentos
        if state.get("has_specific_documents", False):
            return "document_analysis"
        
        legal_area = state.get("legal_area", "") or "general"
        
        area_mapping = {
            "civil": "civil",
            "comercial": "comercial", 
            "laboral": "laboral",
            "tributario": "tributario",
            "general": "civil"  # Para casos generales, usar civil
        }
        
        return area_mapping.get(legal_area, "civil")  # Default a civil
    
    async def process_query(
        self,
        question: str,
        context: str = "",
        sources: List[Dict[str, Any]] = None,
        user_id: str = "default",
        session_id: str = None,
        conversation_context: str = ""
    ) -> Dict[str, Any]:
        """
        Procesar consulta legal a través del sistema multiagente
        
        Args:
            question: Pregunta del usuario
            context: Contexto de documentos relevantes
            sources: Lista de fuentes documentales
            user_id: ID del usuario para seguimiento
            session_id: ID de sesión para memoria de conversación
            conversation_context: Contexto de conversación anterior (deprecated, usar session_id)
            
        Returns:
            Respuesta procesada por el sistema multiagente
        """
        # Validaciones de entrada
        if not question or not question.strip():
            logger.error("Pregunta vacía recibida")
            return {
                "answer": "Por favor, proporciona una pregunta válida.",
                "confidence": 0.0,
                "legal_area": "error",
                "complexity": "simple",
                "sources": [],
                "suggestions": ["Escribe una pregunta legal específica", "Intenta ser más claro en tu consulta"],
                "metadata": {"error": "empty_question", "timestamp": datetime.now().isoformat()}
            }
        
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
        initial_state = AgentState(
            question=question.strip(),
            context=context or "Legislación colombiana aplicable.",
            sources=sources or [{"title": "Legislación Colombiana", "content": "Documentos legales del sistema", "relevance": 1.0, "filename": "legislacion_colombiana", "metadata": {}}],
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
        
        # Configuración de thread para memoria persistente de LangGraph
        config = {"configurable": {"thread_id": f"legal_query_{session_id}"}}
        
        try:
            # Ejecutar el grafo
            result = await self.graph.ainvoke(initial_state, config=config)
            
            logger.info(f"✅ Consulta procesada exitosamente con confianza {result['confidence']}")
            
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
                    "has_conversation_history": len(self.conversation_cache.get(session_id, [])) > 0
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error procesando consulta: {e}")
            return {
                "answer": "Lo siento, ocurrió un error procesando tu consulta. Por favor, intenta nuevamente.",
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
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "session_id": session_id,
                    "user_id": user_id
                }
            }
    
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

# Instancia global del sistema
legal_agent_system = LegalAgentSystem()
