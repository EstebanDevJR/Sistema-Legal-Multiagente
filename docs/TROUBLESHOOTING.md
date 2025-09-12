# 🆘 Guía de Troubleshooting - Desarrollo Local

## 🚨 Problemas Comunes y Soluciones

### 🔧 **Problemas de Instalación**

#### ❌ **Error de dependencias Python**

**Síntomas:**
- Error durante `pip install -e .`
- Dependencias no encontradas
- Conflictos de versiones

**Soluciones:**
```bash
# 1. Limpiar cache de pip
pip cache purge

# 2. Reinstalar dependencias
cd backend
pip install -e . --force-reinstall

# 3. Si falla, actualizar herramientas
pip install --upgrade pip setuptools wheel
```

#### ❌ **Error de dependencias Node.js**

**Síntomas:**
- Error durante `npm install`
- Módulos no encontrados
- Conflictos de versiones

**Soluciones:**
```bash
# 1. Limpiar cache de npm
npm cache clean --force

# 2. Eliminar node_modules y reinstalar
cd frontend
rm -rf node_modules package-lock.json
npm install

# 3. Si falla, actualizar npm
npm install -g npm@latest
```

### 🗄️ **Problemas de Base de Datos**

#### ❌ **Error de conexión a PostgreSQL**

**Síntomas:**
- `psycopg2.OperationalError`
- `connection refused`
- Base de datos no encontrada

**Soluciones:**
```bash
# 1. Verificar que PostgreSQL esté ejecutándose
# En macOS con Homebrew:
brew services start postgresql

# En Ubuntu/Debian:
sudo systemctl start postgresql

# En Windows: Iniciar desde Services

# 2. Verificar conexión
psql -h localhost -U tu_usuario -d legal_db

# 3. Crear base de datos si no existe
createdb legal_db
```

#### ❌ **Error de migraciones**

**Síntomas:**
- Tablas no encontradas
- Error de esquema
- Datos corruptos

**Soluciones:**
```bash
# 1. Recrear base de datos
dropdb legal_db
createdb legal_db

# 2. Ejecutar setup RAG
cd backend
python scripts/setup_rag.py
```

### 🤖 **Problemas de OpenAI**

#### ❌ **Error de API Key**

**Síntomas:**
- `Invalid API key`
- `Authentication failed`
- `Rate limit exceeded`

**Soluciones:**
```bash
# 1. Verificar API key en .env
cat backend/.env | grep OPENAI_API_KEY

# 2. Verificar que la key sea válida
# Visita: https://platform.openai.com/api-keys

# 3. Verificar créditos disponibles
# Visita: https://platform.openai.com/usage
```

#### ❌ **Error de modelos**

**Síntomas:**
- `Model not found`
- `Model not available`
- Timeout en requests

**Soluciones:**
```bash
# 1. Verificar que el modelo esté disponible
# Visita: https://platform.openai.com/docs/models

# 2. Cambiar a un modelo alternativo
# En .env: EMBEDDING_MODEL=text-embedding-3-small
```

### 🎨 **Problemas de Frontend**

#### ❌ **Error 404 en localhost:3000**

**Síntomas:**
- Página no carga
- Error de conexión
- API no responde

**Soluciones:**
```bash
# 1. Verificar que el backend esté ejecutándose
curl http://localhost:8000/health

# 2. Verificar variables de entorno
cat frontend/.env.local

# 3. Reiniciar ambos servicios
# Backend: uvicorn src.app.main:app --reload --port 8000
# Frontend: npm run dev
```

#### ❌ **Error de CORS**

**Síntomas:**
- `CORS policy` en consola
- Requests bloqueados
- API no accesible

**Soluciones:**
```bash
# 1. Verificar CORS_ORIGINS en backend/.env
CORS_ORIGINS=http://localhost:3000

# 2. Reiniciar backend
uvicorn src.app.main:app --reload --port 8000
```

### 🔍 **Problemas de RAG**

#### ❌ **RAG no funciona**

**Síntomas:**
- No encuentra documentos
- Respuestas genéricas
- Error de embeddings

**Soluciones:**
```bash
# 1. Verificar que los documentos estén en la carpeta correcta
ls backend/docs/legal/

# 2. Ejecutar setup RAG
cd backend
python scripts/setup_rag.py

# 3. Verificar base de datos
python scripts/verify_rag_compatibility.py
```

### 🎤 **Problemas de Voz**

#### ❌ **Audio no se reproduce**

**Síntomas:**
- Audio no carga
- Error de CORS
- URL duplicada

**Soluciones:**
```bash
# 1. Verificar que el backend esté ejecutándose
curl http://localhost:8000/health

# 2. Verificar variables de entorno
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# 3. Revisar consola del navegador para errores
```

## 🔍 **Debugging Avanzado**

### Logs del Backend

```bash
# Ejecutar con logs detallados
uvicorn src.app.main:app --reload --log-level debug
```

### Logs del Frontend

```bash
# Ejecutar con logs detallados
npm run dev -- --inspect
```

### Verificar Estado del Sistema

```bash
# 1. Verificar puertos
lsof -i :8000  # Backend
lsof -i :3000  # Frontend

# 2. Verificar procesos
ps aux | grep uvicorn
ps aux | grep next

# 3. Verificar memoria
free -h  # Linux/macOS
```

## 📞 **Obtener Ayuda**

1. **Revisar logs**: Siempre revisa los logs de error
2. **Verificar variables**: Asegúrate de que todas las variables de entorno estén configuradas
3. **Reiniciar servicios**: Muchos problemas se solucionan reiniciando
4. **Crear issue**: Si nada funciona, crea un issue en GitHub con:
   - Sistema operativo
   - Versiones de Python/Node.js
   - Logs de error completos
   - Pasos para reproducir el problema