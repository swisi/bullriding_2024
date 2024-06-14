#!/bin/sh

# Pfad zur Datenbankdatei
DB_DIR=/app/database
DB_FILE=$DB_DIR/site.db

# Erstellen Sie das Verzeichnis, falls es nicht existiert
mkdir -p $DB_DIR

# Überprüfen, ob die Datenbankdatei existiert
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
