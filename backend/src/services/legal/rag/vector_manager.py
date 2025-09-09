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
            "constitución": {"k": 7, "threshold": 0.4, "boost_keywords": ["sas", "empresa", "constituir", "cámara", "comercio"]},
            "laboral": {"k": 6, "threshold": 0.45, "boost_keywords": ["contrato", "trabajo", "empleado", "prestaciones", "liquidación"]},
            "tributario": {"k": 8, "threshold": 0.5, "boost_keywords": ["impuesto", "dian", "tributario", "renta", "iva"]},
            "contractual": {"k": 5, "threshold": 0.4, "boost_keywords": ["contrato", "cláusula", "obligación", "comercial"]},
            "general": {"k": 5, "threshold": 0.5, "boost_keywords": []}
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
    
    async def add_document_to_vectorstore(self, document_id: str, content: str, filename: str, user_id: str) -> bool:
        """
        Agregar un documento al vector store para búsquedas
        
        Args:
            document_id: ID único del documento
            content: Contenido del documento
            filename: Nombre del archivo
            user_id: ID del usuario
            
        Returns:
            True si se agregó exitosamente, False en caso contrario
        """
        if not self.vectorstore:
            logger.warning("Vector store not initialized, cannot add document")
            return False
        
        try:
            # Dividir el contenido en chunks inteligentes que respeten la estructura del documento
            chunks = self._intelligent_chunking(content)
            
            # Crear documentos para el vector store usando Document de LangChain
            from langchain_core.documents import Document
            
            documents = []
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "document_id": document_id,
                        "id": document_id,  # Para compatibilidad con el filtrado
                        "filename": filename,
                        "user_id": user_id,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "source": "user_upload"
                    }
                )
                documents.append(doc)
            
            # Agregar al vector store
            logger.info(f"🔄 Adding {len(documents)} document chunks to vector store...")
            self.vectorstore.add_documents(documents)
            logger.info(f"✅ Document {document_id} added to vector store with {len(chunks)} chunks")
            
            # Verificar que se agregó correctamente
            test_results = self.vectorstore.similarity_search_with_score(
                f"document_id:{document_id}", k=1
            )
            logger.info(f"🔍 Test search for document {document_id}: {len(test_results)} results")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding document to vector store: {e}")
            return False
    
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
        if not self.vectorstore:
            if document_ids and len(document_ids) > 0:
                return "No se encontró información en los documentos específicos.", []
            return "Legislación colombiana aplicable.", [{"title": "Legislación Colombiana", "content": "Documentos legales del sistema", "relevance": 1.0, "filename": "legislacion_colombiana", "metadata": {}}]
        
        try:
            start_time = time.time()
            
            print(f"🔍 VectorManager - document_ids received: {document_ids}")
            print(f"🔍 VectorManager - document_ids type: {type(document_ids)}")
            print(f"🔍 VectorManager - document_ids length: {len(document_ids) if document_ids else 0}")
            
            # Configuración optimizada por categoría
            config = self.query_configs.get(category, self.query_configs["general"])
            k = min(config["k"], 4)  # Reducir k para mayor velocidad
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
                    doc_id = metadata.get('document_id') or metadata.get('id')
                    print(f"🔍 Checking document {doc_id} against filter {document_ids}")
                    logger.info(f"🔍 Checking document {doc_id} against filter {document_ids}")
                    
                    # Verificar si el documento está en la lista de documentos específicos
                    if doc_id not in document_ids:
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
            
            # Limitar contexto para velocidad pero permitir más contenido para documentos específicos
            if document_ids and len(document_ids) > 0:
                # Para documentos específicos, usar más contexto
                context = " ".join(relevant_chunks[:5])  # Hasta 5 chunks para documentos específicos
                if len(context) > 3000:  # Aumentar límite para documentos específicos
                    context = context[:3000] + "..."
            else:
                # Para búsqueda general, mantener límite más bajo
                context = " ".join(relevant_chunks[:3])  # Solo primeros 3 chunks
                if len(context) > 1500:
                    context = context[:1500] + "..."
            
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
            
            return context, sources[:3]  # Máximo 3 fuentes
            
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