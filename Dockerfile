# ── Imagen base ──────────────────────────────────────────────────────────────
FROM python:3.11-slim
 
LABEL maintainer="Practica2-IA"
LABEL description="Búsqueda Informada y Local: A* y Simulated Annealing"
 
# Instalar tkinter y dependencias de sistema para la GUI
RUN apt-get update && apt-get install -y \
    python3-tk \
    tk-dev \
    libx11-6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*
 
# Directorio de trabajo
WORKDIR /app
 
# Copiar dependencias primero (capa cacheada)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# Copiar el código fuente
COPY . .
 
# Variable de entorno para display X11 (necesaria para Tkinter en Docker)
ENV DISPLAY=:0
 
# Comando por defecto: ejecutar los tests
# Para la GUI: docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix practica2 python main.py
CMD ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]