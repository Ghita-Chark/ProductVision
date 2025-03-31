from sqlalchemy import create_engine

class DatabaseConnector:
    """Classe pour gérer la connexion à SQL Server"""

    def __init__(self):
        """Initialisation avec des paramètres de connexion intégrés"""
        self.host = "127.0.0.1"      # Adresse du serveur MySQL
        self.database = "Carrefour_db"  # Nom de la base MySQL
        self.username = "root"   # Nom d'utilisateur
        self.password = "Mysql"     # Mot de passe
        self.port = 3306             # Port MySQL (3306 par défaut)
        self.engine = None

    def connect(self):
        """Créer et retourner une connexion SQLAlchemy"""
        try:
            self.engine = create_engine(
                f"mysql+mysqlconnector://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
            )
            print("Connexion à SQL Server réussie !")
            return self.engine
        except Exception as e:
            print(f"Erreur de connexion à SQL Server : {e}")
            return None

    def get_engine(self):
        """Retourner l'engine SQLAlchemy pour l'utiliser ailleurs"""
        if self.engine is None:
            self.connect()
        return self.engine

if __name__ == "__main__":
    db_connector = DatabaseConnector()
    engine = db_connector.connect()

    
