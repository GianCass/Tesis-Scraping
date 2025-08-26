# Python 3.9.x compatible con 3.9.5
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    # Chromium paths (SeleniumBase los detecta, pero explicitamos por si acaso)
    CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER=/usr/bin/chromedriver

# Dependencias del sistema (Chromium, Chromedriver, Xvfb, fuentes para render)
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium chromium-driver xvfb xauth \
    python3-tk python3-dev \
    fonts-liberation fonts-dejavu-core \
    libnss3 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libgbm1 libgtk-3-0 \
    libx11-6 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 \
    ca-certificates curl unzip gnupg \
    build-essential \
    python3-dev \
    linux-libc-dev \
    pkg-config \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia solo requirements primero para aprovechar layer caching
COPY requirements.txt /app/requirements.txt
# (si tienes dos listas)
COPY requirements2.txt /app/requirements2.txt

# Instala dependencias Python (Scrapy, SeleniumBase, etc.)
RUN pip install -U pip setuptools wheel \
    && pip install -r requirements.txt -r requirements2.txt

# # Si tienes el directorio FlareSolverr con requirements propios en el repo,
# # y quieres instalarlos dentro del contenedor del scraper (opcional):
# COPY FlareSolverr /FlareSolverr
# RUN pip install -r /FlareSolverr/requirements.txt

# Copia el resto del código del scraper (spiders, utils, etc.)
COPY . /app

# Script de entrada: envuelve cualquier comando con Xvfb si hace falta GUI
# (SeleniumBase en modo headless suele bastar, pero Xvfb evita edge cases)
RUN printf '#!/usr/bin/env bash\nset -e\nif command -v xvfb-run >/dev/null 2>&1 && command -v xauth >/dev/null 2>&1; then xvfb-run -a "$@"; else exec "$@"; fi\n' > /usr/local/bin/with-xvfb && chmod +x /usr/local/bin/with-xvfb

# Por defecto no fijamos el comando, Airflow lo pasará.
ENTRYPOINT ["with-xvfb"]

#CMD ["python3", "extraccion/main.py"]
