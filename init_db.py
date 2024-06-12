import os
from app import create_app, db
from app.models import User, Participant

def init_db():
    app = create_app()
    with app.app_context():
        # Überprüfen und Erstellen des Verzeichnisses für die Datenbank
        db_dir = os.path.join(app.root_path, 'database')
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # Geben Sie den Pfad zur Datenbankdatei aus
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Initialisieren der Datenbank
        db.create_all()
        print("Database initialized!")

if __name__ == "__main__":
    init_db()
