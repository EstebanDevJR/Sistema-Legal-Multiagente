"""
Aplicación principal FastAPI para el Sistema Legal Multiagente
"""

import os
import time
import logging
import warnings
from contextlib import asynccontextmanager

# Suprimir warnings específicos de compatibilidad
warnings.filterwarnings("ignore", message=".*pydantic_v1.*", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain_pinecone")
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Importar routers
from ..api.legal.rag_api import router as rag_router
from ..api.voice.voice_api import router as voice_router
from ..api.documents.documents_api import router as documents_router
from ..api.chat.chat_api import router as chat_router
from ..api.email.email_api import router as email_router

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("🚀 Iniciando Sistema Legal Multiagente...")
    
    # Verificar variables de entorno críticas
    required_env_vars = ["OPENAI_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"⚠️ Variables de entorno faltantes: {missing_vars}")
        logger.warning("El sistema funcionará con capacidades limitadas")
    else:
        logger.info("✅ Variables de entorno configuradas correctamente")
    
    # Verificar servicios opcionales
    optional_services = {
        "ELEVENLABS_API_KEY": "Síntesis de voz",
        "AWS_ACCESS_KEY_ID": "Almacenamiento S3",
        "LANGSMITH_API_KEY": "Monitoreo LangSmith"
    }
    
    for var, service in optional_services.items():
        if os.getenv(var):
            logger.info(f"✅ {service} habilitado")
        else:
            logger.info(f"ℹ️ {service} no configurado (opcional)")
    
    yield
    
    # Shutdown
    logger.info("🛑 Cerrando Sistema Legal Multiagente...")

# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema Legal Multiagente Colombia",
    description="""
    Sistema inteligente para consultas legales colombianas usando IA multiagente.
    
    ## Características
    
    * **Consultas RAG**: Respuestas basadas en legislación colombiana
    * **Multiagente**: Especialistas en Civil, Comercial, Laboral y Tributario  
    * **Voz**: Speech-to-text y text-to-speech con ElevenLabs
    * **Documentos**: Almacenamiento en AWS S3 con fallback local
    * **Tiempo real**: Respuestas rápidas y precisas
    
    ## Áreas Legales Soportadas
    
    * 🏛️ **Derecho Civil**: Contratos, familia, sucesiones
    * 🏪 **Derecho Comercial**: Sociedades, registro mercantil
    * 👥 **Derecho Laboral**: Contratos, prestaciones, liquidaciones
    * 💰 **Derecho Tributario**: Impuestos, DIAN, declaraciones
    """,
    version="1.0.0",
    contact={
        "name": "Sistema Legal IA",
        "email": "soporte@legalai.co"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    lifespan=lifespan
)

# Configurar CORS (permitidos vía variable de entorno ALLOWED_ORIGINS, separados por coma)
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
default_allowed = [
    "http://localhost:3000",
    "http://localhost:5173",
]
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()] if allowed_origins_env else default_allowed

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "User-Agent", "X-Requested-With"],
    max_age=600,
)

# Middleware de seguridad
trusted_hosts_env = os.getenv("TRUSTED_HOSTS")
trusted_hosts = [h.strip() for h in trusted_hosts_env.split(",") if h.strip()] if trusted_hosts_env else ["localhost", "127.0.0.1"]

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=trusted_hosts
)

# Middleware GZip para compresión
app.add_middleware(GZipMiddleware, minimum_size=1024)

