import os
from pymongo import MongoClient
from datetime import datetime

# ------------------------------
# Configuración MongoDB
# ------------------------------
# URI general sin especificar la base
MONGO_URI = "mongodb://root:example@localhost:27017/?authSource=admin"

DB_NAME = "bodies_scraping"
COLLECTION_NAME = "bodies"

# Conectar a MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# ------------------------------
# Carpeta con tus archivos
# ------------------------------
CARPETA = "./paginas_descargadas"  # ruta a tu carpeta con HTML

# Iterar archivos HTML
for filename in os.listdir(CARPETA):
    filepath = os.path.join(CARPETA, filename)
    
    if os.path.isfile(filepath) and filename.endswith(".html"):
        with open(filepath, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        uid = filename  # nombre del archivo como UID
        doc = {
            "uid": uid,
            "text_raw": contenido,
            "Fecha": datetime.now()
        }
        
        # Insertar uno por uno
        collection.insert_one(doc)
        print(f"Insertado: {uid}")

# Confirmar inserción
print("Total documentos en la colección:", collection.count_documents({}))
