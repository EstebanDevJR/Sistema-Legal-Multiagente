import re
from typing import Dict, Any, List, Optional

class QueryProcessor:
    """Procesador especializado de consultas legales"""
    
    def __init__(self):
        # Configuraciones optimizadas por tipo de consulta  
        self.query_configs = {
            "constitución": {"k": 15, "threshold": 0.25, "boost_keywords": ["sas", "empresa", "constituir", "cámara", "comercio", "sociedad", "registro", "mercantil", "documentos", "requisitos", "pasos"]},
            "laboral": {"k": 12, "threshold": 0.3, "boost_keywords": ["contrato", "trabajo", "empleado", "prestaciones", "liquidación", "salario", "derechos", "obligaciones"]},
            "tributario": {"k": 15, "threshold": 0.3, "boost_keywords": ["impuesto", "dian", "tributario", "renta", "iva", "declaración", "régimen", "obligaciones"]},
            "contractual": {"k": 10, "threshold": 0.25, "boost_keywords": ["contrato", "cláusula", "obligación", "comercial", "acuerdo", "términos", "condiciones"]},
            "general": {"k": 10, "threshold": 0.3, "boost_keywords": []}
        }
        
        # Palabras clave por categoría
        self.category_keywords = {
            "constitución": [
                "constituir", "empresa", "sociedad", "sas", "limitada", "ltda",
                "cámara", "comercio", "registro", "mercantil", "socios", "accionistas"
            ],
            "laboral": [
                "empleado", "trabajador", "contrato", "trabajo", "salario", "sueldo",
                "prestaciones", "liquidación", "despido", "vacaciones", "incapacidad",
                "seguridad", "social", "eps", "afp", "arl"
            ],
            "tributario": [
                "impuesto", "tributario", "dian", "renta", "iva", "retefuente",
                "declaración", "régimen", "simple", "tributación", "deducción"
            ],
            "contractual": [
                "contrato", "acuerdo", "cláusula", "obligación", "derecho",
                "comercial", "civil", "arrendamiento", "compraventa", "servicios"
            ]
        }
    
    def determine_query_category(self, question: str) -> str:
        """
        Determinar la categoría de una consulta legal
        
        Args:
            question: Pregunta del usuario
            
        Returns:
            Categoría determinada
        """
        question_lower = question.lower()
        category_scores = {}
        
        # Calcular score por categoría basado en keywords
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                # Buscar palabra completa
                if re.search(r'\b' + re.escape(keyword) + r'\b', question_lower):
                    score += 1
                # Buscar coincidencias parciales (menos peso)
                elif keyword in question_lower:
                    score += 0.5
            
            if score > 0:
                category_scores[category] = score
        
        if not category_scores:
            return "general"
        
        # Retornar categoría con mayor score
        best_category = max(category_scores.items(), key=lambda x: x[1])
        
        print(f"🏷️ Categoría detectada: {best_category[0]} (score: {best_category[1]})")
        return best_category[0]
    
    def determine_query_type(self, question: str) -> str:
        """
        Determinar el tipo específico de consulta
        
        Args:
            question: Pregunta del usuario
            
        Returns:
            Tipo de consulta
        """
        question_lower = question.lower()
        
        # Patrones de tipo de consulta
        type_patterns = {
            "procedimiento": ["cómo", "como", "pasos", "proceso", "procedimiento", "qué hacer"],
            "definición": ["qué es", "que es", "definición", "significa", "concepto"],
            "requisitos": ["requisitos", "necesito", "documentos", "papeles", "exigencias"],
            "costos": ["costo", "precio", "cuánto", "cuanto", "valor", "tarifa"],
            "plazos": ["plazo", "tiempo", "cuándo", "cuando", "fecha", "término"],
            "consecuencias": ["pasa si", "consecuencias", "sanciones", "multas", "penalidades"],
            "derechos": ["derechos", "tengo derecho", "puede", "permitido", "legal"],
            "obligaciones": ["obligaciones", "debo", "tengo que", "obligatorio", "deber"]
        }
        
        type_scores = {}
        
        for query_type, patterns in type_patterns.items():
            score = sum(1 for pattern in patterns if pattern in question_lower)
            if score > 0:
                type_scores[query_type] = score
        
        if not type_scores:
            return "consulta_general"
        
        best_type = max(type_scores.items(), key=lambda x: x[1])
        return best_type[0]
    
    def preprocess_query(self, question: str, category: str) -> str:
        """
        Preprocesar consulta para mejor matching vectorial
        
        Args:
            question: Consulta original
            category: Categoría determinada
            
        Returns:
            Consulta procesada
        """
        # 1. Limpiar y normalizar
        processed = question.lower().strip()
        processed = re.sub(r'[¿?¡!]', '', processed)
        processed = re.sub(r'\s+', ' ', processed)
        
        # 2. Expandir abreviaciones comunes
        abbreviations = {
            "sas": "sociedad por acciones simplificada",
            "ltda": "sociedad limitada",
            "iva": "impuesto al valor agregado",
            "pyme": "pequeña y mediana empresa",
            "microempresa": "micro empresa pequeña",
        }
        
        for abbr, full in abbreviations.items():
            processed = re.sub(r'\b' + abbr + r'\b', full, processed)
        
        # 3. Agregar keywords relevantes según categoría
        config = self.query_configs.get(category, self.query_configs["general"])
        boost_keywords = config["boost_keywords"]
        
        if boost_keywords:
            # Agregar más keywords que no estén ya presentes para mejor recuperación
            missing_keywords = [kw for kw in boost_keywords[:4] if kw not in processed]
            if missing_keywords:
                processed += " " + " ".join(missing_keywords)
        
        # 4. Asegurar contexto colombiano
        colombia_keywords = ["colombia", "colombiano", "colombiana"]
        if not any(keyword in processed for keyword in colombia_keywords):
            processed += " colombia legislación colombiana"
        
        return processed
    
    def extract_key_entities(self, question: str) -> Dict[str, List[str]]:
        """
        Extraer entidades clave de la consulta
        
        Args:
            question: Pregunta del usuario
            
        Returns:
            Diccionario con entidades extraídas
        """
        question_lower = question.lower()
        entities = {
            "company_types": [],
            "legal_concepts": [],
            "processes": [],
            "amounts": [],
            "dates": []
        }
        
        # Tipos de empresa
        company_patterns = {
            "sas": ["sas", "sociedad por acciones simplificada"],
            "ltda": ["ltda", "limitada", "sociedad limitada"],
            "sa": ["s.a.", "sociedad anónima"],
            "eu": ["empresa unipersonal"],
            "cooperativa": ["cooperativa"]
        }
        
        for company_type, patterns in company_patterns.items():
            if any(pattern in question_lower for pattern in patterns):
                entities["company_types"].append(company_type)
        
        # Conceptos legales comunes
        legal_concepts = [
            "contrato", "liquidación", "prestaciones", "seguridad social",
            "impuesto", "declaración", "registro mercantil", "marca"
        ]
        
        for concept in legal_concepts:
            if concept in question_lower:
                entities["legal_concepts"].append(concept)
        
        # Procesos
        processes = [
            "constituir", "liquidar", "despedir", "contratar", "registrar",
            "declarar", "presentar", "solicitar"
        ]
        
        for process in processes:
            if process in question_lower:
                entities["processes"].append(process)
        
        # Cantidades (básico)
        import re
        amounts = re.findall(r'\$?[\d,]+\.?\d*', question)
        entities["amounts"] = amounts
        
        # Fechas/plazos (básico)
        date_patterns = [
            r'\d{1,2}\s+de\s+\w+',  # "15 de enero"
            r'\d{1,2}/\d{1,2}/\d{4}',  # "15/01/2024"
            r'\d+\s+días?',  # "30 días"
            r'\d+\s+meses?',  # "6 meses"
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, question, re.IGNORECASE)
            entities["dates"].extend(matches)
        
        return entities
    
    def get_query_complexity(self, question: str) -> str:
        """
        Determinar la complejidad de la consulta
        
        Args:
            question: Pregunta del usuario
            
        Returns:
            Nivel de complejidad (simple, medium, complex)
        """
        # Indicadores de complejidad
        complexity_indicators = {
            "simple": [
                "qué es", "que es", "definición", "significa",
                "cuánto", "cuanto", "costo", "precio"
            ],
            "complex": [
                "cómo hacer", "como hacer", "procedimiento", "pasos",
                "requisitos", "documentos", "proceso completo",
                "implicaciones", "consecuencias", "alternativas"
            ]
        }
        
        question_lower = question.lower()
        
        # Contar palabras
        word_count = len(question.split())
        
        # Complejidad por longitud
        if word_count <= 5:
            length_complexity = "simple"
        elif word_count <= 15:
            length_complexity = "medium"
        else:
            length_complexity = "complex"
        
        # Complejidad por indicadores
        for level, indicators in complexity_indicators.items():
            if any(indicator in question_lower for indicator in indicators):
                # Si hay indicadores explícitos, usar ese nivel
                if level == "complex" or length_complexity == "simple":
                    return level
        
        return length_complexity
    
    def get_related_queries(self, question: str, category: str) -> List[str]:
        """
        Generar consultas relacionadas
        
        Args:
            question: Pregunta original
            category: Categoría de la consulta
            
        Returns:
            Lista de consultas relacionadas
        """
        related_queries = {
            "constitución": [
                "¿Cuáles son los requisitos para constituir una SAS?",
                "¿Qué documentos necesito para registrar mi empresa?",
                "¿Cuánto cuesta constituir una sociedad en Colombia?",
                "¿Cuál es la diferencia entre SAS y Ltda?"
            ],
            "laboral": [
                "¿Cuáles son las prestaciones sociales obligatorias?",
                "¿Cómo calcular la liquidación de un empleado?",
                "¿Qué pasos seguir para despedir un trabajador?",
                "¿Cuáles son las obligaciones del empleador?"
            ],
            "tributario": [
                "¿Cómo presentar la declaración de renta?",
                "¿Qué deducciones puedo aplicar?",
                "¿Cuál es la diferencia entre régimen simple y ordinario?",
                "¿Cómo calcular el IVA?"
            ],
            "contractual": [
                "¿Cómo redactar un contrato de trabajo?",
                "¿Qué cláusulas debe tener un contrato comercial?",
                "¿Cómo terminar un contrato legalmente?",
                "¿Qué hacer si incumplen un contrato?"
            ]
        }
        
        return related_queries.get(category, [
            "¿Cuáles son mis obligaciones legales?",
            "¿Qué derechos tengo?",
            "¿Cómo resolver conflictos legales?",
            "¿Dónde buscar asesoría legal?"
        ]) 