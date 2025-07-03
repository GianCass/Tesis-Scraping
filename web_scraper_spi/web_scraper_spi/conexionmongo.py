import pandas as pd
from pymongo import MongoClient
import glob

archivos_csv = glob.glob("datos_estructurados_*.csv")

client = MongoClient('mongodb://localhost:27017/')
db = client['bodies_scraping_Python']
collection = db['page_bodies']

collection.delete_many({})
print("Colección 'page_bodies' vaciada.")

for archivo in archivos_csv:
    print(f"Procesando {archivo}")
    df = pd.read_csv(archivo)
    df['fuente'] = archivo.replace('datos_estructurados_', '').replace('.csv', '') 
    data_dict = df.to_dict("records")
    if data_dict:
        collection.insert_many(data_dict)

print("¡Todos los datos actuales han sido insertados en MongoDB!")
