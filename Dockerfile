FROM apache/airflow:2.8.2-python3.9

USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-setuptools \
    python3-wheel \
    libhdf5-dev \
    libyaml-dev \
    libhdf5-serial-dev \
    libhdf5-103 \
    pkg-config \
    zlib1g-dev \
    libssl-dev \
    libbz2-dev \
    liblzma-dev \
    && rm -rf /var/lib/apt/lists/*

# Variables de entorno para que h5py detecte HDF5
ENV HDF5_DIR=/usr/lib/x86_64-linux-gnu/hdf5/serial
ENV CC=gcc

USER airflow

# Actualizar herramientas de compilación
RUN pip install --upgrade pip setuptools wheel cython
RUN pip install --no-cache-dir "h5py==3.10.0"

# Instalar h5py primero (para aislar el error) y luego el resto
# COPY requirements.txt /requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.8.2/constraints-3.9.txt"

COPY requirements2.txt .
RUN pip install --no-cache-dir -r requirements2.txt \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.8.2/constraints-3.9.txt"
