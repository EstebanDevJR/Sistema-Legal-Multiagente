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

## 🎯 Áreas Legales Soportadas

### 🏛️ Derecho Civil
- Contratos civiles
- Derecho de familia
- Sucesiones y herencias
- Derecho de propiedad
- Responsabilidad civil

### 🏢 Derecho Comercial
- Sociedades comerciales
- Contratos mercantiles
- Títulos valores
- Derecho concursal
- Propiedad industrial

### 👷 Derecho Laboral
- Contratos de trabajo
- Prestaciones sociales
- Derecho sindical
- Seguridad social
- Accidentes de trabajo

### 💰 Derecho Tributario
- Impuestos nacionales
- Impuestos territoriales
- Procedimientos tributarios
- Sanciones fiscales
- Régimen cambiario

## 🚀 Deploy Rápido

### ⚡ **¿Quieres deployar en 5 minutos?**

**[📖 Guía de Inicio Rápido](docs/QUICK_START.md)** - Deploy completo paso a paso

### 🎯 **Demo en Vivo**
- **Frontend:** [https://legal-agent.vercel.app](https://legal-agent.vercel.app)
- **API Docs:** [https://legal-agent-api.onrender.com/docs](https://legal-agent-api.onrender.com)

## 📋 Requisitos

### Prerrequisitos
- Python 3.9+
- Node.js 18+
- API Keys (ver [Variables de Entorno](docs/ENVIRONMENT_VARIABLES_GUIDE.md))

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

## 📚 Documentación

- [Guía de Desarrollo](docs/DEVELOPMENT.md) - Configuración del entorno de desarrollo
- [Variables de Entorno](docs/ENV_EXAMPLE.md) - Configuración de variables
- [Guía de RAG](docs/RAG_SETUP_GUIDE.md) - Configuración del sistema RAG
- [Solución de Problemas](docs/TROUBLESHOOTING.md) - Errores comunes y soluciones

## 🚀 Despliegue

Para desplegar en producción, consulta la documentación oficial de:
- **Frontend**: [Vercel](https://vercel.com/docs) o [Netlify](https://docs.netlify.com/)
- **Backend**: [Render](https://render.com/docs) o [Railway](https://docs.railway.app/)
- **Base de Datos**: [Supabase](https://supabase.com/docs) o [Neon](https://neon.tech/docs)

## 🤝 Contribución

1. Fork el repositorio
2. Crea una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

Ver [Guía de Deployment](docs/DEPLOYMENT.md) para más detalles.

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- [LangGraph](https://github.com/langchain-ai/langgraph) - Framework para agentes
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web
- [Next.js](https://nextjs.org/) - Framework React
- [OpenAI](https://openai.com/) - Modelos de IA

## 🆘 Soporte

### Problemas Comunes
- **Error de API Keys**: Ver [Variables de Entorno](docs/ENVIRONMENT_VARIABLES_GUIDE.md)
- **Deploy fallido**: Ver [Troubleshooting](docs/TROUBLESHOOTING.md)
- **CORS errors**: Verificar variables de entorno

### Contacto
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/agentLegal/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/tu-usuario/agentLegal/discussions)

Si este proyecto te resulta útil, ¡dale una estrella! ⭐

---

**Desarrollado por Esteban Ortiz ❤️ para la comunidad legal colombiana**