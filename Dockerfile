# Verwenden Sie ein offizielles Python-Image als Basis
FROM python:3.12-slim

# Setzen Sie das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopieren Sie die Anforderungen und installieren Sie sie
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Kopieren Sie den Rest des Anwendungscodes
COPY . .

# Erstellen Sie das Verzeichnis für die Datenbank, falls es nicht existiert
RUN mkdir -p /app/app/database

# Setzen Sie die Flask-Umgebungsvariablen
ENV FLASK_APP=app
ENV FLASK_ENV=production

# Exponieren Sie den Port, auf dem die App läuft
EXPOSE 5000

# Initialisieren Sie die Datenbank
RUN ["python", "init_db.py"]

# Starten Sie die Flask-Anwendung
CMD ["flask", "run", "--host=0.0.0.0"]
