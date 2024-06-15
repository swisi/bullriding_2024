import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

# Verzeichnis-Erstellung
basedir = os.path.abspath(os.path.dirname(__file__))
database_dir = os.path.join(basedir, 'database')
if not os.path.exists(database_dir):
    os.makedirs(database_dir)

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from . import models  # Importiere deine Modelle hier

    return app

app = create_app()
