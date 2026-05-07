# Imagen base
FROM python:3.10-slim

# Configurar el directorio de trabajo dentro del contenedor
WORKDIR /app

# Evitar que Python genere archivos .pyc y permitir logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar las librerías de Python (requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar todo el código de la aplicación al contenedor
COPY . .

# 7. Exponer el puerto donde correrá FastAPI
EXPOSE 8000

# 8. Arrancar la aplicación con Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]