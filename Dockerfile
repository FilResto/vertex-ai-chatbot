# Usa Python 3.11 come base image
FROM python:3.11-slim

# Imposta la directory di lavoro
WORKDIR /app

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia i file requirements e installa le dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice dell'applicazione
COPY . .

# Crea un utente non-root per sicurezza
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Espone la porta (Cloud Run userà la variabile PORT)
EXPOSE 8080

# Comando per avviare l'applicazione
CMD ["python", "app.py"]
