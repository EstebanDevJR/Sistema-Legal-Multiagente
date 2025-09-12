# 🔧 Variables de Entorno para Desarrollo Local

## Backend (.env)

```env
# OpenAI API Key (REQUERIDO)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Base de datos PostgreSQL (REQUERIDO)
DATABASE_URL=postgresql://usuario:password@localhost:5432/legal_db

# Clave secreta para JWT (REQUERIDO)
SECRET_KEY=your-super-secret-key-here

# Configuración del servidor
HOST=0.0.0.0
PORT=8000

# Configuración de CORS
CORS_ORIGINS=http://localhost:3000

# Configuración de logging
LOG_LEVEL=INFO
```

## Frontend (.env.local)

```env
# URL del backend (REQUERIDO)
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Deshabilitar telemetría de Next.js
NEXT_TELEMETRY_DISABLED=1
```

## Configuración RAG (Opcional)

```env
# Configuración de embeddings
EMBEDDING_MODEL=text-embedding-3-small
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Configuración de búsqueda
MAX_RESULTS=5
SIMILARITY_THRESHOLD=0.7
```

## Configuración de Voz (Opcional)

```env
# Configuración de síntesis de voz
TTS_MODEL=tts-1
TTS_VOICE=alloy

# Configuración de transcripción
STT_MODEL=whisper-1
```

## 📝 Notas

- **REQUERIDO**: Solo `OPENAI_API_KEY`, `DATABASE_URL` y `SECRET_KEY` son obligatorios
- **Opcional**: Las demás variables tienen valores por defecto
- **Desarrollo**: Estas configuraciones son para desarrollo local únicamente
