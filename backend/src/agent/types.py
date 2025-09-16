"""
Tipos y estructuras de datos para el sistema multiagente legal
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, TypedDict
from dataclasses import dataclass, field
from enum import Enum


class LegalArea(Enum):
    """Áreas legales soportadas por el sistema"""
    CIVIL = "civil"
    COMERCIAL = "comercial"
    LABORAL = "laboral"
    TRIBUTARIO = "tributario"
    DOCUMENT_ANALYSIS = "document_analysis"
    GENERAL = "general"


class QueryComplexity(Enum):
    """Niveles de complejidad de consultas"""
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
    conversation_history: List[Dict[str, Any]]
    session_id: str
    timestamp: str


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


@dataclass
class ModelConfig:
    """Configuración del modelo de IA"""
    model: str = "gpt-4o-mini"  # Modelo más rápido
    temperature: float = 0.1     # Menor temperatura para respuestas más consistentes
    max_tokens: int = 1000       # Reducido para respuestas más concisas y rápidas
