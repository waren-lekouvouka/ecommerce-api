# database.py
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Charge le fichier .env lors de l'exécution locale.
# Sur le serveur cloud, MONGODB_URL est défini directement comme variable d'environnement.
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")

if not MONGODB_URL:
    raise ValueError(
        "La variable d'environnement MONGODB_URL n'est pas définie. "
        "Créez un fichier .env localement ou définissez la variable sur votre serveur."
    )

# Crée une connexion client partagée par toute l'application.
# Motor est async — il ne bloque pas en attendant la réponse de MongoDB.
client = AsyncIOMotorClient(MONGODB_URL)

# Sélectionne la base de données et la collection.
# Ces noms doivent correspondre à ce que vous avez créé dans Atlas.
db                  = client["ecommerce"]
products_collection = db["products"]

