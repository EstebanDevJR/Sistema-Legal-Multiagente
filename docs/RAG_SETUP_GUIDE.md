# 🗄️ Guía de Configuración RAG - Desarrollo Local

## 🎯 Configuración RAG para Desarrollo

Esta guía te ayudará a configurar el sistema RAG (Retrieval Augmented Generation) para desarrollo local.

---

## 📁 Documentos Legales Incluidos

El sistema incluye documentos legales colombianos organizados por área:

```
backend/docs/legal/
├── civil/
│   ├── codigo_civil.txt
│   └── ley_1581_2012.pdf
├── comercial/
│   ├── codigo_comercio.txt
│   └── ley_1480_2011.pdf
├── laboral/
│   └── codigo_trabajo.pdf
└── tributario/
    └── estatuto_tributario.txt
```

### 📋 Contenido de cada área:

- **🏛️ Civil:** Código Civil, Ley de Protección de Datos
- **🏪 Comercial:** Código de Comercio, Ley del Consumidor
- **👥 Laboral:** Código Sustantivo del Trabajo
- **💰 Tributario:** Estatuto Tributario Nacional

---

## 🚀 Opción Alternativa: Usar Índice Compartido (No Recomendado)

### Para usuarios que quieren usar tu sistema:

1. **Configurar variables de entorno:**
   ```bash
   # En Render/Vercel, usar estas variables:
   PINECONE_API_KEY=tu-api-key-compartida
   PINECONE_INDEX_NAME=legal-colombia-docs
   PINECONE_ENVIRONMENT=us-east-1-aws
   ```

2. **Crear API Key compartida:**
   - Ve a tu cuenta Pinecone
   - API Keys → Create new key
   - Nombre: `legal-agent-shared`
   - **Permisos:** Solo lectura (read-only)

3. **Compartir con usuarios:**
   - Envía la API key a usuarios autorizados
   - O publícala en la documentación (si es read-only)

### ✅ Ventajas:
- Funciona inmediatamente
- No necesitan configurar nada
- Usan tu base de datos actualizada

### ❌ Desventajas:
- Dependen de tu cuenta
- Límites compartidos
- Menos control para ellos

---

## 🏗️ Configuración Paso a Paso (Recomendado)

