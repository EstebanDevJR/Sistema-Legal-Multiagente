"""
Servicio de caché simple para consultas frecuentes
"""

import hashlib
import time
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class QueryCacheService:
    """Servicio de caché en memoria para consultas frecuentes"""
    
    def __init__(self, max_size: int = 100, ttl_hours: int = 24):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl_hours = ttl_hours
        
    def _generate_cache_key(self, question: str, context_hash: str = "") -> str:
        """Generar clave única para la consulta"""
        # Normalizar la pregunta
        normalized_question = question.lower().strip()
        
        # Crear hash de la pregunta + contexto
        content = f"{normalized_question}|{context_hash}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """Verificar si una entrada del caché ha expirado"""
        created_at = datetime.fromisoformat(cache_entry["created_at"])
        expiry_time = created_at + timedelta(hours=self.ttl_hours)
        return datetime.now() > expiry_time
    
    def get(self, question: str, context_hash: str = "") -> Optional[Dict[str, Any]]:
        """Obtener respuesta del caché si existe"""
        try:
            cache_key = self._generate_cache_key(question, context_hash)
            
            if cache_key not in self.cache:
                return None
                
            cache_entry = self.cache[cache_key]
            
            # Verificar si ha expirado
            if self._is_expired(cache_entry):
                del self.cache[cache_key]
                logger.info(f"🗑️ Cache entry expired and removed: {cache_key[:8]}...")
                return None
            
            # Actualizar último acceso
            cache_entry["last_accessed"] = datetime.now().isoformat()
            cache_entry["access_count"] += 1
            
            logger.info(f"✅ Cache hit for query: {question[:50]}...")
            return cache_entry["response"]
            
        except Exception as e:
            logger.error(f"❌ Error getting from cache: {e}")
            return None
    
    def set(self, question: str, response: Dict[str, Any], context_hash: str = "") -> None:
        """Guardar respuesta en el caché"""
        try:
            cache_key = self._generate_cache_key(question, context_hash)
            
            # Si el caché está lleno, eliminar la entrada menos usada
            if len(self.cache) >= self.max_size:
                self._evict_least_used()
            
            # Crear entrada del caché
            cache_entry = {
                "response": response,
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "access_count": 1,
                "question_preview": question[:100]
            }
            
            self.cache[cache_key] = cache_entry
            logger.info(f"💾 Cached response for query: {question[:50]}...")
            
        except Exception as e:
            logger.error(f"❌ Error setting cache: {e}")
    
    def _evict_least_used(self) -> None:
        """Eliminar la entrada menos usada del caché"""
        if not self.cache:
            return
            
        # Encontrar la entrada con menor acceso y más antigua
        least_used_key = min(
            self.cache.keys(),
            key=lambda k: (
                self.cache[k]["access_count"],
                self.cache[k]["last_accessed"]
            )
        )
        
        del self.cache[least_used_key]
        logger.info(f"🗑️ Evicted least used cache entry: {least_used_key[:8]}...")
    
    def clear_expired(self) -> int:
        """Limpiar entradas expiradas del caché"""
        expired_keys = []
        
        for key, entry in self.cache.items():
            if self._is_expired(entry):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"🧹 Cleared {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del caché"""
        total_entries = len(self.cache)
        total_accesses = sum(entry["access_count"] for entry in self.cache.values())
        
        return {
            "total_entries": total_entries,
            "max_size": self.max_size,
            "total_accesses": total_accesses,
            "average_accesses": total_accesses / total_entries if total_entries > 0 else 0,
            "ttl_hours": self.ttl_hours
        }
    
    def should_cache_query(self, question: str, response: Dict[str, Any]) -> bool:
        """Determinar si una consulta debe ser cacheada"""
        # No cachear consultas muy específicas o con baja confianza
        if response.get("confidence", 0) < 0.7:
            return False
        
        # No cachear preguntas muy cortas o muy largas
        if len(question.strip()) < 10 or len(question.strip()) > 500:
            return False
        
        # No cachear si la respuesta indica error
        if "error" in response.get("metadata", {}):
            return False
        
        return True


# Instancia global del servicio de caché
query_cache = QueryCacheService(max_size=50, ttl_hours=12)  # Caché más pequeño y TTL más corto
