# ✅ Checklist de Deployment - Sistema Legal Multiagente

## 📋 Pre-Deployment

### Repositorio
- [ ] Repositorio creado en GitHub
- [ ] Código subido al repositorio
- [ ] Archivos de configuración incluidos:
  - [ ] `backend/render.yaml`
  - [ ] `backend/pyproject.toml`
  - [ ] `backend/Dockerfile`
  - [ ] `backend/env_example.txt`
  - [ ] `frontend/vercel.json`
  - [ ] `frontend/env_example.txt`

### APIs Externas
- [ ] **OpenAI API Key** obtenida y configurada
- [ ] **Pinecone API Key** obtenida y configurada
- [ ] **Índice Pinecone** creado:
  - [ ] Nombre: `legal-colombia-docs`
  - [ ] Dimensions: `1536`
  - [ ] Metric: `cosine`
  - [ ] Environment: `us-east-1-aws`

### Documentos Legales
- [ ] Documentos en `backend/docs/legal/`
- [ ] Scripts de importación funcionando
- [ ] Documentos importados en Pinecone
- [ ] Verificación de importación exitosa

---

## 🖥️ Backend (Render)

### Configuración
- [ ] Cuenta en Render creada
- [ ] Web Service creado:
  - [ ] Nombre: `legal-agent-api`
  - [ ] Environment: Python 3
  - [ ] Region: Oregon
  - [ ] Branch: main
  - [ ] Root Directory: backend
  - [ ] Build Command: `pip install -e .`
  - [ ] Start Command: `uvicorn src.app.main:app --host 0.0.0.0 --port $PORT`

### Variables de Entorno
- [ ] `OPENAI_API_KEY` configurada
- [ ] `PINECONE_API_KEY` configurada
- [ ] `PINECONE_INDEX_NAME` configurada
- [ ] `PINECONE_ENVIRONMENT` configurada
- [ ] `ELEVENLABS_API_KEY` configurada (opcional)
- [ ] `AWS_ACCESS_KEY_ID` configurada (opcional)
- [ ] `AWS_SECRET_ACCESS_KEY` configurada (opcional)

### Deployment
- [ ] Build exitoso
- [ ] Service iniciado correctamente
- [ ] Health check funcionando: `/health`
- [ ] RAG status operacional: `/rag/status`
- [ ] API docs accesibles: `/docs`

### URLs Backend
- [ ] URL del servicio: `https://legal-agent-api.onrender.com`
- [ ] Health check: `https://legal-agent-api.onrender.com/health`
- [ ] API docs: `https://legal-agent-api.onrender.com/docs`

---

## 🌐 Frontend (Vercel)

### Configuración
- [ ] Cuenta en Vercel creada
- [ ] Proyecto importado:
  - [ ] Framework: Next.js
  - [ ] Root Directory: frontend
  - [ ] Build Command: `npm run build`
  - [ ] Output Directory: `.next`

### Variables de Entorno
- [ ] `NEXT_PUBLIC_API_BASE_URL` configurada con URL del backend

### Deployment
- [ ] Build exitoso
- [ ] Frontend desplegado correctamente
- [ ] Página principal carga
- [ ] Formulario de consulta funciona
- [ ] Respuestas del RAG aparecen

### URLs Frontend
- [ ] URL del frontend: `https://sistema-legal-ia.vercel.app`

---

## 🧪 Testing

### Pruebas Básicas
- [ ] Health check backend: `curl https://legal-agent-api.onrender.com/health`
- [ ] RAG status: `curl https://legal-agent-api.onrender.com/rag/status`
- [ ] Frontend carga: Visitar URL del frontend

### Pruebas de Consultas Legales
- [ ] "¿Cómo constituyo una SAS en Colombia?"
- [ ] "¿Cómo calcular las prestaciones sociales?"
- [ ] "¿Cómo presentar la declaración de renta?"
- [ ] "¿Qué documentos necesito para un contrato de trabajo?"

### Funcionalidades
- [ ] **Consultas RAG:** Respuestas basadas en documentos legales
- [ ] **Categorización:** Detecta área legal correcta
- [ ] **Fuentes:** Muestra documentos de referencia
- [ ] **Sugerencias:** Genera preguntas relacionadas
- [ ] **Voz:** Speech-to-text y text-to-speech (si configurado)

---

## 🔧 Configuración Avanzada

### Monitoreo
- [ ] Logs de Render accesibles
- [ ] Logs de Vercel accesibles
- [ ] Health checks automáticos funcionando

### Optimización
- [ ] Plan Starter en Render (opcional, $7/mes)
- [ ] CDN de Vercel funcionando
- [ ] Cache de respuestas implementado

### Seguridad
- [ ] Variables de entorno seguras
- [ ] CORS configurado correctamente
- [ ] Headers de seguridad activos

---

## 📊 Costos

### Plan Básico
- [ ] OpenAI: $10-20/mes
- [ ] Pinecone: Gratis
- [ ] Render: Gratis
- [ ] Vercel: Gratis
- [ ] **Total: ~$15/mes**

### Plan Optimizado (Opcional)
- [ ] OpenAI: $10-20/mes
- [ ] Pinecone: Gratis
- [ ] Render Starter: $7/mes
- [ ] Vercel Pro: $20/mes
- [ ] **Total: ~$40/mes**

---

## 🎉 Deployment Completado


### Verificación Final
- [ ] Sistema completo operacional
- [ ] Consultas legales responden correctamente
- [ ] Fuentes se muestran
- [ ] Categorización funciona
- [ ] Interfaz responsive
- [ ] Performance aceptable

---

## 🆘 Troubleshooting

### Problemas Comunes
- [ ] Build failed en Render → Verificar variables de entorno
- [ ] RAG no funciona → Verificar documentos importados
- [ ] CORS error → Verificar URLs y configuración
- [ ] Cold start lento → Considerar upgrade de plan

### Logs y Debugging
- [ ] Logs de Render accesibles
- [ ] Logs de Vercel accesibles
- [ ] Health checks funcionando
- [ ] API endpoints respondiendo

---
