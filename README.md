# Sistema Legal Multiagente

Un sistema de inteligencia artificial especializado en consultas legales colombianas, construido con FastAPI y Next.js.

## 🚀 Características

- **Consultas Legales Inteligentes**: Respuestas basadas en la legislación colombiana
- **Múltiples Agentes Especializados**: Agentes para diferentes áreas del derecho
- **Interfaz de Voz**: Grabación y síntesis de voz para consultas
- **RAG (Retrieval Augmented Generation)**: Búsqueda semántica en documentos legales
- **Interfaz Moderna**: UI responsive con Next.js y Tailwind CSS

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   RAG System    │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (Vector DB)   │
│                 │    │                 │    │                 │
│ • Chat UI       │    │ • Legal Agents  │    │ • Documentos    │
│ • Voice Recorder│    │ • Voice API     │    │ • Embeddings    │
│ • Document Mgmt │    │ • RAG Service   │    │ • Search        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Requisitos

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL** (para vector storage)
- **OpenAI API Key**

## 🛠️ Instalación

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -e .
```

### Frontend

```bash
cd frontend
npm install
```

## ⚙️ Configuración

### Variables de Entorno

**Backend** (`backend/.env`):
```env
OPENAI_API_KEY=tu_api_key_aqui
DATABASE_URL=postgresql://usuario:password@localhost:5432/legal_db
SECRET_KEY=tu_secret_key_aqui
```

**Frontend** (`frontend/.env.local`):
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## 🚀 Ejecución Local

### Desarrollo

**Backend:**
```bash
cd backend
uvicorn src.app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

**Acceder a la aplicación:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentación API: http://localhost:8000/docs

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

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🙏 Agradecimientos

- [LangGraph](https://github.com/langchain-ai/langgraph) - Framework para agentes
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web
- [Next.js](https://nextjs.org/) - Framework React
- [OpenAI](https://openai.com/) - Modelos de IA