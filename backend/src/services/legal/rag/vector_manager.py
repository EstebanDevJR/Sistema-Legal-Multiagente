import os
import time
import warnings
import logging
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Suprimir warnings específicos de langchain-pinecone
warnings.filterwarnings("ignore", message=".*pydantic_v1.*", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*LangChainDeprecationWarning.*")

load_dotenv()

class VectorManager:
    """Gestor de operaciones con vectorstore Pinecone"""
    
    def __init__(self):
        self.vectorstore = None
        self.pc = None
        
        # Configuraciones optimizadas por tipo de consulta
        self.query_configs = {
            "constitución": {"k": 15, "threshold": 0.25, "boost_keywords": ["sas", "empresa", "constituir", "cámara", "comercio"]},
            "laboral": {"k": 12, "threshold": 0.3, "boost_keywords": ["contrato", "trabajo", "empleado", "prestaciones", "liquidación"]},
            "tributario": {"k": 15, "threshold": 0.3, "boost_keywords": ["impuesto", "dian", "tributario", "renta", "iva"]},
            "contractual": {"k": 10, "threshold": 0.25, "boost_keywords": ["contrato", "cláusula", "obligación", "comercial"]},
            "general": {"k": 10, "threshold": 0.3, "boost_keywords": []}
        }
        
        self.initialize_vectorstore()
    
    def initialize_vectorstore(self):
        """Inicializar Pinecone usando langchain-pinecone de forma robusta"""
        try:
            from langchain_pinecone import PineconeVectorStore
            from langchain_openai import OpenAIEmbeddings
            
            # Inicializar embeddings
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY no encontrada")
            
            embeddings = OpenAIEmbeddings(
                openai_api_key=api_key,
                model="text-embedding-3-small"
            )
            
            # Inicializar vectorstore
            pinecone_api_key = os.getenv("PINECONE_API_KEY")
            if not pinecone_api_key:
                raise ValueError("PINECONE_API_KEY no encontrada")
            
            index_name = os.getenv("PINECONE_INDEX_NAME")
            if not index_name:
                raise ValueError("PINECONE_INDEX_NAME no encontrada")
            
            self.vectorstore = PineconeVectorStore(
                index_name=index_name,
                embedding=embeddings,
                pinecone_api_key=pinecone_api_key,
                text_key="chunk_text"  # Los datos están en el campo chunk_text, no text
            )
            
            # Probar conexión haciendo una búsqueda simple
            test_results = self.vectorstore.similarity_search("test", k=1)
            
            print(f"✅ Vectorstore conectado exitosamente!")
            print(f"   📊 Índice: {index_name}")
            print(f"   🚀 LangChain-Pinecone integración activada")
            
        except Exception as e:
            print(f"⚠️ Error conectando Pinecone: {e}")
            print("🔄 Funcionando en modo básico (sin vectorstore)")
            self.vectorstore = None
    
    def calculate_relevance_score(self, match, category: str, question_lower: str) -> float:
        """Calcular score de relevancia optimizado"""
        base_score = match.score
        metadata = match.metadata or {}
        
        # Boost por tipo de documento
        doc_boosts = {
            "codigo_civil": 1.1,
            "codigo_comercio": 1.15,
            "codigo_sustantivo_trabajo": 1.1,
            "estatuto_tributario": 1.2
        }
        
        doc_boost = 1.0
        filename = metadata.get('filename', '').lower()
        for doc_type, boost in doc_boosts.items():
            if doc_type in filename:
                doc_boost = boost
                break
        
        # Boost por coincidencia de keywords específicos
        content = metadata.get('chunk_text', '').lower()
        config = self.query_configs.get(category, self.query_configs["general"])
        keyword_boost = 1.0
        
        matching_keywords = sum(1 for kw in config["boost_keywords"] if kw in content)
        if matching_keywords > 0:
            keyword_boost = 1.0 + (matching_keywords * 0.05)  # 5% por keyword
        
        # Score final
        final_score = base_score * doc_boost * keyword_boost
        
        return final_score
    
    def _analyze_documents_directly(self, document_ids: List[str], question: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Analizar documentos directamente desde S3 sin usar vector store
        """
        try:
            # Import services needed
            from ...documents.document_service import document_service
            from ...documents.textract_service import textract_service
            
            context_parts = []
            sources = []
            
            logger.info(f"🔍 Direct analysis of {len(document_ids)} documents")
            
            for doc_id in document_ids:
                try:
                    # Buscar el documento en todos los usuarios (simplificado para el ejemplo)
                    # En producción deberías pasar el user_id
                    document_info = None
                    content = None
                    
                    # Buscar en todos los usuarios (temporal)
                    for user_id, user_docs in document_service.documents_db.items():
                        for doc in user_docs:
                            if doc.get('id') == doc_id:
                                document_info = doc
                                # Descargar contenido
                                if document_service.s3_client and doc.get('s3_key'):
                                    # Desde S3
                                    response = document_service.s3_client.get_object(
                                        Bucket=document_service.bucket_name,
                                        Key=doc['s3_key']
                                    )
                                    content = response['Body'].read()
                                elif doc.get('local_path'):
                                    # Desde archivo local
                                    with open(doc['local_path'], 'rb') as f:
                                        content = f.read()
                                break
                        if document_info:
                            break
                    
                    if not document_info:
                        logger.warning(f"⚠️ Document {doc_id} not found")
                        continue
                    
                    # Verificar si ya tenemos el texto en caché
                    cached_data = document_service.get_cached_document_text(doc_id)
                    if cached_data:
                        extracted_text = cached_data['text']
                        extraction_metadata = cached_data['metadata']
                        logger.info(f"🚀 Using cached text for document {doc_id}")
                    else:
                        # No está en caché, necesitamos extraer el texto
                        if not content:
                            logger.warning(f"⚠️ Document {doc_id} has no content available")
                            continue
                        
                        extracted_text, extraction_metadata = textract_service.extract_text_from_content(
                            content=content,
                            content_type=document_info.get('content_type', 'application/octet-stream'),
                            filename=document_info.get('filename', f'document_{doc_id}')
                        )
                        
                        # Cachear el texto extraído para futuras consultas
                        if extracted_text and len(extracted_text.strip()) >= 10:
                            document_service.cache_document_text(doc_id, extracted_text, extraction_metadata)
                    
                    if not extracted_text or len(extracted_text.strip()) < 10:
                        logger.warning(f"⚠️ No text extracted from document {doc_id}")
                        continue
                    
                    # Buscar partes relevantes del texto
                    relevant_parts = self._extract_relevant_parts(extracted_text, question)
                    context_parts.extend(relevant_parts)
                    
                    # Agregar como fuente
                    sources.append({
                        "title": document_info.get('filename', f'Document {doc_id}'),
                        "content": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
                        "document_id": doc_id,
                        "relevance": 0.9,  # Alta relevancia para documentos específicos
                        "source": "direct_analysis",
                        "extraction_method": extraction_metadata.get('extraction_method', 'unknown'),
                        "metadata": {
                            "file_size": len(content),
                            "text_length": len(extracted_text),
                            "content_type": document_info.get('content_type', 'unknown')
                        }
                    })
                    
                    logger.info(f"✅ Successfully analyzed document {doc_id}")
                        
                except Exception as doc_error:
                    logger.error(f"❌ Error analyzing document {doc_id}: {doc_error}")
                    continue
            
            # Combinar contexto
            if context_parts:
                context = "\n\n".join(context_parts)
                logger.info(f"📄 Direct analysis found {len(context)} characters of context from {len(sources)} documents")
                return context, sources
            else:
                logger.warning("⚠️ No content found in direct document analysis")
                return "No se encontró información relevante en los documentos específicos subidos. Verifica que los documentos contengan información relacionada con tu consulta.", []
                
        except Exception as e:
            logger.error(f"❌ Error in direct document analysis: {e}")
            return "Error al analizar los documentos específicos.", []
    
    def _extract_relevant_parts(self, text: str, question: str) -> List[str]:
        """
        Extraer partes del texto que sean relevantes para la pregunta
        """
        import re
        
        # Palabras clave de la pregunta
        question_words = set(re.findall(r'\w+', question.lower()))
        question_words = {word for word in question_words if len(word) > 3}
        
        # Dividir texto en párrafos
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
        
        relevant_parts = []
        
        for paragraph in paragraphs:
            paragraph_lower = paragraph.lower()
            
            # Contar palabras clave en el párrafo
            matches = sum(1 for word in question_words if word in paragraph_lower)
            
            # Si el párrafo tiene suficientes palabras clave, incluirlo
            if matches >= 2 or (len(question_words) <= 2 and matches >= 1):
                relevant_parts.append(paragraph)
            
            # Límite de párrafos para evitar contexto muy largo
            if len(relevant_parts) >= 5:
                break
        
        # Si no se encontraron párrafos relevantes, tomar los primeros
        if not relevant_parts:
            relevant_parts = paragraphs[:3]
        
        return relevant_parts
    
    # NOTA: Los documentos de usuario ya NO se almacenan en Pinecone
    # Solo se usa análisis directo desde S3. El vector store es solo para conocimiento legal general.
    
    def _intelligent_chunking(self, content: str) -> List[str]:
        """
        Chunking inteligente que respeta la estructura del documento legal
        """
        import re
        
        # Dividir por cláusulas, secciones o párrafos
        # Patrones comunes en documentos legales
        patterns = [
            r'\n\s*(CLÁUSULA|CLAUSULA)\s+[IVX\d]+[\.\-\s]',  # CLÁUSULA PRIMERA, SEGUNDA, etc.
            r'\n\s*(ARTÍCULO|ARTICULO)\s+[IVX\d]+[\.\-\s]',  # ARTÍCULO 1, 2, etc.
            r'\n\s*(SEXTA|SEPTIMA|OCTAVA|NOVENA|DECIMA)',     # SEXTA, SÉPTIMA, etc.
            r'\n\s*(PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA)',  # PRIMERA, SEGUNDA, etc.
            r'\n\s*[IVX\d]+[\.\-\s]',                        # Números romanos
            r'\n\s*\d+[\.\-\s]',                             # Números
            r'\n\s*[A-Z][A-Z\s]+:',                          # Títulos en mayúsculas
            r'\n\s*(PROPIEDAD|INTELECTUAL|DERECHOS)',        # Palabras clave importantes
        ]
        
        chunks = []
        current_chunk = ""
        max_chunk_size = 2000  # Aumentar tamaño para mantener cláusulas completas
        
        # Dividir el contenido por líneas para procesar
        lines = content.split('\n')
        
        for line in lines:
            # Verificar si la línea es el inicio de una nueva sección/cláusula
            is_new_section = any(re.search(pattern, f'\n{line}', re.IGNORECASE) for pattern in patterns)
            
            # Si encontramos una nueva sección y el chunk actual es muy grande, guardarlo
            if is_new_section and len(current_chunk) > max_chunk_size:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = line + '\n'
            else:
                current_chunk += line + '\n'
                
                # Si el chunk se vuelve muy grande, forzar división
                if len(current_chunk) > max_chunk_size * 1.5:
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    current_chunk = ""
        
        # Agregar el último chunk si no está vacío
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Si no se encontraron patrones, usar chunking simple pero más grande
        if len(chunks) == 1 and len(chunks[0]) > max_chunk_size:
            logger.info("No se encontraron patrones de estructura, usando chunking simple")
            chunks = [content[i:i+max_chunk_size] for i in range(0, len(content), max_chunk_size)]
        
        logger.info(f"📄 Intelligent chunking: {len(chunks)} chunks created")
        for i, chunk in enumerate(chunks):
            logger.info(f"Chunk {i}: {len(chunk)} chars, preview: {chunk[:200]}...")
            # Buscar si contiene palabras clave importantes
            if any(keyword in chunk.upper() for keyword in ['SEXTA', 'PROPIEDAD', 'INTELECTUAL', 'DERECHOS']):
                logger.info(f"🎯 Chunk {i} contains important keywords!")
        
        return chunks
    
    def search_vectorstore(self, question: str, category: str = "general", document_ids: Optional[List[str]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Buscar en vectorstore optimizado para velocidad
        
        Args:
            question: Pregunta del usuario
            category: Categoría de la consulta
            document_ids: Lista de IDs de documentos específicos a buscar (opcional)
            
        Returns:
            Tupla con contexto y fuentes (cada fuente es un diccionario con title, content, relevance, etc.)
        """
        # Si se especifican document_ids, hacer análisis directo
        if document_ids and len(document_ids) > 0:
            logger.info(f"🔍 Direct document analysis requested for: {document_ids}")
            return self._analyze_documents_directly(document_ids, question)
        
        if not self.vectorstore:
            return "Legislación colombiana aplicable.", [{"title": "Legislación Colombiana", "content": "Documentos legales del sistema", "relevance": 1.0, "filename": "legislacion_colombiana", "metadata": {}}]
        
        try:
            start_time = time.time()
            
            print(f"🔍 VectorManager - document_ids received: {document_ids}")
            print(f"🔍 VectorManager - document_ids type: {type(document_ids)}")
            print(f"🔍 VectorManager - document_ids length: {len(document_ids) if document_ids else 0}")
            
            # Configuración optimizada por categoría
            config = self.query_configs.get(category, self.query_configs["general"])
            k = config["k"]  # Usar el k completo para mejor recuperación
            threshold = config["threshold"]
            
            # Búsqueda optimizada
            if document_ids and len(document_ids) > 0:
                # Buscar solo en documentos específicos con más resultados
                logger.info(f"🔍 Searching in specific documents: {document_ids}")
                # Hacer búsqueda más amplia para encontrar documentos específicos
                results = self.vectorstore.similarity_search_with_score(
                    question,
                    k=k * 5  # Buscar más resultados para encontrar documentos específicos
                )
            else:
                results = self.vectorstore.similarity_search_with_score(
                    question,
                    k=k
                )
            
            # Filtrar y procesar resultados rápidamente
            relevant_chunks = []
            sources = []
            
            logger.info(f"🔍 Found {len(results)} total results, filtering by document_ids: {document_ids}")
            
            for doc, score in results:
                # Pinecone devuelve scores de similitud (más alto = más similar)
                # Convertir a distancia si es necesario (más bajo = más similar)
                similarity_score = 1 - score if score > 1 else score
                
                # Filtrar por document_ids si se proporcionan
                if document_ids and len(document_ids) > 0:
                    metadata = doc.metadata or {}
                    
                    # Intentar múltiples formas de obtener el document_id
                    doc_id = (
                        metadata.get('document_id') or 
                        metadata.get('id') or 
                        metadata.get('doc_id') or
                        metadata.get('source_id')
                    )
                    
                    # Debug: mostrar todos los metadatos disponibles si doc_id es None
                    if doc_id is None:
                        logger.warning(f"⚠️ No document_id found in metadata. Available keys: {list(metadata.keys())}")
                        logger.warning(f"⚠️ Metadata content: {metadata}")
                        # Intentar buscar cualquier UUID-like string en los valores
                        for key, value in metadata.items():
                            if isinstance(value, str) and len(value) == 36 and '-' in value:
                                logger.info(f"🔍 Found potential document_id in {key}: {value}")
                                doc_id = value
                                break
                    
                    print(f"🔍 Checking document {doc_id} against filter {document_ids}")
                    logger.info(f"🔍 Checking document {doc_id} against filter {document_ids}")
                    
                    # Verificar si el documento está en la lista de documentos específicos
                    if doc_id is None or doc_id not in document_ids:
                        print(f"⏭️ Skipping document {doc_id} - not in filter list")
                        logger.info(f"⏭️ Skipping document {doc_id} - not in filter list")
                        continue  # Saltar este documento si no está en la lista
                    else:
                        print(f"✅ Document {doc_id} matches filter")
                        logger.info(f"✅ Document {doc_id} matches filter")
                
                if similarity_score >= threshold:
                    relevant_chunks.append(doc.page_content)
                    
                    # Extraer fuente del metadata
                    metadata = doc.metadata or {}
                    filename = metadata.get('filename', 'Documento legal')
                    chunk_text = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                    
                    # Crear diccionario de fuente compatible con QueryResponse
                    source_dict = {
                        "title": filename,
                        "content": chunk_text,
                        "relevance": round(1 - similarity_score, 3),
                        "filename": filename,
                        "metadata": {
                            **metadata,
                            "source": "user_upload" if document_ids and len(document_ids) > 0 else "system"
                        }
                    }
                    sources.append(source_dict)
            
            # Usar más contexto para mejor calidad de respuestas
            if document_ids and len(document_ids) > 0:
                # Para documentos específicos, usar más contexto
                context = " ".join(relevant_chunks[:8])  # Hasta 8 chunks para documentos específicos
                if len(context) > 5000:  # Aumentar límite para documentos específicos
                    context = context[:5000] + "..."
            else:
                # Para búsqueda general, usar más contexto también
                context = " ".join(relevant_chunks[:6])  # Aumentar a 6 chunks
                if len(context) > 3000:  # Aumentar límite general
                    context = context[:3000] + "..."
            
            # Si se especificaron documentos específicos pero no se encontraron resultados
            if document_ids and len(document_ids) > 0 and len(relevant_chunks) == 0:
                logger.warning(f"⚠️ No results found in specified documents: {document_ids}")
                logger.warning(f"⚠️ Total results before filtering: {len(results)}")
                logger.warning(f"⚠️ Threshold used: {threshold}")
                
                # Intentar con un threshold más bajo para documentos específicos
                logger.info("🔄 Retrying with lower threshold for specific documents...")
                for doc, score in results:
                    metadata = doc.metadata or {}
                    doc_id = metadata.get('document_id') or metadata.get('id')
                    if doc_id in document_ids:
                        similarity_score = 1 - score if score > 1 else score
                        if similarity_score >= 0.2:  # Threshold más bajo
                            relevant_chunks.append(doc.page_content)
                            filename = metadata.get('filename', 'Documento legal')
                            chunk_text = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                            
                            source_dict = {
                                "title": filename,
                                "content": chunk_text,
                                "relevance": round(1 - similarity_score, 3),
                                "filename": filename,
                                "metadata": {
                                    **metadata,
                                    "source": "user_upload"
                                }
                            }
                            sources.append(source_dict)
                            logger.info(f"✅ Found document {doc_id} with lower threshold: {similarity_score}")
                
                if len(relevant_chunks) == 0:
                    return "No se encontró información relevante en los documentos específicos subidos. Verifica que los documentos contengan información relacionada con tu consulta.", []
            
            search_time = int((time.time() - start_time) * 1000)
            logger.info(f"🔍 Vector search completed in {search_time}ms")
            logger.info(f"📊 Results: {len(relevant_chunks)} relevant chunks, {len(sources)} sources")
            if document_ids:
                logger.info(f"📄 Filtered by document_ids: {document_ids}")
            
            return context, sources[:5]  # Aumentar a máximo 5 fuentes para más información
            
        except Exception as e:
            print(f"❌ Error en búsqueda vectorial: {e}")
            return "Legislación colombiana aplicable.", [{"title": "Legislación Colombiana", "content": "Documentos legales del sistema", "relevance": 1.0, "filename": "legislacion_colombiana", "metadata": {}}]
    
    def get_vectorstore_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del vectorstore"""
        if not self.vectorstore:
            return {"status": "disconnected", "error": "Vectorstore no inicializado"}
        
        try:
            # Intentar obtener estadísticas básicas
            test_results = self.vectorstore.similarity_search("test", k=1)
            
            return {
                "status": "connected",
                "index_name": os.getenv("PINECONE_INDEX_NAME"),
                "embedding_model": "text-embedding-3-small",
                "text_key": "chunk_text",
                "test_results": len(test_results) > 0
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e)
            }
    
    def test_connection(self) -> bool:
        """Prueba la conexión con el vectorstore"""
        if not self.vectorstore:
            return False
        
        try:
            results = self.vectorstore.similarity_search("test legal", k=1)
            return len(results) > 0
        except Exception:
            return False 