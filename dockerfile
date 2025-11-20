# Imagen base con Python 3.10
FROM python:3.10-slim

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Configuración de cache para modelos TTS
ENV HF_HOME=/opt/cache/huggingface
ENV TORCH_HOME=/opt/cache/torch
ENV XDG_CACHE_HOME=/opt/cache

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    libsndfile1 \
    build-essential \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivo de dependencias
COPY requirements.txt /opt/requirements.txt

# Crear entorno virtual e instalar dependencias
RUN python -m venv /opt/.venv \
    && /opt/.venv/bin/pip install --upgrade pip setuptools wheel \
    && /opt/.venv/bin/pip install --no-cache-dir -r /opt/requirements.txt

# Los modelos YourTTS y XTTS v2 están incluidos en el paquete TTS
# Se descargarán automáticamente al primer uso

# Establecer directorio de trabajo
WORKDIR /opt/project

# Copiar código fuente
COPY . /opt/project

# Crear directorios necesarios
RUN mkdir -p \
    /opt/project/outputs/xtts \
    /opt/project/outputs/yourtts \
    /opt/project/inputs \
    /opt/cache/huggingface \
    /opt/cache/torch

# Configurar volúmenes para persistencia
VOLUME ["/opt/project/outputs", "/opt/project/inputs", "/opt/cache"]

# Comando por defecto - mostrar ayuda
CMD ["python", "main.py", "--help"]
