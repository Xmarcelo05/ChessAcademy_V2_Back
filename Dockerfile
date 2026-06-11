# Usar una versión oficial y ligera de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de requerimientos primero (para optimizar la caché)
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el resto de tu código a la carpeta /app del contenedor
COPY . .

# Exponer el puerto que usa FastAPI
EXPOSE 8000

# El comando que ejecutará AWS para encender tu servidor
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]