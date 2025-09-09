# 🔑 Guía de Variables de Entorno - Sistema Legal Multiagente

## 📋 Resumen

Esta guía explica todas las variables de entorno necesarias para el deployment del Sistema Legal Multiagente.

---

## 🖥️ **Backend (Render)**

### Variables Requeridas (CRÍTICAS)

| Variable | Descripción | Ejemplo | Dónde Obtener |
|----------|-------------|---------|---------------|
| `OPENAI_API_KEY` | API Key de OpenAI para GPT-4 | `sk-proj-...` | [platform.openai.com](https://platform.openai.com) |
| `PINECONE_API_KEY` | API Key de Pinecone | `12345678-...` | [pinecone.io](https://pinecone.io) |
| `PINECONE_INDEX_NAME` | Nombre del índice Pinecone | `legal-colombia-docs` | Tu índice en Pinecone |
| `PINECONE_ENVIRONMENT` | Ambiente de Pinecone | `us-east-1-aws` | Tu configuración Pinecone |

### Variables Opcionales

| Variable | Descripción | Ejemplo | Dónde Obtener |
|----------|-------------|---------|---------------|
| `ELEVENLABS_API_KEY` | API Key para síntesis de voz | `sk_...` | [elevenlabs.io](https://elevenlabs.io) |
| `AWS_ACCESS_KEY_ID` | AWS Access Key para S3 | `AKIA...` | [aws.amazon.com](https://aws.amazon.com) |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Key para S3 | `wJalr...` | [aws.amazon.com](https://aws.amazon.com) |
| `AWS_REGION` | Región de AWS | `us-east-1` | Tu configuración AWS |
| `AWS_S3_BUCKET_NAME` | Nombre del bucket S3 | `legal-agent-docs` | Tu bucket S3 |
| `LANGSMITH_API_KEY` | API Key para monitoreo | `ls__...` | [smith.langchain.com](https://smith.langchain.com) |
| `LANGSMITH_PROJECT` | Proyecto de LangSmith | `legal-agent-colombia` | Tu proyecto LangSmith |

### Variables de Configuración

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `ENVIRONMENT` | Ambiente de ejecución | `production` |
| `PORT` | Puerto del servidor | `8000` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |
| `ALLOWED_ORIGINS` | Orígenes CORS permitidos | `http://localhost:3000,https://tu-frontend.vercel.app` |
| `TRUSTED_HOSTS` | Hosts confiables | `localhost,127.0.0.1,tu-backend.onrender.com` |
| `REQUESTS_PER_MINUTE` | Límite de requests | `300` |

---

## 🌐 **Frontend (Vercel)**

### Variables Requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | URL base del backend | `https://legal-agent-api.onrender.com` |

### Variables Opcionales

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `NEXT_TELEMETRY_DISABLED` | Deshabilitar telemetría de Next.js | `1` |

---

## 🔧 **Configuración Paso a Paso**

### 1. Backend en Render

1. **Ve a tu servicio en Render**
2. **Settings** → **Environment**
3. **Agrega cada variable:**

```bash
# Variables Requeridas
OPENAI_API_KEY = sk-proj-tu-key-aqui
PINECONE_API_KEY = tu-pinecone-key-aqui
PINECONE_INDEX_NAME = legal-colombia-docs
PINECONE_ENVIRONMENT = us-east-1-aws

# Variables Opcionales
ELEVENLABS_API_KEY = sk_tu-elevenlabs-key-aqui
AWS_ACCESS_KEY_ID = AKIA_tu-aws-key-aqui
AWS_SECRET_ACCESS_KEY = tu-aws-secret-aqui
AWS_REGION = us-east-1
AWS_S3_BUCKET_NAME = tu-bucket-name
LANGSMITH_API_KEY = ls__tu-langsmith-key-aqui
LANGSMITH_PROJECT = legal-agent-colombia

# Variables de Configuración
ENVIRONMENT = production
PORT = 8000
LOG_LEVEL = INFO
ALLOWED_ORIGINS = https://tu-frontend.vercel.app
TRUSTED_HOSTS = tu-backend.onrender.com
REQUESTS_PER_MINUTE = 300
```

### 2. Frontend en Vercel

1. **Ve a tu proyecto en Vercel**
2. **Settings** → **Environment Variables**
3. **Agrega cada variable:**

```bash
# Variable Requerida
NEXT_PUBLIC_API_BASE_URL = https://legal-agent-api.onrender.com

# Variables Opcionales
NEXT_TELEMETRY_DISABLED = 1
```

---

## 🔐 **Seguridad**

### Variables Sensibles
- **NUNCA** subas estas variables al repositorio
- **SIEMPRE** usa las variables de entorno del servicio
- **ROTA** las API keys regularmente

### Variables Seguras
- Variables que empiezan con `NEXT_PUBLIC_` son públicas
- Variables sin `NEXT_PUBLIC_` son privadas del servidor

---

## 🧪 **Verificación**

### Backend
```bash
# Verificar variables configuradas
curl https://tu-backend.onrender.com/health

# Verificar RAG funcionando
curl https://tu-backend.onrender.com/rag/status
```

### Frontend
```bash
# Verificar que la API URL esté configurada
# Revisar Network tab en DevTools
# Debe mostrar requests a tu backend
```

---

## 🆘 **Troubleshooting**

### Problemas Comunes

#### ❌ "API Key not found"
- Verificar que la variable esté configurada
- Verificar que no tenga espacios extra
- Verificar que esté en el ambiente correcto

#### ❌ "CORS error"
- Verificar `ALLOWED_ORIGINS` en backend
- Verificar `NEXT_PUBLIC_API_BASE_URL` en frontend
- Verificar URLs exactas (sin trailing slash)

#### ❌ "Pinecone connection failed"
- Verificar `PINECONE_API_KEY`
- Verificar `PINECONE_INDEX_NAME`
- Verificar `PINECONE_ENVIRONMENT`
- Verificar que el índice exista

#### ❌ "OpenAI API error"
- Verificar `OPENAI_API_KEY`
- Verificar que tenga créditos disponibles
- Verificar límites de uso

---

## 📊 **Costos por API**

### OpenAI
- **Modelo:** GPT-4
- **Costo:** ~$0.03 por 1K tokens
- **Estimado:** $10-20/mes

### Pinecone
- **Plan:** Starter (gratis)
- **Límite:** 100K vectores
- **Costo:** $0/mes

### ElevenLabs
- **Plan:** Starter
- **Límite:** 10K caracteres/mes
- **Costo:** $5/mes

### AWS S3
- **Uso:** Almacenamiento de documentos
- **Costo:** ~$1-5/mes

---

## ✅ **Checklist de Variables**

### Backend (Render)
- [ ] `OPENAI_API_KEY` configurada
- [ ] `PINECONE_API_KEY` configurada
- [ ] `PINECONE_INDEX_NAME` configurada
- [ ] `PINECONE_ENVIRONMENT` configurada
- [ ] `ELEVENLABS_API_KEY` configurada (opcional)
- [ ] `AWS_ACCESS_KEY_ID` configurada (opcional)
- [ ] `AWS_SECRET_ACCESS_KEY` configurada (opcional)
- [ ] `ALLOWED_ORIGINS` configurada
- [ ] `TRUSTED_HOSTS` configurada

### Frontend (Vercel)
- [ ] `NEXT_PUBLIC_API_BASE_URL` configurada
- [ ] `NEXT_TELEMETRY_DISABLED` configurada (opcional)

---

**🔑 ¡Todas las variables configuradas correctamente!**
