import extraccion_urls as extract
import extraccion_urls_variables as extract_vars
import mongo_storage as mongo
import mongo_storage_vars as mongo_vars

def iniciar_proceso():
    print("👉 Iniciando extracción de productos…")
    extract.extraccion_controller()
    # mongo.mongo_storage()

    print("👉 Iniciando extracción de variables…")
    extract_vars.extraccion_controller()
    # mongo_vars.mongo_storage()

    print("\n✅ Proceso completo.\n")


if __name__ == "__main__":
    iniciar_proceso()



