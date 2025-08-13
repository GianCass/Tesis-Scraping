import extraccion_urls as extract
import mongo_storage as mongo

def iniciar_proceso():
    extract.extraccion_controller()
    mongo.mongo_storage()

if __name__ == "__main__":
    iniciar_proceso()



