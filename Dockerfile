# Usa Python 3
FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos
COPY . .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Ejecuta el bot
CMD ["python", "main.py"]
