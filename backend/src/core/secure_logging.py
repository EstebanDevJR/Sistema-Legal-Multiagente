"""
Módulo de logging seguro para evitar exposición de información sensible
"""

import logging
import re
import os
from typing import Any, Dict, List, Optional
from functools import wraps

class SecureLogger:
    """
    Logger que sanitiza automáticamente información sensible
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        
        # Patrones de información sensible a sanitizar
        self.sensitive_patterns = [
            # API Keys y tokens
            (r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-]{20,})(["\']?)', r'\1***REDACTED***\3'),
            (r'(token["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-\.]{20,})(["\']?)', r'\1***REDACTED***\3'),
            (r'(password["\']?\s*[:=]\s*["\']?)([^"\']+)(["\']?)', r'\1***REDACTED***\3'),
            (r'(secret["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-]{10,})(["\']?)', r'\1***REDACTED***\3'),
            
            # Emails
            (r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', r'***@***.***'),
            
            # Números de teléfono (formato colombiano)
            (r'(\+?57\s?)?[0-9]{3}\s?[0-9]{3}\s?[0-9]{4}', r'***-***-****'),
            
            # Cédulas y documentos
            (r'\b[0-9]{6,12}\b', r'***DOCUMENT***'),
            
            # Rutas de archivos con información personal
            (r'([/\\][^/\\]*[/\\])([^/\\]+\.(pdf|doc|docx|txt|jpg|png))', r'\1***FILE***'),
            
            # IDs de sesión largos
            (r'\b[a-f0-9]{8,}\b', r'***ID***'),
        ]
        
        # Palabras clave que indican contenido sensible
        self.sensitive_keywords = [
            'contrato', 'acuerdo', 'clausula', 'obligacion', 'derecho',
            'demanda', 'demandado', 'demandante', 'sentencia', 'fallo',
            'testamento', 'herencia', 'matrimonio', 'divorcio', 'custodia',
            'salario', 'prestaciones', 'liquidacion', 'despido', 'renuncia',
            'impuesto', 'declaracion', 'renta', 'iva', 'dian'
        ]
    
    def _sanitize_message(self, message: str) -> str:
        """Sanitizar mensaje removiendo información sensible"""
        if not isinstance(message, str):
            return str(message)
        
        sanitized = message
        
        # Aplicar patrones de regex
        for pattern, replacement in self.sensitive_patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        # Detectar contenido legal sensible
        message_lower = sanitized.lower()
        if any(keyword in message_lower for keyword in self.sensitive_keywords):
            # Si contiene palabras legales sensibles, truncar o redactar
            if len(sanitized) > 100:
                sanitized = sanitized[:100] + "... [CONTENT REDACTED]"
        
        return sanitized
    
    def _sanitize_args(self, args: tuple) -> tuple:
        """Sanitizar argumentos del log"""
        sanitized_args = []
        for arg in args:
            if isinstance(arg, str):
                sanitized_args.append(self._sanitize_message(arg))
            elif isinstance(arg, dict):
                sanitized_args.append(self._sanitize_dict(arg))
            elif isinstance(arg, list):
                sanitized_args.append(self._sanitize_list(arg))
            else:
                sanitized_args.append(arg)
        return tuple(sanitized_args)
    
    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitizar diccionario removiendo campos sensibles"""
        sensitive_keys = [
            'password', 'token', 'api_key', 'secret', 'key', 'auth',
            'email', 'phone', 'document', 'cedula', 'file_path', 'filename',
            'content', 'text', 'transcription', 'query', 'question'
        ]
        
        sanitized = {}
        for key, value in data.items():
            key_lower = key.lower()
            
            # Redactar campos sensibles
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                if isinstance(value, str) and len(value) > 20:
                    sanitized[key] = f"[{key.upper()} REDACTED - {len(value)} chars]"
                else:
                    sanitized[key] = f"[{key.upper()} REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = self._sanitize_list(value)
            elif isinstance(value, str):
                sanitized[key] = self._sanitize_message(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _sanitize_list(self, data: List[Any]) -> List[Any]:
        """Sanitizar lista"""
        return [self._sanitize_message(item) if isinstance(item, str) else item for item in data]
    
    def info(self, message: str, *args, **kwargs):
        """Log info sanitizado"""
        sanitized_message = self._sanitize_message(message)
        sanitized_args = self._sanitize_args(args)
        self.logger.info(sanitized_message, *sanitized_args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning sanitizado"""
        sanitized_message = self._sanitize_message(message)
        sanitized_args = self._sanitize_args(args)
        self.logger.warning(sanitized_message, *sanitized_args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error sanitizado"""
        sanitized_message = self._sanitize_message(message)
        sanitized_args = self._sanitize_args(args)
        self.logger.error(sanitized_message, *sanitized_args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug sanitizado"""
        sanitized_message = self._sanitize_message(message)
        sanitized_args = self._sanitize_args(args)
        self.logger.debug(sanitized_message, *sanitized_args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical sanitizado"""
        sanitized_message = self._sanitize_message(message)
        sanitized_args = self._sanitize_args(args)
        self.logger.critical(sanitized_message, *sanitized_args, **kwargs)

def secure_logger(name: str) -> SecureLogger:
    """Factory function para crear logger seguro"""
    return SecureLogger(name)

def log_sensitive_operation(operation_name: str):
    """Decorator para loggear operaciones sensibles de forma segura"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = secure_logger(func.__module__)
            logger.info(f"Starting {operation_name}")
            try:
                result = await func(*args, **kwargs)
                logger.info(f"Completed {operation_name} successfully")
                return result
            except Exception as e:
                logger.error(f"Failed {operation_name}: {str(e)}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = secure_logger(func.__module__)
            logger.info(f"Starting {operation_name}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Completed {operation_name} successfully")
                return result
            except Exception as e:
                logger.error(f"Failed {operation_name}: {str(e)}")
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Importar asyncio para el decorator
import asyncio
