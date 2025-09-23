"""
Constructor del grafo de agentes usando LangGraph
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, Any

from .types import AgentState
from .workflow_nodes import WorkflowNodes


class LegalAgentGraphBuilder:
    """Constructor del grafo de agentes legales"""
    
    def __init__(self, workflow_nodes: WorkflowNodes):
        self.workflow_nodes = workflow_nodes
    
    def build_graph(self):
        """Crear el grafo de agentes con LangGraph"""
        workflow = StateGraph(AgentState)
        
        # Agregar nodos
        workflow.add_node("coordinator", self.workflow_nodes.coordinator_node)
        workflow.add_node("document_analysis", self.workflow_nodes.document_analysis_node)
        workflow.add_node("civil", self.workflow_nodes.civil_node)
        workflow.add_node("comercial", self.workflow_nodes.comercial_node)
        workflow.add_node("laboral", self.workflow_nodes.laboral_node)
        workflow.add_node("tributario", self.workflow_nodes.tributario_node)
        workflow.add_node("constitucional", self.workflow_nodes.constitucional_node)
        workflow.add_node("administrativo", self.workflow_nodes.administrativo_node)
        workflow.add_node("evaluator", self.workflow_nodes.evaluator_node)
        
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
                "constitucional": "constitucional",
                "administrativo": "administrativo",
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
        workflow.add_edge("constitucional", "evaluator")
        workflow.add_edge("administrativo", "evaluator")
        
        # El evaluador termina el flujo
        workflow.add_edge("evaluator", END)
        
        # Compilar con checkpointer para memoria
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    
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
            "constitucional": "constitucional",
            "administrativo": "administrativo",
            "general": "civil"  # Para casos generales, usar civil
        }
        
        return area_mapping.get(legal_area, "civil")  # Default a civil
