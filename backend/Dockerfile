# Dockerfile para deployment del Sistema Legal Multiagente

FROM python:3.11-slim

# Configurar directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de configuración
COPY pyproject.toml ./

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -e .

# Copiar código fuente
COPY src/ ./src/
COPY langgraph.json ./

# Crear directorios necesarios
RUN mkdir -p ./uploads ./temp_audio ./logs \
    && adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app

USER appuser

# Configurar variables de entorno por defecto
ENV PYTHONPATH=/app
ENV PORT=8000
ENV ENVIRONMENT=production

# Exponer puerto
EXPOSE $PORT

# Configurar health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:$PORT/health || exit 1

# Comando por defecto
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
