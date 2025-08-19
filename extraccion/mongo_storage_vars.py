import os
from pymongo import MongoClient
from datetime import datetime
import glob

# Ruta completa a los archivos HTML
carpeta_txt = "extraccion/dataset/paginas_descargadas_vars/"

# Conexión a MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/bodies_scraping")
client = MongoClient(MONGO_URI)
db_name = MONGO_URI.rsplit('/', 1)[-1] or "bodies_scraping"
db = client[db_name]
collection = db['vars']

# Vaciar colección antes de insertar
def mongo_storage():
    collection.delete_many({})
    print("🧹 Colección 'vars de bodies_scraping' vaciada.")

    # Buscar todos los archivos .html
    archivos_txt = glob.glob(os.path.join(carpeta_txt, "*.txt"))

    print("📁 Ruta completa a carpeta:", os.path.abspath(carpeta_txt))
    print("🔎 Archivos encontrados:", glob.glob(os.path.join(carpeta_txt, "*.txt")))


    # Recorrer cada archivo y guardarlo en MongoDB
    for archivo in archivos_txt:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()


        # Usar el nombre del archivo sin extensión como uid
        uid = os.path.splitext(os.path.basename(archivo))[0]

        documento = {
            "uid": uid,
            "text_raw": contenido,
            "text_clear": "-",
            "Fecha": datetime.now(),
        }

        collection.insert_one(documento)
        print(f"✅ Insertado: {uid}")

    print("🎉 ¡Todos los archivos HTML han sido insertados en MongoDB!")