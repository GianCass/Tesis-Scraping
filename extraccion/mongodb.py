from pymongo import MongoClient
try:
    client = MongoClient('localhost', 27017)

    database = client['bodies_scraping_Python']
    collection = database['page_bodies']



    
except Exception as ex:
    print("error durante la conexión a MongoDB:", ex)
finally:
    print("Conexion finalizada a MongoDB")