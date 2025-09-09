# 🚀 Guía de Deployment - Sistema Legal Multiagente

## 📋 Resumen de Pasos

Esta guía te llevará a través del proceso completo de deployment manual del Sistema Legal Multiagente.

### ⏱️ Tiempo Estimado: 45-60 minutos
### 💰 Costo Estimado: $15-40/mes (dependiendo del plan)

---

## 🎯 **PASO 1: Crear Nuevo Repositorio en GitHub**

### 1.1 Crear Repositorio
1. Ve a [GitHub.com](https://github.com) y haz clic en **"New repository"**
2. **Nombre:** `sistema-legal-ia` (o el que prefieras)
3. **Descripción:** "Sistema Legal Multiagente - IA especializada en derecho colombiano"
4. **Visibilidad:** Público o Privado (tu elección)
5. **NO marques:** "Add a README file", "Add .gitignore", "Choose a license"
6. Haz clic en **"Create repository"**

### 1.2 Subir Código
```bash
# En tu directorio del proyecto
cd C:\Users\Esteb\OneDrive\Escritorio\agentLegal

# Inicializar git (si no está inicializado)
git init

# Agregar todos los archivos
git add .

# Commit inicial
git commit -m "Initial commit: Sistema Legal Multiagente - Deployment Ready"

# Conectar con el nuevo repositorio (reemplaza con tu URL)
git remote add origin https://github.com/TU-USUARIO/sistema-legal-ia.git

# Subir al repositorio
git branch -M main
git push -u origin main
```

---

## 🔑 **PASO 2: Configurar APIs Externas**

### 2.1 OpenAI API (REQUERIDO)
1. **Crear cuenta:** [platform.openai.com](https://platform.openai.com)
2. **Configurar billing:** Agregar tarjeta de crédito (mínimo $5)
3. **Crear API Key:**
   - Ve a API Keys → Create new secret key
   - Copia la key (empieza con `sk-`)
   - **Guárdala segura** - no la compartas
4. **Configurar límites de uso:**
   - Ve a Usage limits
   - Establece límite de $50/mes (recomendado)

### 2.2 Pinecone API (REQUERIDO)
1. **Crear cuenta:** [pinecone.io](https://pinecone.io)
2. **Crear índice:**
   - Name: `legal-colombia-docs`
   - Dimensions: `1536`
   - Metric: `cosine`
   - Environment: `us-east-1-aws`
3. **Obtener API Key:**
   - Ve a API Keys → Copy
   - **Guárdala segura**

### 2.3 APIs Opcionales
- **ElevenLabs:** [elevenlabs.io](https://elevenlabs.io) (para síntesis de voz)
- **AWS S3:** [aws.amazon.com](https://aws.amazon.com) (para almacenamiento de documentos)

---

## 📚 **PASO 3: Importar Documentos Legales**

### 3.1 Configurar Entorno Local
```bash
# Clonar el repositorio (si no lo tienes)
git clone https://github.com/TU-USUARIO/sistema-legal-ia.git
cd sistema-legal-ia/backend

# Configurar variables de entorno
cp env_example.txt .env

# Editar .env con tus API keys:
# OPENAI_API_KEY=sk-tu-key-aqui
# PINECONE_API_KEY=tu-key-aqui
# PINECONE_INDEX_NAME=legal-colombia-docs
# PINECONE_ENVIRONMENT=us-east-1-aws
```

### 3.2 Instalar Dependencias
```bash
# Instalar dependencias Python
pip install -e .

# Verificar instalación
python -c "import langchain; print('✅ Dependencias instaladas')"
```

### 3.3 Importar Documentos
```bash
# Importar documentos al índice Pinecone
python scripts/setup_rag.py --mode import --data-dir docs/legal

# Verificar importación
python scripts/setup_rag.py --mode verify

# Verificar compatibilidad completa
python scripts/verify_rag_compatibility.py
```

**Resultado esperado:**
```
✅ Vectorstore conectado exitosamente!
✅ Procesados 150 chunks
✅ Importación completada
✅ Todas las pruebas pasaron exitosamente!
```

---

## 🖥️ **PASO 4: Deploy Backend en Render**

### 4.1 Crear Cuenta en Render
1. Ve a [render.com](https://render.com)
2. Regístrate con tu cuenta de GitHub
3. Autoriza el acceso a tu repositorio

### 4.2 Crear Web Service
1. **Dashboard** → **New** → **Web Service**
2. **Connect Repository:** Selecciona tu repositorio `sistema-legal-ia`
3. **Configuración:**
   ```
   Name: legal-agent-api
   Environment: Python 3
   Region: Oregon (más cercano a Colombia)
   Branch: main
   Root Directory: backend
   Build Command: pip install -e .
   Start Command: uvicorn src.app.main:app --host 0.0.0.0 --port $PORT
   ```
   
   **Nota:** Usamos `pyproject.toml` para gestionar dependencias (estándar moderno de Python)

### 4.3 Configurar Variables de Entorno
En la sección **Environment Variables**, agrega:

**Variables Requeridas:**
```
OPENAI_API_KEY = sk-tu-openai-key-aqui
PINECONE_API_KEY = tu-pinecone-key-aqui
PINECONE_INDEX_NAME = legal-colombia-docs
PINECONE_ENVIRONMENT = us-east-1-aws
```

**Variables Opcionales:**
```
ELEVENLABS_API_KEY = tu-elevenlabs-key-aqui
AWS_ACCESS_KEY_ID = tu-aws-key-aqui
AWS_SECRET_ACCESS_KEY = tu-aws-secret-aqui
AWS_S3_BUCKET_NAME = tu-bucket-name
```

### 4.4 Deploy
1. Haz clic en **"Create Web Service"**
2. Espera el deployment (5-10 minutos)
3. Anota la URL: `https://legal-agent-api.onrender.com`

### 4.5 Verificar Backend
```bash
# Health check
curl https://legal-agent-api.onrender.com/health

# RAG status
curl https://legal-agent-api.onrender.com/rag/status

# API docs
# Visitar: https://legal-agent-api.onrender.com/docs
```

---

## 🌐 **PASO 5: Deploy Frontend en Vercel**

### 5.1 Crear Cuenta en Vercel
1. Ve a [vercel.com](https://vercel.com)
2. Regístrate con tu cuenta de GitHub
3. Autoriza el acceso a tu repositorio

### 5.2 Importar Proyecto
1. **Dashboard** → **Add New** → **Project**
2. **Import Git Repository:** Selecciona tu repositorio `sistema-legal-ia`
3. **Configuración:**
   ```
   Framework Preset: Next.js
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

### 5.3 Configurar Variables de Entorno
En la sección **Environment Variables**, agrega:

**Variable Requerida:**
```
NEXT_PUBLIC_API_BASE_URL = https://legal-agent-api.onrender.com
```

**Variable Opcional:**
```
NEXT_TELEMETRY_DISABLED = 1
```

### 5.4 Deploy
1. Haz clic en **"Deploy"**
2. Espera el deployment (2-3 minutos)
3. Anota la URL: `https://sistema-legal-ia.vercel.app`

### 5.5 Verificar Frontend
- ✅ Página carga correctamente
- ✅ Formulario de consulta funciona
- ✅ Respuestas del RAG aparecen
- ✅ Interfaz responsive

---

## ⚙️ **PASO 6: Configurar Variables de Entorno**

### 6.1 Backend (Render)
Verifica que todas las variables estén configuradas:
```
✅ OPENAI_API_KEY
✅ PINECONE_API_KEY
✅ PINECONE_INDEX_NAME
✅ PINECONE_ENVIRONMENT
✅ ELEVENLABS_API_KEY (opcional)
✅ AWS_ACCESS_KEY_ID (opcional)
✅ AWS_SECRET_ACCESS_KEY (opcional)
```

### 6.2 Frontend (Vercel)
Verifica que las variables estén configuradas:
```
✅ NEXT_PUBLIC_API_BASE_URL = https://legal-agent-api.onrender.com
✅ NEXT_TELEMETRY_DISABLED = 1 (opcional)
```

---

## 🧪 **PASO 7: Verificar Funcionamiento Completo**

### 7.1 Pruebas Básicas
```bash
# 1. Health check backend
curl https://legal-agent-api.onrender.com/health

# 2. Test RAG
curl -X POST "https://legal-agent-api.onrender.com/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Cómo constituyo una SAS en Colombia?", "use_uploaded_docs": false}'

# 3. Test frontend
# Visitar: https://sistema-legal-ia.vercel.app
```

### 7.2 Pruebas de Consultas Legales
**Consultas de prueba:**
- "¿Cómo constituyo una SAS en Colombia?"
- "¿Cómo calcular las prestaciones sociales?"
- "¿Cómo presentar la declaración de renta?"
- "¿Qué documentos necesito para un contrato de trabajo?"

### 7.3 Verificar Funcionalidades
- ✅ **Consultas RAG:** Respuestas basadas en documentos legales
- ✅ **Categorización:** Detecta área legal correcta
- ✅ **Fuentes:** Muestra documentos de referencia
- ✅ **Sugerencias:** Genera preguntas relacionadas
- ✅ **Voz:** (Si configurado) Speech-to-text y text-to-speech

---

## 🎉 **¡Deployment Completado!**

### URLs Finales:
- **🌐 Frontend:** `https://sistema-legal-ia.vercel.app`
- **🖥️ Backend:** `https://legal-agent-api.onrender.com`
- **📚 API Docs:** `https://legal-agent-api.onrender.com/docs`

### ✅ Checklist Final:
- [ ] Repositorio en GitHub creado y subido
- [ ] APIs configuradas (OpenAI, Pinecone)
- [ ] Documentos legales importados
- [ ] Backend desplegado en Render
- [ ] Frontend desplegado en Vercel
- [ ] Variables de entorno configuradas
- [ ] Consultas legales funcionando
- [ ] Sistema completo operacional

---

## 🆘 **Troubleshooting**

### Problemas Comunes:

#### ❌ "Build failed" en Render
- Verificar variables de entorno
- Verificar dependencias en pyproject.toml
- Verificar comando de build

#### ❌ "RAG no funciona"
- Verificar documentos importados en Pinecone
- Verificar API keys correctas
- Verificar índice Pinecone existe

#### ❌ "CORS error" en frontend
- Verificar NEXT_PUBLIC_API_BASE_URL configurado
- Verificar ALLOWED_ORIGINS en backend
- Verificar URLs correctas

#### ❌ "Cold start lento"
- Upgrade a plan Starter en Render ($7/mes)
- Implementar keep-alive
- Optimizar imports

---

## 📊 **Costos Estimados**

### Plan Básico (Funcional)
- **OpenAI:** $10-20/mes
- **Pinecone:** Gratis (100K vectores)
- **Render:** Gratis (con limitaciones)
- **Vercel:** Gratis
- **Total:** ~$15/mes

### Plan Optimizado (Producción)
- **OpenAI:** $10-20/mes
- **Pinecone:** Gratis
- **Render Starter:** $7/mes
- **Vercel Pro:** $20/mes
- **Total:** ~$40/mes

---

**🚀 ¡Tu sistema legal con IA estará funcionando en menos de 60 minutos!**
