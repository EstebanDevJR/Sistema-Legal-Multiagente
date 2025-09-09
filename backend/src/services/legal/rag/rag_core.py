"""
Core RAG functionality - integrates all RAG components
"""

from typing import Dict, Any, List, Optional, Tuple
from .vector_manager import VectorManager
from .query_processor import QueryProcessor

class RAGCore:
    """Core RAG system that orchestrates query processing and vector search"""
    
    def __init__(self):
        self.vector_manager = VectorManager()
        self.query_processor = QueryProcessor()
    
    async def process_query(
        self, 
        question: str, 
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Process a legal query through the RAG pipeline
        
        Args:
            question: User's question
            user_id: User identifier
            
        Returns:
            Processed query result
        """
        # Determine category and preprocess
        category = self.query_processor.determine_query_category(question)
        complexity = self.query_processor.get_query_complexity(question)
        processed_question = self.query_processor.preprocess_query(question, category)
        
        # Search vector store
        context, sources = self.vector_manager.search_vectorstore(processed_question, category)
        
        # Generate related queries
        suggestions = self.query_processor.get_related_queries(question, category)
        
        return {
            "context": context,
            "sources": sources,
            "category": category,
            "complexity": complexity,
            "suggestions": suggestions,
            "processed_question": processed_question,
            "original_question": question,
            "user_id": user_id
        }

# Global instance
rag_core = RAGCore()
