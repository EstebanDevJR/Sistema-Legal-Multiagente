# 🚀 Guía de Despliegue Manual - Render + Vercel

## 📋 **Resumen del Despliegue**

Despliegue **SIN DOCKER** usando servicios gratuitos:
- ✅ **Backend (FastAPI)** → **Render** (gratis)
- ✅ **Frontend (Next.js)** → **Vercel** (gratis)
- ✅ **Pinecone** → Vector database externo
- ✅ **Caché en memoria** → Sin Redis

---

## 🎯 **Paso 1: Preparar el Backend para Render**

### **1.1 Crear `backend/render.yaml`:**
```yaml
services:
  - type: web
    name: agent-legal-backend
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: ELEVENLABS_API_KEY
        sync: false
      - key: PINECONE_API_KEY
        sync: false
      - key: PINECONE_INDEX_NAME
        value: legal-documents
      - key: SECRET_KEY
        generateValue: true
```

### **1.2 Crear `backend/requirements.txt`:**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
langchain==0.0.350
langchain-openai==0.0.2
langgraph==0.0.20
openai==1.3.7
elevenlabs==0.2.26
python-multipart==0.0.6
python-dotenv==1.0.0
pinecone-client>=5.0.0
langchain-pinecone>=0.2.1
chromadb==0.4.18
sentence-transformers==2.2.2
pydantic==2.5.0
httpx==0.25.2
aiofiles==23.2.1
```

### **1.3 Crear `backend/runtime.txt`:**
```txt
python-3.11.7
```

---

## 🎯 **Paso 2: Preparar el Frontend para Vercel**

### **2.1 Crear `frontend/vercel.json`:**
```json
{
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ]
}
```

### **2.2 Actualizar `frontend/next.config.mjs`:**
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`
      }
    ]
  }
}

export default nextConfig
```

---

## 🎯 **Paso 3: Desplegar Backend en Render**

### **3.1 Crear cuenta en Render:**
1. Ve a [render.com](https://render.com)
2. Conecta tu cuenta de GitHub
3. Selecciona tu repositorio `agentLegal`

### **3.2 Crear Web Service:**
1. **New** → **Web Service**
2. **Connect GitHub** → Selecciona `agentLegal`
3. **Configuración:**
   - **Name**: `agent-legal-backend`
   - **Environment**: `Python 3`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
   - **Auto-Deploy**: `Yes` (para deploy automático en push)

### **3.3 Variables de Entorno en Render:**
```
OPENAI_API_KEY=sk-tu-api-key-aqui
ELEVENLABS_API_KEY=tu-elevenlabs-key-aqui
PINECONE_API_KEY=tu-pinecone-api-key-aqui
PINECONE_INDEX_NAME=legal-documents
SECRET_KEY=tu-secret-key-muy-seguro
```

### **3.4 Deploy:**
1. Click **Create Web Service**
2. Render construirá y desplegará automáticamente
3. **URL del backend**: `https://agent-legal-backend.onrender.com`

---

## 🎯 **Paso 4: Desplegar Frontend en Vercel**

