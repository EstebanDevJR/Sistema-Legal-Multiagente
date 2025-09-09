# 🏛️ Sistema Legal Multiagente Colombia

[![Deploy to Render](https://img.shields.io/badge/Deploy%20Backend-Render-blue)](https://render.com)
[![Deploy to Vercel](https://img.shields.io/badge/Deploy%20Frontend-Vercel-black)](https://vercel.com)
[![Python](https://img.shields.io/badge/Python-3.9+-green)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black)](https://nextjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

Sistema inteligente de consultas legales especializado en derecho colombiano, construido con IA multiagente, RAG y servicios de voz.

## ✨ Características Principales

- 🤖 **Sistema Multiagente**: Especialistas en Civil, Comercial, Laboral y Tributario
- 🧠 **RAG Avanzado**: Respuestas basadas en legislación colombiana real
- 🎤 **Servicios de Voz**: Speech-to-text y text-to-speech con ElevenLabs
- 📄 **Gestión de Documentos**: Almacenamiento seguro en AWS S3
- ⚡ **API REST Completa**: FastAPI con documentación automática
- 🚀 **Deploy Listo**: Configurado para Render.com y Vercel

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Servicios     │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   Externos      │
│                 │    │                 │    │                 │
│ • React/TS      │    │ • LangGraph     │    │ • OpenAI        │
│ • Tailwind      │    │ • LangChain     │    │ • Pinecone      │
│ • shadcn/ui     │    │ • FastAPI       │    │ • ElevenLabs    │
│ • Voice UI      │    │ • Pydantic      │    │ • AWS S3        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Deploy Rápido

### ⚡ **¿Quieres deployar en 5 minutos?**

**[📖 Guía de Inicio Rápido](docs/QUICK_START.md)** - Deploy completo paso a paso

### 🎯 **Demo en Vivo**
- **Frontend:** [https://legal-agent.vercel.app](https://legal-agent.vercel.app)
- **API Docs:** [https://legal-agent-api.onrender.com/docs](https://legal-agent-api.onrender.com)

## 🎯 Áreas Legales Soportadas

### 🏛️ Derecho Civil
- Contratos civiles
- Derecho de familia
- Sucesiones y herencias
- Responsabilidad civil

### 🏪 Derecho Comercial
- Constitución de sociedades
- Registro mercantil
- Contratos comerciales
- Títulos valores

### 👥 Derecho Laboral
- Contratos de trabajo
- Prestaciones sociales
- Liquidación laboral
- Seguridad social

### 💰 Derecho Tributario
- Declaración de renta
- IVA y retenciones
- Régimen tributario
- Procedimientos DIAN

## 🛠️ Tecnologías

### Backend
- **Python 3.9+** - Lenguaje principal
- **FastAPI** - Framework web
- **LangGraph** - Orquestación de agentes
- **LangChain** - Framework de IA
- **OpenAI GPT-4** - Modelo de lenguaje
- **Pinecone** - Base de datos vectorial
- **ElevenLabs** - Síntesis de voz

### Frontend
- **Next.js 14** - Framework React
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Estilos
- **shadcn/ui** - Componentes
- **React Hook Form** - Formularios
- **Zod** - Validación

### Deployment
- **Render.com** - Backend hosting
- **Vercel** - Frontend hosting
- **AWS S3** - Almacenamiento
- **GitHub Actions** - CI/CD

## 📚 Documentación

- 🚀 **[Guía de Deployment](docs/DEPLOYMENT.md)** - Proceso completo paso a paso
- 🗄️ **[Configuración RAG](docs/RAG_SETUP_GUIDE.md)** - Setup de Pinecone y datos
- 🆘 **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Solución a problemas
- 🔑 **[Variables de Entorno](docs/ENVIRONMENT_VARIABLES_GUIDE.md)** - Configuración completa
- ✅ **[Checklist de Deployment](docs/DEPLOYMENT_CHECKLIST.md)** - Lista de verificación

## 🚀 Instalación Local

### Prerrequisitos
- Python 3.9+
- Node.js 18+
- API Keys (ver [Variables de Entorno](ENVIRONMENT_VARIABLES_GUIDE.md))

### Setup Rápido

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/agentLegal.git
cd agentLegal

# 2. Configurar backend
cd backend
cp env_example.txt .env
# Editar .env con tus API keys
pip install -e .

# 3. Configurar frontend
cd ../frontend
npm install
cp .env.example .env.local
# Editar .env.local con NEXT_PUBLIC_API_URL=http://localhost:8000

# 4. Ejecutar
# Terminal 1: Backend
uvicorn src.app.main:app --reload --port 8000

# Terminal 2: Frontend
npm run dev
```

### Verificar Instalación
- **Backend:** http://localhost:8000/docs
- **Frontend:** http://localhost:3000
- **Health Check:** http://localhost:8000/health

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ --cov=src

# Frontend tests
cd frontend
npm test
```

## 📊 API Endpoints

### RAG Legal (`/rag/*`)
- `POST /rag/query` - Consulta legal principal
- `GET /rag/suggestions` - Sugerencias por categoría
- `GET /rag/examples` - Ejemplos de consultas
- `GET /rag/status` - Estado del sistema RAG

### Servicios de Voz (`/voice/*`)
- `POST /voice/speech-to-text` - Audio a texto
- `POST /voice/text-to-speech` - Texto a audio
- `POST /voice/voice-query` - Consulta completa por voz
- `GET /voice/download/{audio_id}` - Descargar audio

### Gestión de Documentos (`/documents/*`)
- `POST /documents/upload` - Subir documento
- `GET /documents/user/{user_id}` - Documentos del usuario
- `GET /documents/download/{user_id}/{doc_id}` - Descargar documento
- `DELETE /documents/delete/{user_id}/{doc_id}` - Eliminar documento

## 💰 Costos Estimados

### Plan Básico (Solo APIs requeridas)
- **OpenAI:** $10-20/mes
- **Pinecone:** Gratis (100K vectores)
- **Render:** Gratis (con limitaciones)
- **Vercel:** Gratis
- **Total:** ~$15/mes

### Plan Completo (Todas las funcionalidades)
- **OpenAI:** $10-20/mes
- **Pinecone:** Gratis
- **ElevenLabs:** Gratis (10K caracteres)
- **AWS S3:** $1-5/mes
- **Render Starter:** $7/mes
- **Total:** ~$25/mes

## 🤝 Contribución

1. Fork el repositorio
2. Crea una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

Ver [Guía de Deployment](docs/DEPLOYMENT.md) para más detalles.

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 🆘 Soporte

### Problemas Comunes
- **Error de API Keys**: Ver [Variables de Entorno](ENVIRONMENT_VARIABLES_GUIDE.md)
- **Deploy fallido**: Ver [Troubleshooting](docs/TROUBLESHOOTING.md)
- **CORS errors**: Verificar variables de entorno

### Contacto
- 📧 Email: esteban.ortiz.dev@gmail.com


## 🌟 Estrellas

Si este proyecto te resulta útil, ¡dale una estrella! ⭐

---

**Desarrollado por Esteban Ortiz ❤️ para la comunidad legal colombiana**
