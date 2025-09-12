# 🛠️ Guía de Desarrollo Local

Esta guía te ayudará a configurar el entorno de desarrollo local para el Sistema Legal Multiagente.

## 📋 Prerrequisitos

- Python 3.11+
- Node.js 18+
- PostgreSQL
- Git

## 🚀 Configuración Inicial

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/sistema-legal-multiagente.git
cd sistema-legal-multiagente
```

### 2. Configurar Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -e .
```

### 3. Configurar Frontend

```bash
cd frontend
npm install
```

### 4. Configurar Base de Datos

```bash
# Crear base de datos
createdb legal_db
```

### 5. Configurar Variables de Entorno

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

## 🔧 Comandos de Desarrollo

### Backend

```bash
# Ejecutar en modo desarrollo
uvicorn src.app.main:app --reload --port 8000

# Ejecutar tests
pytest

# Linting
black src/
flake8 src/
```

### Frontend

```bash
# Ejecutar en modo desarrollo
npm run dev

# Ejecutar tests
npm test

# Linting
npm run lint

# Build
npm run build
```

## 🏗️ Estructura del Proyecto

```
├── backend/
│   ├── src/
│   │   ├── agent/          # Agentes de IA
│   │   ├── api/            # Endpoints de la API
│   │   ├── core/           # Servicios principales
│   │   ├── models/         # Modelos de datos
│   │   └── services/       # Servicios de negocio
│   ├── docs/               # Documentos legales
│   └── tests/              # Tests del backend
├── frontend/
│   ├── app/                # Páginas de Next.js
│   ├── components/         # Componentes React
│   ├── hooks/              # Custom hooks
│   ├── lib/                # Utilidades
│   └── styles/             # Estilos CSS
└── docs/                   # Documentación
```

## 🧪 Testing

### Backend

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests específicos
pytest tests/unit_tests/test_configuration.py

# Tests con cobertura
pytest --cov=src tests/
```

### Frontend

```bash
# Ejecutar tests
npm test

# Tests con cobertura
npm run test:coverage
```

## 🔍 Debugging

### Backend

```bash
# Ejecutar con debug
uvicorn src.app.main:app --reload --log-level debug
```

### Frontend

```bash
# Ejecutar con debug
npm run dev -- --inspect
```

## 📝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature
3. Haz commit de tus cambios
4. Push a la rama
5. Abre un Pull Request

### Estándares de Código

- **Python**: Black, Flake8
- **TypeScript**: ESLint, Prettier
- **Commits**: Conventional Commits
- **Tests**: Cobertura mínima del 80%

## 🐛 Solución de Problemas

### Error de Dependencias

```bash
# Limpiar cache de pip
pip cache purge

# Reinstalar dependencias
pip install -e . --force-reinstall
```

### Error de Node Modules

```bash
# Limpiar cache de npm
npm cache clean --force

# Reinstalar dependencias
rm -rf node_modules package-lock.json
npm install
```

### Error de Base de Datos

```bash
# Verificar conexión
psql -h localhost -U usuario -d legal_db

# Recrear base de datos
dropdb legal_db
createdb legal_db
```

## 📚 Recursos Adicionales

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