### **4.1 Crear cuenta en Vercel:**
1. Ve a [vercel.com](https://vercel.com)
2. Conecta tu cuenta de GitHub
3. Selecciona tu repositorio `agentLegal`

### **4.2 Configurar Proyecto:**
1. **Import Project** → Selecciona `agentLegal`
2. **Framework Preset**: `Next.js`
3. **Root Directory**: `frontend`
4. **Build Command**: `npm run build`
5. **Output Directory**: `.next`
6. **Install Command**: `npm install`

### **4.3 Variables de Entorno en Vercel:**
```
NEXT_PUBLIC_API_URL=https://agent-legal-backend.onrender.com
```

### **4.4 Deploy:**
1. Click **Deploy**
2. Vercel construirá y desplegará automáticamente
3. **URL del frontend**: `https://agent-legal-frontend.vercel.app`

---

## 🎯 **Paso 5: Configurar Dominio Personalizado (Opcional)**

### **5.1 En Vercel:**
1. Ve a **Settings** → **Domains**
2. Agrega tu dominio personalizado
3. Configura los DNS records

### **5.2 En Render:**
1. Ve a **Settings** → **Custom Domains**
2. Agrega tu subdominio (ej: `api.tudominio.com`)

---

## 🎯 **Paso 6: Verificar el Despliegue**

### **6.1 Backend:**
```bash
# Health check
curl https://agent-legal-backend.onrender.com/health

# API test
curl https://agent-legal-backend.onrender.com/docs
```

### **6.2 Frontend:**
```bash
# Abrir en navegador
https://agent-legal-frontend.vercel.app
```

---

## 💰 **Costo Total: $0/mes**

### **Render (Backend):**
- ✅ **Plan Free**: 750 horas/mes
- ✅ **Auto-sleep**: Después de 15 min inactivo
- ✅ **Wake-up**: 30 segundos

### **Vercel (Frontend):**
- ✅ **Plan Free**: Ilimitado
- ✅ **CDN global**: Rápido en todo el mundo
- ✅ **Auto-deploy**: Con cada push a GitHub

---

## 🔧 **Estructura Final:**
```
Render (Backend)
├── FastAPI + Pinecone
├── Caché en memoria
└── Auto-sleep/wake

Vercel (Frontend)
├── Next.js
├── CDN global
└── Auto-deploy
```

---

## 🚨 **Limitaciones del Plan Free:**

### **Render:**
- ⚠️ **Sleep**: Se duerme después de 15 min inactivo
- ⚠️ **Wake-up**: 30 segundos para despertar
- ⚠️ **CPU**: Limitado a 0.1 CPU

### **Vercel:**
- ⚠️ **Bandwidth**: 100GB/mes
- ⚠️ **Function executions**: 100GB-horas/mes

---

## 🔄 **Actualizaciones Automáticas:**

### **Render:**
- Auto-deploy en push a `main`
- Build automático
- Health checks

### **Vercel:**
- Auto-deploy en push a `main`
- Preview deployments en PRs
- Instant rollbacks

---

## 📊 **Monitoreo:**

### **Render:**
- Logs en tiempo real
- Métricas de CPU/RAM
- Health checks

### **Vercel:**
- Analytics de visitas
- Performance metrics
- Error tracking

---

## 🎉 **¡Listo!**

Tu aplicación estará disponible en:
- **Frontend**: `https://agent-legal-frontend.vercel.app`
- **Backend**: `https://agent-legal-backend.onrender.com`

**Costo total: $0/mes** 🎉

---

## 🔧 **Troubleshooting**

### **Problemas Comunes:**

#### **Backend no inicia en Render:**
```bash
# Verificar logs en Render Dashboard
# Problema común: Variables de entorno faltantes
# Solución: Agregar todas las variables en Render Dashboard
```

#### **Frontend no se conecta al Backend:**
```bash
# Verificar NEXT_PUBLIC_API_URL en Vercel
# Debe ser: https://agent-legal-backend.onrender.com
# NO usar localhost en producción
```

#### **Error de CORS:**
```bash
# El backend ya tiene CORS configurado
# Si persiste, verificar ALLOWED_ORIGINS en Render
```

#### **Backend se duerme (Render Free):**
```bash
# Normal en plan free - se despierta automáticamente
# Tiempo de wake-up: ~30 segundos
# Para evitar: usar plan Starter ($7/mes)
```

### **Verificar Despliegue:**
```bash
# Backend health check
curl https://agent-legal-backend.onrender.com/health

# Frontend
curl https://agent-legal-frontend.vercel.app

# API docs
curl https://agent-legal-backend.onrender.com/docs
```

### **Logs y Debugging:**
- **Render**: Dashboard → Logs en tiempo real
- **Vercel**: Dashboard → Functions → Logs
- **GitHub**: Actions para ver builds
