#!/bin/sh

# Warte, bis die Datenbank verfügbar ist
while ! nc -z db 5432; do
  sleep 0.1
done

# Datenbankmigrationen durchführen
flask db init || true
flask db migrate || true
flask db upgrade

# Starten Sie die Anwendung
exec "$@"
