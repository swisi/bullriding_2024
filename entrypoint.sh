#!/bin/sh

# Pfad zur Datenbankdatei
DB_FILE=/app/app/database/site.db

if [ ! -f "$DB_FILE" ]; then
  echo "Datenbankdatei nicht gefunden. Erstelle eine neue Datenbank..."
  flask db init
  flask db migrate
  flask db upgrade
else
  echo "Datenbankdatei gefunden. Führe ein Upgrade durch..."
  flask db upgrade
fi

# Starten Sie die Anwendung
exec "$@"
