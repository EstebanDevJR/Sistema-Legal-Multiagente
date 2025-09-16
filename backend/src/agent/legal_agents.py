"""
Sistema Multiagente para Consultas Legales Colombianas - LEGACY FILE
Este archivo mantiene compatibilidad hacia atrás.
La nueva implementación refactorizada está en legal_agent_system.py
"""

# Importar desde la nueva implementación refactorizada
from .legal_agent_system import LegalAgentSystem
from .types import LegalArea, QueryComplexity, AgentState, AgentResponse, LegalResponse

# Mantener compatibilidad con la instancia global
legal_agent_system = LegalAgentSystem()