# Middleware personalizado para cabeceras de seguridad
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Middleware para agregar cabeceras de seguridad"""
    response = await call_next(request)
    
    # Agregar cabeceras de seguridad
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "origin-when-cross-origin"
    
    # HSTS solo en HTTPS
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"

    return response

# Incluir routers
app.include_router(rag_router)
app.include_router(voice_router)
app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(email_router)

# Servir archivos estáticos si existen
if os.path.exists("./static"):
    app.mount("/static", StaticFiles(directory="./static"), name="static")

# Rutas principales
@app.get("/")
async def root():
    """Ruta principal con información del sistema"""
    return {
        "message": "🏛️ Sistema Legal Multiagente Colombia",
        "version": "1.0.0",
        "status": "operational",
        "features": [
            "Consultas legales RAG",
            "Sistema multiagente especializado", 
            "Servicios de voz (STT/TTS)",
            "Gestión de documentos",
            "API REST completa"
        ],
        "areas_legales": [
            "Civil", "Comercial", "Laboral", "Tributario"
        ],
        "endpoints": {
            "rag": "/rag/*",
            "voice": "/voice/*", 
            "documents": "/documents/*",
            "docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check general del sistema"""
    try:
        # Verificar componentes críticos
        health_status = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "components": {
                "api": "healthy",
                "database": "healthy",  # Placeholder
                "external_services": {
                    "openai": "healthy" if os.getenv("OPENAI_API_KEY") else "unavailable",
                    "pinecone": "healthy" if os.getenv("PINECONE_API_KEY") else "unavailable",
                    "elevenlabs": "healthy" if os.getenv("ELEVENLABS_API_KEY") else "unavailable",
                    "aws_s3": "healthy" if os.getenv("AWS_ACCESS_KEY_ID") else "unavailable"
                }
            },
            "version": "1.0.0"
        }
        
        # Determinar estado general
        critical_services = ["openai", "pinecone"]
        if any(health_status["components"]["external_services"][service] == "unavailable" 
               for service in critical_services):
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

@app.get("/info")
async def system_info():
    """Información detallada del sistema"""
    return {
        "name": "Sistema Legal Multiagente Colombia",
        "description": "IA especializada en derecho colombiano",
        "version": "1.0.0",
        "python_version": "3.9+",
        "framework": "FastAPI",
        "ai_stack": [
            "LangChain",
            "LangGraph", 
            "OpenAI GPT-4",
            "Pinecone Vector DB",
            "ElevenLabs TTS"
        ],
        "deployment": {
            "backend": "Render.com",
            "frontend": "Vercel",
            "storage": "AWS S3"
        },
        "legal_areas": {
            "civil": "Contratos civiles, familia, sucesiones",
            "comercial": "Sociedades, registro mercantil, títulos valores",
            "laboral": "Contratos trabajo, prestaciones, liquidaciones", 
            "tributario": "Impuestos, DIAN, régimen tributario"
        }
    }

# Manejador de errores global
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Manejador personalizado para errores HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "path": str(request.url.path),
            "method": request.method
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Manejador para errores generales"""
    logger.error(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "message": "Error interno del servidor",
            "path": str(request.url.path),
            "method": request.method
        }
    )

# Middleware de logging básico
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logging de requests con manejo mejorado de conexiones"""
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log solo requests importantes (no health checks)
        if request.url.path not in ["/health", "/"]:
            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"❌ Request failed: {request.method} {request.url.path} - {str(e)} - Time: {process_time:.3f}s")
        raise

# Rate limiting básico por IP (en memoria, para despliegues pequeños)
_rate_limit_store = {}
REQUESTS_PER_MINUTE = int(os.getenv("REQUESTS_PER_MINUTE", "300"))  # Aumentado para producción

@app.middleware("http")
async def basic_rate_limit(request: Request, call_next):
    try:
        # No aplicar rate limiting a health checks y requests internos
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)
            
        client_ip = request.client.host if request.client else "unknown"
        now = int(time.time())
        window = now // 60
        key = f"{client_ip}:{window}"
        count = _rate_limit_store.get(key, 0) + 1
        _rate_limit_store[key] = count
        # Limpieza básica de ventanas anteriores
        old_window = (now - 120) // 60
        for k in list(_rate_limit_store.keys()):
            if k.endswith(f":{old_window}"):
                _rate_limit_store.pop(k, None)
        if count > REQUESTS_PER_MINUTE:
            return JSONResponse(status_code=429, content={
                "error": True,
                "message": "Demasiadas solicitudes. Inténtalo de nuevo en un minuto.",
            })
        response = await call_next(request)
        # Añadir cabeceras informativas
        remaining = max(0, REQUESTS_PER_MINUTE - count)
        response.headers["X-RateLimit-Limit"] = str(REQUESTS_PER_MINUTE)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
    except Exception:
        # En caso de error en el limiter, no bloquear la petición
        return await call_next(request)

if __name__ == "__main__":
    # Configuración para desarrollo
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level="info"
    )
