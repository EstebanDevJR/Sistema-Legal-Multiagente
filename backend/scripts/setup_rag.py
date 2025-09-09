#!/usr/bin/env python3
"""
Script para configurar RAG con Pinecone usando documentos legales colombianos
Uso: python setup_rag.py --mode [import|verify|clear]
"""

import os
import argparse
import json
from pathlib import Path
from typing import List, Dict

import pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain.schema import Document

def setup_pinecone():
    """Configurar conexión a Pinecone"""
    pinecone.init(
        api_key=os.getenv("PINECONE_API_KEY"),
        environment=os.getenv("PINECONE_ENVIRONMENT")
    )
    return pinecone.Index(os.getenv("PINECONE_INDEX_NAME"))

def load_legal_documents(data_dir: str) -> List[Document]:
    """Cargar documentos legales desde directorio organizado por áreas"""
    documents = []
    
    # Mapeo de áreas legales
    legal_areas = {
        "civil": "Derecho Civil",
        "comercial": "Derecho Comercial", 
        "laboral": "Derecho Laboral",
        "tributario": "Derecho Tributario"
    }
    
    for area_dir in Path(data_dir).iterdir():
        if area_dir.is_dir():
            area_name = area_dir.name
            legal_area = legal_areas.get(area_name, area_name.title())
            
            print(f"📁 Procesando área: {legal_area}")
            
            # Cargar archivos de texto
            for txt_file in area_dir.glob("*.txt"):
                try:
                    loader = TextLoader(str(txt_file), encoding="utf-8")
                    docs = loader.load()
                    for doc in docs:
                        doc.metadata.update({
                            "area": area_name,
                            "legal_area": legal_area,
                            "file_type": "text",
                            "source_file": txt_file.name
                        })
                    documents.extend(docs)
                    print(f"  ✅ {txt_file.name}")
                except Exception as e:
                    print(f"  ❌ Error cargando {txt_file.name}: {e}")
            
            # Cargar archivos PDF
            for pdf_file in area_dir.glob("*.pdf"):
                try:
                    loader = PyPDFLoader(str(pdf_file))
                    docs = loader.load()
                    for doc in docs:
                        doc.metadata.update({
                            "area": area_name,
                            "legal_area": legal_area,
                            "file_type": "pdf",
                            "source_file": pdf_file.name
                        })
                    documents.extend(docs)
                    print(f"  ✅ {pdf_file.name}")
                except Exception as e:
                    print(f"  ❌ Error cargando {pdf_file.name}: {e}")
    
    return documents

