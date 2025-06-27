import pandas as pd
import subprocess
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from captcha import save_cookies

archivo_excel = os.path.join('extraccion', 'dataset', 'edaSisPricingInt.xlsx')


def extraer_urls_excel(archivo_excel, columna_url='URL', columna_tipo='Tipo Pagina', columna_captcha='Captcha?', hoja=0):
    carpeta_destino = os.path.join('dataset', 'datos_extraidos')
    os.makedirs(carpeta_destino, exist_ok=True)

    # Rutas de archivos de salida
    ruta_estaticas = os.path.join(carpeta_destino, 'estaticas.txt')
    ruta_dinamicas = os.path.join(carpeta_destino, 'dinamicas.txt')

    # Leer el archivo Excel
    ruta_absoluta = os.path.abspath(archivo_excel)
    print(f"Buscando archivo en: {ruta_absoluta}")
    print(f"¿Existe el archivo? {os.path.exists(archivo_excel)}")

    if not os.path.exists(archivo_excel):
        print("ERROR: El archivo Excel no existe en la ruta especificada")
        return 0, 0

    df = pd.read_excel(ruta_absoluta, sheet_name=hoja)

    # Filtrar filas donde URL y Tipo Pagina no sean nulos
    df_limpio = df.dropna(subset=[columna_url, columna_tipo])

    # Rellenar NaNs en Captcha con cadena vacía
    df_limpio[columna_captcha] = df_limpio[columna_captcha].fillna("")

    # Guardar URLs estáticas con captcha
    with open(ruta_estaticas, 'w', encoding='utf-8') as archivo:
        for _, row in df_limpio[df_limpio[columna_tipo] == 'E'].iterrows():
            archivo.write(f"{row[columna_url]}, {row[columna_captcha]}\n")

    # Guardar URLs dinámicas con captcha
    with open(ruta_dinamicas, 'w', encoding='utf-8') as archivo:
        for _, row in df_limpio[df_limpio[columna_tipo] == 'D'].iterrows():
            archivo.write(f"{row[columna_url]}, {row[columna_captcha]}\n")

    print(f"URLs estáticas guardadas en: {ruta_estaticas} ({len(df_limpio[df_limpio[columna_tipo] == 'E'])} URLs)")
    print(f"URLs dinámicas guardadas en: {ruta_dinamicas} ({len(df_limpio[df_limpio[columna_tipo] == 'D'])} URLs)")

    #usar una vez al inicio si no hay archivos en cookies de captcha
    #urls = save_cookies.load_urls_from_txts()
    #save_cookies.save_cookies_for_multiple_urls(urls)

    return len(df_limpio[df_limpio[columna_tipo] == 'E']), len(df_limpio[df_limpio[columna_tipo] == 'D'])


def descargar_paginas_scrapy_y_selenium():
    try:
        project_dir = os.path.join(os.getcwd(), 'web_scraper_spi')
        subprocess.run(["scrapy", "crawl", "page_downloader"], cwd=project_dir, check=True)
        print("Descarga completada con Scrapy!")
    except Exception as e:
        print(f"Error al ejecutar Scrapy: {e}")



def extraccion_controller():
    try:
        num_estaticas, num_dinamicas = extraer_urls_excel(archivo_excel)

        if num_estaticas == 0 and num_dinamicas == 0:
            print("No se procesaron URLs. Verificar archivo Excel.")
            return

        descargar_paginas_scrapy_y_selenium()
        print(f"Proceso completado: {num_estaticas} URLs estáticas y {num_dinamicas} URLs dinámicas procesadas")
    except Exception as e:
        print(f"Error en el proceso de extracción: {e}")


def verificar_tipos_pagina(archivo_excel, columna_tipo='Tipo Pagina', hoja=0):
    try:
        ruta_absoluta = os.path.abspath(archivo_excel)
        df = pd.read_excel(ruta_absoluta, sheet_name=hoja)
        tipos_unicos = df[columna_tipo].value_counts()
        print("Tipos de página encontrados:")
        print(tipos_unicos)
        return tipos_unicos
    except Exception as e:
        print(f"Error al verificar tipos de página: {e}")
        return None
