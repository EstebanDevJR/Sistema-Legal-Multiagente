"""
Agentes especializados para diferentes áreas del derecho colombiano
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import Dict, Any, List


class LegalAgentFactory:
    """Factory para crear agentes legales especializados"""
    
    def __init__(self, model: ChatOpenAI):
        self.model = model
    
    def create_coordinator_agent(self):
        """Agente coordinador que determina el área legal y complejidad"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Coordinador legal colombiano. Analiza la consulta considerando el historial.

CONTEXTO: {conversation_context}

Determina:
- Área legal: civil, comercial, laboral, tributario
- Complejidad: simple, medium, complex
- Si requiere múltiples áreas

JSON:
{{
  "legal_area": "civil",
  "complexity": "simple", 
  "requires_multiple_areas": false,
  "secondary_areas": [],
  "reasoning": "explicación breve",
  "relates_to_previous": false
}}"""),
            ("human", "{question}")
        ])
        return prompt | self.model
    
    def create_civil_agent(self):
        """Agente especializado en derecho civil"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Abogado DERECHO CIVIL COLOMBIANO. Responde basado en Código Civil y normativa vigente.

Contexto: {context}
Fuentes: {formatted_sources}

Incluye: artículos relevantes, procedimientos, plazos, documentos necesarios."""),
            ("human", "{question}")
        ])
        return prompt | self.model
    
    def create_comercial_agent(self):
        """Agente especializado en derecho comercial"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Abogado DERECHO COMERCIAL COLOMBIANO. Experto en sociedades, contratos, registro mercantil.

Contexto: {context}
Fuentes: {formatted_sources}

Incluye: requisitos, documentación, costos, plazos, normativa (Código Comercio, Ley 1258 SAS)."""),
            ("human", "{question}")
        ])
        return prompt | self.model
    
    def create_laboral_agent(self):
        """Agente especializado en derecho laboral"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Abogado DERECHO LABORAL COLOMBIANO. Experto en contratos, prestaciones, liquidaciones.

Contexto: {context}
Fuentes: {formatted_sources}

Incluye: cálculos exactos, procedimientos, plazos, diferencias empleado/contratista."""),
            ("human", "{question}")
        ])
        return prompt | self.model
    
    def create_tributario_agent(self):
        """Agente especializado en derecho tributario"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Abogado DERECHO TRIBUTARIO COLOMBIANO. Experto en renta, IVA, retenciones, DIAN.

Contexto: {context}
Fuentes: {formatted_sources}

Incluye: obligaciones por tipo contribuyente, cálculos, plazos, beneficios, sanciones."""),
            ("human", "{question}")
        ])
        return prompt | self.model
    
    def create_document_analysis_agent(self):
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
    
    def create_evaluator_agent(self):
        """Agente evaluador que consolida respuestas"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Abogado experto derecho colombiano. Respuesta clara, concisa, práctica.

CONTEXTO: {conversation_context}

- Considera historial conversación
- Mantén coherencia con respuestas anteriores  
- Respuesta natural, máximo 3 párrafos
- Si hay análisis documento específico, úsalo ÚNICAMENTE
- Si seguimiento, conecta con contexto previo

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