def process_documents(documents: List[Document]) -> List[Document]:
    """Procesar y dividir documentos en chunks optimizados para RAG legal"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Tamaño optimizado para consultas legales
        chunk_overlap=200,  # Overlap para mantener contexto
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]  # Separadores para documentos legales
    )
    
    processed_docs = text_splitter.split_documents(documents)
    
    # Agregar metadatos adicionales a cada chunk
    for i, doc in enumerate(processed_docs):
        doc.metadata.update({
            "chunk_id": i,
            "chunk_type": "legal_document",
            "language": "es",
            "country": "colombia"
        })
    
    return processed_docs

def import_to_pinecone(documents: List[Document], index):
    """Importar documentos legales a Pinecone"""
    embeddings = OpenAIEmbeddings()
    
    print(f"🚀 Iniciando importación de {len(documents)} chunks...")
    
    # Procesar en lotes para evitar límites de API
    batch_size = 50  # Tamaño de lote optimizado
    total_batches = (len(documents) - 1) // batch_size + 1
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        batch_num = i // batch_size + 1
        
        print(f"📦 Procesando lote {batch_num}/{total_batches} ({len(batch)} chunks)...")
        
        try:
            # Generar embeddings
            texts = [doc.page_content for doc in batch]
            vectors = embeddings.embed_documents(texts)
            
            # Preparar vectores para Pinecone
            vectors_to_upsert = []
            for j, (doc, vector) in enumerate(zip(batch, vectors)):
                vector_id = f"{doc.metadata['area']}_{doc.metadata['chunk_id']}"
                
                vectors_to_upsert.append({
                    "id": vector_id,
                    "values": vector,
                    "metadata": {
                        # Campos requeridos por el sistema RAG
                        "chunk_text": doc.page_content,  # Campo principal para búsqueda
                        "filename": doc.metadata["source_file"],  # Para títulos en respuestas
                        "document_id": vector_id,  # Para filtrado por documentos
                        "id": vector_id,  # Alias para compatibilidad
                        
                        # Metadatos adicionales para organización
                        "area": doc.metadata["area"],
                        "legal_area": doc.metadata["legal_area"],
                        "source_file": doc.metadata["source_file"],
                        "file_type": doc.metadata["file_type"],
                        "chunk_id": doc.metadata["chunk_id"],
                        "chunk_type": "legal_document",
                        "language": "es",
                        "country": "colombia",
                        
                        # Metadatos para el sistema de agentes
                        "source": "system_legal_docs",
                        "user_id": "system"
                    }
                })
            
            # Subir a Pinecone
            index.upsert(vectors=vectors_to_upsert)
            print(f"  ✅ Lote {batch_num} importado exitosamente")
            
        except Exception as e:
            print(f"  ❌ Error en lote {batch_num}: {e}")
            continue
    
    print("🎉 Importación completada!")

def verify_index(index):
    """Verificar contenido del índice y mostrar estadísticas"""
    try:
        stats = index.describe_index_stats()
        print(f"📊 Estadísticas del índice:")
        print(f"   - Total vectores: {stats.total_vector_count}")
        print(f"   - Dimensiones: {stats.dimension}")
        print(f"   - Namespaces: {list(stats.namespaces.keys())}")
        
        # Verificar distribución por área legal
        print(f"\n🔍 Verificando distribución por área legal...")
        areas = ["civil", "comercial", "laboral", "tributario"]
        
        for area in areas:
            try:
                # Query de prueba para cada área
                test_query = [0.0] * 1536  # Vector de prueba
                results = index.query(
                    vector=test_query,
                    top_k=1,
                    filter={"area": area},
                    include_metadata=True
                )
                count = len(results.matches) if results.matches else 0
                print(f"   - {area.title()}: {count} vectores encontrados")
            except Exception as e:
                print(f"   - {area.title()}: Error verificando - {e}")
        
        # Query de prueba general
        print(f"\n🧪 Query de prueba...")
        test_query = [0.0] * 1536
        results = index.query(
            vector=test_query,
            top_k=3,
            include_metadata=True
        )
        
        if results.matches:
            print(f"   ✅ Query exitosa - {len(results.matches)} resultados")
            for i, match in enumerate(results.matches[:2]):
                area = match.metadata.get("legal_area", "Unknown")
                source = match.metadata.get("source_file", "Unknown")
                print(f"   - Resultado {i+1}: {area} - {source}")
        else:
            print(f"   ❌ No se encontraron resultados")
            
    except Exception as e:
        print(f"❌ Error verificando índice: {e}")

def clear_index(index):
    """Limpiar índice (¡CUIDADO!)"""
    confirm = input("⚠️ ¿Estás seguro de que quieres limpiar el índice? (yes/no): ")
    if confirm.lower() == "yes":
        try:
            index.delete(delete_all=True)
            print("🗑️ Índice limpiado exitosamente")
        except Exception as e:
            print(f"❌ Error limpiando índice: {e}")
    else:
        print("❌ Operación cancelada")

def main():
    parser = argparse.ArgumentParser(description="Configurar RAG con documentos legales colombianos")
    parser.add_argument("--mode", choices=["import", "verify", "clear"], 
                       default="import", help="Modo de operación")
    parser.add_argument("--data-dir", default="./docs/legal", 
                       help="Directorio con documentos legales")
    
    args = parser.parse_args()
    
    # Verificar variables de entorno
    required_vars = ["PINECONE_API_KEY", "PINECONE_ENVIRONMENT", "PINECONE_INDEX_NAME", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Variables de entorno faltantes: {missing_vars}")
        print(f"💡 Configura las variables en tu archivo .env")
        return
    
    # Verificar que el directorio de datos existe
    if args.mode == "import" and not Path(args.data_dir).exists():
        print(f"❌ Directorio de datos no encontrado: {args.data_dir}")
        print(f"💡 Asegúrate de que el directorio con documentos legales existe")
        return
    
    # Configurar Pinecone
    try:
        index = setup_pinecone()
        print("✅ Conectado a Pinecone exitosamente")
    except Exception as e:
        print(f"❌ Error conectando a Pinecone: {e}")
        print(f"💡 Verifica tus credenciales de Pinecone")
        return
    
    if args.mode == "import":
        print(f"📁 Cargando documentos desde: {args.data_dir}")
        documents = load_legal_documents(args.data_dir)
        
        if not documents:
            print("❌ No se encontraron documentos para importar")
            return
            
        print(f"✅ Cargados {len(documents)} documentos")
        
        print("✂️ Procesando documentos en chunks...")
        processed_docs = process_documents(documents)
        print(f"✅ Procesados {len(processed_docs)} chunks")
        
        print("🚀 Importando a Pinecone...")
        import_to_pinecone(processed_docs, index)
        
    elif args.mode == "verify":
        verify_index(index)
        
    elif args.mode == "clear":
        clear_index(index)

if __name__ == "__main__":
    main()
