#!/bin/sh

# Warten auf die Datenbank
sleep 5

# Überprüfen, ob die Datenbank existiert und initialisieren oder migrieren
if flask db current > /dev/null 2>&1; then
  echo "Datenbank existiert. Anwenden von Migrationen..."
  flask db migrate
  flask db upgrade
else
  echo "Datenbank existiert nicht. Initialisierung..."
  flask db init
  flask db migrate
  flask db upgrade
fi

# Starten Sie die Flask-Anwendung
exec "$@"
