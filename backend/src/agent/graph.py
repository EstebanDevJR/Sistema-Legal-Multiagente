"""
Grafo principal del sistema multiagente legal
"""

from .legal_agents import legal_agent_system

# Exportar el grafo para LangGraph
graph = legal_agent_system.graph
