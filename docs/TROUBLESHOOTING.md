# 🆘 Guía de Troubleshooting - Sistema Legal Multiagente

## 🚨 Problemas Comunes y Soluciones

### 🔧 **Problemas de Deployment**

#### ❌ **"Build failed" en Render**

**Síntomas:**
- Build falla durante `pip install -e .`
- Error de dependencias no encontradas

**Soluciones:**
```bash
# 1. Verificar pyproject.toml
cat backend/pyproject.toml

# 2. Verificar que todas las dependencias estén listadas
# 3. Probar build localmente
cd backend
pip install -e .

# 4. Si falla, actualizar dependencias
pip install --upgrade pip setuptools wheel
```

**Causas comunes:**
- Dependencias conflictivas
- Versiones de Python incompatibles
- Archivos corruptos en cache

---

#### ❌ **"Cold start lento" en Render**

**Síntomas:**
- Primera request toma 30+ segundos
- Timeout en requests

**Soluciones:**
```bash
# 1. Upgrade a plan Starter ($7/mes)
# 2. Implementar keep-alive
# 3. Optimizar imports
```

**Configuración keep-alive:**
```python
# En main.py
@app.middleware("http")
async def keep_alive(request: Request, call_next):
    response = await call_next(request)
    response.headers["Keep-Alive"] = "timeout=5, max=1000"
    return response
```

---

#### ❌ **"CORS error" en frontend**

**Síntomas:**
- Error en browser: "CORS policy"
- Frontend no puede conectar con backend

**Soluciones:**
```bash
# 1. Verificar ALLOWED_ORIGINS en backend
# En Render: Environment Variables
ALLOWED_ORIGINS=https://tu-frontend.vercel.app,http://localhost:3000

# 2. Verificar NEXT_PUBLIC_API_URL en frontend
# En Vercel: Environment Variables
NEXT_PUBLIC_API_URL=https://tu-backend.onrender.com
```

**Verificación:**
```bash
# Test CORS
curl -H "Origin: https://tu-frontend.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: X-Requested-With" \
  -X OPTIONS \
  https://tu-backend.onrender.com/rag/query
```

---

### 🔑 **Problemas de API Keys**

#### ❌ **"Invalid API Key" - OpenAI**

**Síntomas:**
- Error 401 en requests a OpenAI
- "Invalid API key" en logs

**Soluciones:**
```bash
# 1. Verificar formato de key
# Debe empezar con: sk-proj- o sk-
echo $OPENAI_API_KEY

# 2. Verificar en OpenAI Dashboard
# https://platform.openai.com/api-keys

# 3. Regenerar key si es necesario
# 4. Verificar billing y créditos
```

**Test de API:**
```bash
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

---

#### ❌ **"Index not found" - Pinecone**

**Síntomas:**
- Error al conectar con Pinecone
- "Index does not exist"

**Soluciones:**
```bash
# 1. Verificar nombre del índice
echo $PINECONE_INDEX_NAME  # Debe ser: legal-colombia-docs

# 2. Verificar en Pinecone Dashboard
# https://app.pinecone.io/

# 3. Crear índice si no existe:
# - Name: legal-colombia-docs
# - Dimensions: 1536
# - Metric: cosine
# - Environment: us-east-1-aws
```

**Test de Pinecone:**
```bash
curl -X GET "https://api.pinecone.io/v1/indexes" \
  -H "Api-Key: $PINECONE_API_KEY"
```

---

#### ❌ **"Voice service unavailable" - ElevenLabs**

**Síntomas:**
- Error en síntesis de voz
- "API key invalid"

**Soluciones:**
```bash
# 1. Verificar key de ElevenLabs
echo $ELEVENLABS_API_KEY

# 2. Verificar en ElevenLabs Dashboard
# https://elevenlabs.io/app/settings/api-keys

# 3. Verificar límites de uso
# Plan gratuito: 10,000 caracteres/mes
```

**Test de ElevenLabs:**
```bash
curl -X GET "https://api.elevenlabs.io/v1/voices" \
  -H "xi-api-key: $ELEVENLABS_API_KEY"
