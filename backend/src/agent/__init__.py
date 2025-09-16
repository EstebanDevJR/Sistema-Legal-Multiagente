"""
Módulo del sistema multiagente legal
"""

from .legal_agents import legal_agent_system
from .types import LegalArea, QueryComplexity, AgentState, AgentResponse, LegalResponse

__all__ = [
    'legal_agent_system',
    'LegalArea',
    'QueryComplexity', 
    'AgentState',
    'AgentResponse',
    'LegalResponse'
]