### 1. **Crear cuenta Pinecone:**
   - Ve a [pinecone.io](https://pinecone.io)
   - Crea cuenta gratuita
   - **Plan gratuito:** 1 índice, 100K vectores

### 2. **Crear índice:**
   - Ve a Indexes → Create Index
   - **Name:** `legal-colombia-docs`
   - **Dimensions:** `1536` (para OpenAI embeddings)
   - **Metric:** `cosine`
   - **Environment:** `us-east-1-aws`

### 3. **Configurar variables de entorno:**
   ```bash
   PINECONE_API_KEY=tu-api-key-aqui
   PINECONE_INDEX_NAME=legal-colombia-docs
   PINECONE_ENVIRONMENT=us-east-1-aws
   OPENAI_API_KEY=sk-tu-openai-key-aqui
   ```

### 4. **Importar documentos legales:**
   ```bash
   # Navegar al directorio backend
   cd backend
   
   # Ejecutar script de importación
   python scripts/setup_rag.py --mode import --data-dir docs/legal
   
   # Verificar importación
   python scripts/setup_rag.py --mode verify
   ```

### ✅ Ventajas:
- **Independencia total** - No dependes de cuentas externas
- **Control completo** - Puedes modificar y actualizar los datos
- **Escalabilidad** - Tu propio límite de vectores
- **Privacidad** - Tus datos permanecen en tu cuenta
- **Personalización** - Puedes agregar más documentos legales

### ⚠️ Consideraciones:
- Requiere configuración inicial (15-20 minutos)
- Necesitas tus propias API keys
- Debes ejecutar el script de importación

---

## 📁 Opción 3: Compartir Datos (Para Desarrolladores)

### Si quieres que otros desarrollen con tus datos:

1. **Crear repositorio de datos:**
   ```bash
   # Crear carpeta con datos
   mkdir legal-colombia-data
   cd legal-colombia-data
   
   # Estructura recomendada:
   legal-colombia-data/
   ├── documents/
   │   ├── civil/
   │   ├── commercial/
   │   ├── laboral/
   │   └── tributario/
   ├── embeddings/
   ├── scripts/
   │   ├── import_to_pinecone.py
   │   └── process_documents.py
   └── README.md
   ```

2. **Script de importación:**
   ```python
   # scripts/import_to_pinecone.py
   import pinecone
   from langchain.text_splitter import RecursiveCharacterTextSplitter
   from langchain.embeddings import OpenAIEmbeddings
   import os
   
   def import_documents():
       # Configurar Pinecone
       pinecone.init(
           api_key=os.getenv("PINECONE_API_KEY"),
           environment=os.getenv("PINECONE_ENVIRONMENT")
       )
       
       # Conectar al índice
       index = pinecone.Index("legal-colombia-docs")
       
       # Procesar documentos
       # ... código de importación ...
   ```

3. **Documentación:**
   ```markdown
   # legal-colombia-data/README.md
   ## Datos Legales Colombia
   
   Este repositorio contiene documentos legales colombianos procesados para RAG.
   
   ### Uso:
   1. Clonar repositorio
   2. Configurar API keys
   3. Ejecutar script de importación
   ```

---

## 🛠️ Script de Importación Incluido

**✅ Compatibilidad Garantizada:** El script está optimizado para funcionar perfectamente con tu sistema RAG existente.

```python
#!/usr/bin/env python3
"""
Script para configurar RAG con Pinecone
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
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.schema import Document

def setup_pinecone():
    """Configurar conexión a Pinecone"""
    pinecone.init(
        api_key=os.getenv("PINECONE_API_KEY"),
        environment=os.getenv("PINECONE_ENVIRONMENT")
    )
    return pinecone.Index(os.getenv("PINECONE_INDEX_NAME"))

def load_documents(data_dir: str) -> List[Document]:
    """Cargar documentos desde directorio"""
    loader = DirectoryLoader(
        data_dir,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    return loader.load()

def process_documents(documents: List[Document]) -> List[Document]:
    """Procesar y dividir documentos"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    return text_splitter.split_documents(documents)

def import_to_pinecone(documents: List[Document], index):
    """Importar documentos a Pinecone"""
    embeddings = OpenAIEmbeddings()
    
    # Procesar en lotes
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        
        # Generar embeddings
        texts = [doc.page_content for doc in batch]
        vectors = embeddings.embed_documents(texts)
        
        # Preparar para Pinecone
        vectors_to_upsert = []
        for j, (doc, vector) in enumerate(zip(batch, vectors)):
            vectors_to_upsert.append({
                "id": f"doc_{i + j}",
                "values": vector,
                "metadata": {
                    "text": doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                    "area": extract_legal_area(doc.metadata.get("source", ""))
                }
            })
        
        # Subir a Pinecone
        index.upsert(vectors=vectors_to_upsert)
        print(f"✅ Procesado lote {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")

def extract_legal_area(source: str) -> str:
    """Extraer área legal del path del archivo"""
    if "civil" in source.lower():
        return "civil"
    elif "commercial" in source.lower() or "comercial" in source.lower():
        return "commercial"
    elif "laboral" in source.lower():
        return "laboral"
    elif "tributario" in source.lower():
        return "tributario"
    return "general"

def verify_index(index):
    """Verificar contenido del índice"""
    stats = index.describe_index_stats()
    print(f"📊 Estadísticas del índice:")
    print(f"   - Total vectores: {stats.total_vector_count}")
    print(f"   - Dimensiones: {stats.dimension}")
    print(f"   - Namespaces: {list(stats.namespaces.keys())}")

def clear_index(index):
    """Limpiar índice (¡CUIDADO!)"""
    confirm = input("⚠️ ¿Estás seguro de que quieres limpiar el índice? (yes/no): ")
    if confirm.lower() == "yes":
        index.delete(delete_all=True)
        print("🗑️ Índice limpiado")
    else:
        print("❌ Operación cancelada")

def main():
    parser = argparse.ArgumentParser(description="Configurar RAG con Pinecone")
    parser.add_argument("--mode", choices=["import", "verify", "clear"], 
                       default="import", help="Modo de operación")
    parser.add_argument("--data-dir", default="./data", 
                       help="Directorio con documentos")
    
    args = parser.parse_args()
    
    # Verificar variables de entorno
    required_vars = ["PINECONE_API_KEY", "PINECONE_ENVIRONMENT", "PINECONE_INDEX_NAME", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Variables de entorno faltantes: {missing_vars}")
        return
    
    # Configurar Pinecone
    try:
        index = setup_pinecone()
        print("✅ Conectado a Pinecone")
    except Exception as e:
        print(f"❌ Error conectando a Pinecone: {e}")
        return
    
    if args.mode == "import":
        # Cargar y procesar documentos
        print("📁 Cargando documentos...")
        documents = load_documents(args.data_dir)
        print(f"✅ Cargados {len(documents)} documentos")
        
        print("✂️ Procesando documentos...")
        processed_docs = process_documents(documents)
        print(f"✅ Procesados {len(processed_docs)} chunks")
        
        print("🚀 Importando a Pinecone...")
        import_to_pinecone(processed_docs, index)
        print("✅ Importación completada")
        
    elif args.mode == "verify":
        verify_index(index)
        
    elif args.mode == "clear":
        clear_index(index)

if __name__ == "__main__":
    main()
```

---

## 📋 Instrucciones de Uso

### Para usuarios que quieren usar tu sistema:

1. **Configurar variables de entorno:**
   ```bash
   PINECONE_API_KEY=tu-api-key
   PINECONE_INDEX_NAME=legal-colombia-docs
   PINECONE_ENVIRONMENT=us-east-1-aws
   ```



### Para usuarios que quieren configurar su propio RAG:

1. **Clonar el proyecto:**
   ```bash
   git clone https://github.com/tu-usuario/agentLegal.git
   cd agentLegal
   ```

2. **Configurar APIs:**
   ```bash
   cd backend
   cp env_example.txt .env
   # Editar .env con tus API keys
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -e .
   ```

4. **Importar documentos legales:**
   ```bash
   python scripts/setup_rag.py --mode import --data-dir docs/legal
   ```

5. **Verificar importación:**
   ```bash
   python scripts/setup_rag.py --mode verify
   ```

---

## 🔐 Consideraciones de Seguridad

### API Keys Compartidas:
- ✅ **Read-only keys** para usuarios finales
- ❌ **Never share write keys**
- 🔄 **Rotar keys periódicamente**

### Datos Sensibles:
- ✅ **Documentos públicos** (leyes, códigos)
- ❌ **Documentos privados** o confidenciales
- 📝 **Agregar disclaimer** sobre uso

---

## 💡 Recomendaciones

### Para tu caso específico:

1. **Opción 1 (Recomendada):** Compartir tu índice
   - Crear API key read-only
   - Documentar en README
   - Monitorear uso

2. **Opción 2 (Para desarrolladores):** Compartir datos
   - Crear repositorio con documentos
   - Script de importación
   - Documentación clara

3. **Opción 3 (Híbrida):** Ambas
   - Tu índice para usuarios finales
   - Datos + script para desarrolladores

---

## 📞 Soporte

- 📧 **Email:** esteban.ortiz.dev@gmail.com
---