```

---

### 🗄️ **Problemas de Base de Datos**

#### ❌ **"Vector search failed"**

**Síntomas:**
- RAG no encuentra documentos relevantes
- Respuestas genéricas sin contexto

**Soluciones:**
```bash
# 1. Verificar que el índice tenga datos
# En Pinecone Dashboard, verificar vector count

# 2. Re-indexar documentos
curl -X POST "https://tu-backend.onrender.com/documents/reindex" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 3. Verificar embeddings
curl -X POST "https://tu-backend.onrender.com/rag/status"
```

---

### 🎤 **Problemas de Voz**

#### ❌ **"Audio processing failed"**

**Síntomas:**
- Error al procesar audio
- Speech-to-text no funciona

**Soluciones:**
```bash
# 1. Verificar formato de audio
# Formatos soportados: WAV, MP3, M4A
# Tamaño máximo: 25MB

# 2. Verificar OpenAI Whisper
curl -X POST "https://tu-backend.onrender.com/voice/speech-to-text" \
  -F "audio_file=@test.wav"

# 3. Verificar logs
# En Render: View Logs
```

---

### 📱 **Problemas de Frontend**

#### ❌ **"Hydration mismatch"**

**Síntomas:**
- Error en browser console
- Componentes no se renderizan

**Soluciones:**
```bash
# 1. Verificar next.config.mjs
# Asegurar que suppressHydrationWarning esté configurado

# 2. Limpiar cache
rm -rf frontend/.next
npm run build

# 3. Verificar componentes
# Asegurar que no haya diferencias entre server/client
```

---

#### ❌ **"API calls failing"**

**Síntomas:**
- Requests fallan en frontend
- Network errors

**Soluciones:**
```bash
# 1. Verificar API client
# En lib/api-client.ts

# 2. Verificar variables de entorno
echo $NEXT_PUBLIC_API_URL

# 3. Test directo de API
curl https://tu-backend.onrender.com/health
```

---

### 🔍 **Debugging Avanzado**

#### **Logs en Render**
```bash
# Ver logs en tiempo real
render logs -s legal-agent-api -f

# Ver logs específicos
render logs -s legal-agent-api --tail 100

# Filtrar por error
render logs -s legal-agent-api | grep ERROR
```

#### **Logs en Vercel**
```bash
# Ver logs en Vercel Dashboard
# https://vercel.com/dashboard

# O usar CLI
vercel logs https://tu-proyecto.vercel.app
```

#### **Health Checks**
```bash
# Backend health
curl https://tu-backend.onrender.com/health

# RAG status
curl https://tu-backend.onrender.com/rag/status

# Voice status
curl https://tu-backend.onrender.com/voice/status

# Documents status
curl https://tu-backend.onrender.com/documents/health
```

---

### 🧪 **Testing de Componentes**

#### **Test de RAG**
```bash
curl -X POST "https://tu-backend.onrender.com/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Cómo constituyo una SAS en Colombia?",
    "use_uploaded_docs": false
  }'
```

#### **Test de Voz**
```bash
# Speech-to-text
curl -X POST "https://tu-backend.onrender.com/voice/speech-to-text" \
  -F "audio_file=@consulta.wav"

# Text-to-speech
curl -X POST "https://tu-backend.onrender.com/voice/text-to-speech" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Respuesta legal de prueba",
    "voice_style": "legal"
  }'
```

#### **Test de Documentos**
```bash
# Upload
curl -X POST "https://tu-backend.onrender.com/documents/upload" \
  -F "file=@documento.pdf" \
  -F "user_id=test123"

# List
curl "https://tu-backend.onrender.com/documents/user/test123"
```

---

### 📊 **Monitoreo de Performance**

#### **Métricas Importantes**
- **Response time:** < 5 segundos para RAG
- **Memory usage:** < 512MB en Render
- **Error rate:** < 1%
- **Uptime:** > 99%

#### **Alertas Recomendadas**
```bash
# Configurar en Render
# - CPU > 80%
# - Memory > 90%
# - Response time > 10s
# - Error rate > 5%
```

---

### 📞 **Contacto de Soporte**

- 📧 **Email:** esteban.ortiz.dev@gmail.com

---

**💡 Tip:** Siempre incluye logs, pasos para reproducir y versión del sistema al reportar problemas.
