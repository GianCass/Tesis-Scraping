import extraccion_urls as extract
import extraccion_urls_variables as extract_vars
import mongo_storage as mongo
import mongo_storage_vars as mongo_vars

def iniciar_proceso():
    # extract.extraccion_controller()
    # mongo.mongo_storage()
    extract_vars.extraccion_controller()
    mongo_vars.mongo_storage()


if __name__ == "__main__":
    iniciar_proceso()



