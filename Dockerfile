# Usa la imagen base de CUDA 12.2 para soporte de GPU
FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

# Configura el directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema
RUN apt-get update && \
    apt-get install -y python3.10 python3-pip cmake build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Configura XGBoost para usar CUDA
ENV XGBOOST_USE_CUDA=1

# Copia los archivos necesarios
COPY requirements.txt .
COPY src/ ./src/
COPY .env .

# Instala dependencias de Python
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt --no-cache-dir

# Comando por defecto
CMD ["python3", "./src/train_model.py"]del.py"]