import os
from pymongo import MongoClient
from datetime import datetime
import glob

# Ruta completa a los archivos HTML
carpeta_html = "extraccion/dataset/paginas_descargadas/"

# Conexión a MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['bodies_scraping']
collection = db['bodies']

# Vaciar colección antes de insertar
def mongo_storage():
    collection.delete_many({})
    print("🧹 Colección 'page_bodies_retails' vaciada.")

    # Buscar todos los archivos .html
    archivos_html = glob.glob(os.path.join(carpeta_html, "*.html"))

    print("📁 Ruta completa a carpeta:", os.path.abspath(carpeta_html))
    print("🔎 Archivos encontrados:", glob.glob(os.path.join(carpeta_html, "*.html")))


    # Recorrer cada archivo y guardarlo en MongoDB
    for archivo in archivos_html:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()


        # Usar el nombre del archivo sin extensión como uid
        uid = os.path.splitext(os.path.basename(archivo))[0]

        documento = {
            "uid": uid,
            "text_raw": contenido,
            "text_clear": "-",
            "Fecha": datetime.now(),
            "Product object": {}
        }

        collection.insert_one(documento)
        print(f"✅ Insertado: {uid}")

    print("🎉 ¡Todos los archivos HTML han sido insertados en MongoDB!")