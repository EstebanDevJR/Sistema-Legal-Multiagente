#!/usr/bin/env python3
"""
Script de verificación de compatibilidad RAG
Verifica que el sistema RAG funcione correctamente con los datos importados
"""

import os
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.append(str(Path(__file__).parent.parent / "src"))

def test_rag_compatibility():
    """Probar compatibilidad del sistema RAG"""
    print("🔍 Verificando compatibilidad del sistema RAG...")
    
    try:
        # Importar componentes del sistema RAG
        from core.rag_service import rag_service
        from services.legal.rag.vector_manager import VectorManager
        from services.legal.rag.query_processor import QueryProcessor
        
        print("✅ Importaciones exitosas")
        
        # Probar VectorManager
        print("\n📊 Probando VectorManager...")
        vector_manager = VectorManager()
        stats = vector_manager.get_vectorstore_stats()
        
        if stats.get("status") == "connected":
            print("✅ VectorManager conectado correctamente")
            print(f"   - Índice: {stats.get('index_name')}")
            print(f"   - Modelo: {stats.get('embedding_model')}")
            print(f"   - Text key: {stats.get('text_key')}")
        else:
            print("❌ VectorManager no conectado")
            print(f"   - Error: {stats.get('error')}")
            return False
        
        # Probar QueryProcessor
        print("\n🧠 Probando QueryProcessor...")
        query_processor = QueryProcessor()
        
        test_queries = [
            "¿Cómo constituyo una SAS?",
            "¿Cómo calcular prestaciones sociales?",
            "¿Cómo presentar declaración de renta?"
        ]
        
        for query in test_queries:
            category = query_processor.determine_query_category(query)
            complexity = query_processor.get_query_complexity(query)
            processed = query_processor.preprocess_query(query, category)
            
            print(f"   - '{query[:30]}...' → {category} ({complexity})")
        
        print("✅ QueryProcessor funcionando correctamente")
        
        # Probar búsqueda vectorial
        print("\n🔍 Probando búsqueda vectorial...")
        test_question = "¿Cómo constituyo una empresa SAS en Colombia?"
        category = query_processor.determine_query_category(test_question)
        
        context, sources = vector_manager.search_vectorstore(test_question, category)
        
        if context and len(context) > 50:
            print("✅ Búsqueda vectorial exitosa")
            print(f"   - Contexto: {len(context)} caracteres")
            print(f"   - Fuentes: {len(sources)} encontradas")
            
            # Verificar estructura de fuentes
            if sources:
                source = sources[0]
                required_fields = ["title", "content", "relevance", "filename", "metadata"]
                missing_fields = [field for field in required_fields if field not in source]
                
                if not missing_fields:
                    print("✅ Estructura de fuentes correcta")
                else:
                    print(f"❌ Campos faltantes en fuentes: {missing_fields}")
        else:
            print("❌ Búsqueda vectorial falló")
            print(f"   - Contexto: {context[:100] if context else 'None'}")
            return False
        
        # Probar RAGService completo
        print("\n🤖 Probando RAGService completo...")
        import asyncio
        
        async def test_rag_service():
            result = await rag_service.process_legal_query(
                question=test_question,
                user_id="test_user",
                use_uploaded_docs=False
            )
            return result
        
        result = asyncio.run(test_rag_service())
        
        if result and result.get("answer"):
            print("✅ RAGService funcionando correctamente")
            print(f"   - Respuesta: {len(result['answer'])} caracteres")
            print(f"   - Confianza: {result.get('confidence', 0):.2f}")
            print(f"   - Categoría: {result.get('category', 'unknown')}")
            print(f"   - Fuentes: {len(result.get('sources', []))}")
        else:
            print("❌ RAGService falló")
            return False
        
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("✅ El sistema RAG es 100% compatible con los datos importados")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de que todas las dependencias estén instaladas")
        return False
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        return False

def check_environment():
    """Verificar variables de entorno"""
    print("🔧 Verificando variables de entorno...")
    
    required_vars = [
        "OPENAI_API_KEY",
        "PINECONE_API_KEY", 
        "PINECONE_INDEX_NAME",
        "PINECONE_ENVIRONMENT"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables faltantes: {missing_vars}")
        print("💡 Configura las variables en tu archivo .env")
        return False
    else:
        print("✅ Todas las variables de entorno configuradas")
        return True

def main():
    """Función principal"""
    print("🚀 Verificador de Compatibilidad RAG")
    print("=" * 50)
    
    # Verificar entorno
    if not check_environment():
        return
    
    # Probar compatibilidad
    if test_rag_compatibility():
        print("\n✅ RESULTADO: Sistema RAG completamente compatible")
        print("🎯 Los usuarios pueden usar el script setup_rag.py sin problemas")
    else:
        print("\n❌ RESULTADO: Problemas de compatibilidad detectados")
        print("🔧 Revisa los errores anteriores y corrige los problemas")

if __name__ == "__main__":
    main()
