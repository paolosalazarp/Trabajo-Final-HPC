FROM python:3.11-slim

# Configurar variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Actualizar e instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Actualizar pip primero
RUN pip install --upgrade pip setuptools wheel

# Instalar dependencias directamente sin requirements.txt para evitar problemas de ruta
RUN pip install psutil==5.9.5 && \
    pip install pandas==2.1.4 && \
    pip install numpy==1.25.2 && \
    pip install requests==2.31.0 && \
    pip install beautifulsoup4==4.12.2 && \
    pip install selenium==4.15.2 && \
    pip install webdriver-manager==4.0.1 && \
    pip install tqdm==4.66.1 && \
    pip install redis==5.0.1

# Copiar el código
COPY . .

# Crear directorio para resultados
RUN mkdir -p /app/results

# Comando por defecto
CMD ["python", "scraper.py"]