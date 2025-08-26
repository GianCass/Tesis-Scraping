import os
from pymongo import MongoClient
from datetime import datetime
import glob

# ------------------------------
# Configuración
# ------------------------------
CARPETA_HTML = "extraccion/dataset/paginas_descargadas_vars/"

# URI y base de datos desde variables de entorno
MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = "raw_variables"

# Conexión a MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# ------------------------------
# Función para almacenar en MongoDB
# ------------------------------
def mongo_storage():
    # Crear nombre de colección con fecha (YYYY_MM_DD_HHMMSS)
    fecha_str = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    collection_name = f"raw_variables_{fecha_str}"
    collection = db[collection_name]

    print(f"📁 Carpeta buscada: {os.path.abspath(CARPETA_HTML)}")

    # Buscar todos los archivos .html recursivamente
    archivos_html = glob.glob(os.path.join(CARPETA_HTML, "**", "*.html"), recursive=True)
    print(f"🔎 Archivos encontrados: {len(archivos_html)}")
    print(f"🗂 Colección nueva creada: {collection_name}")

    # Insertar cada archivo
    for archivo in archivos_html:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()

            uid = os.path.splitext(os.path.basename(archivo))[0]

            documento = {
                "uid": uid,
                "text_raw": contenido,
                "Fecha": datetime.now(),
            }

            collection.insert_one(documento)
            print(f"✅ Insertado: {uid}")

        except Exception as e:
            print(f"❌ Error insertando {archivo}: {e}")

    print(f"🎉 ¡Todos los archivos HTML han sido insertados en MongoDB! Total: {collection.count_documents({})}")

# ------------------------------
# Ejecutar script
# ------------------------------
if __name__ == "__main__":
    mongo_storage()
