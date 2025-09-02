import subprocess
import pandas as pd
from pathlib import Path
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# archivo excel variables
archivo_excel = os.path.join('extraccion', 'dataset', 'edaSisPricingInt_variables.xlsx')


def extraccion_eda(hoja=0):
    carpeta_destino = os.path.join('dataset', 'datos_extraidos_variables')
    os.makedirs(carpeta_destino, exist_ok=True)

    # Usar carpeta existente 'dataset'
    ruta_estaticas = os.path.join(carpeta_destino, 'estaticas.txt')
    ruta_dinamicas = os.path.join(carpeta_destino, 'dinamicas.txt')

    ruta_absoluta = os.path.abspath(archivo_excel)

    if not os.path.exists(archivo_excel):
        print("ERROR: El archivo Excel no existe en la ruta especificada")
        return 0, 0

    df = pd.read_excel(ruta_absoluta, sheet_name=hoja)

    if 'Link' not in df.columns or 'Formato' not in df.columns:
        print("❌ Faltan columnas necesarias ('Link', 'Formato')")
        return

    df_limpio = df.dropna(subset=["Link", "Formato"])

    # Guardar URLs estáticas con captcha
    with open(ruta_estaticas, 'w', encoding='utf-8') as archivo:
        for _, row in df_limpio[df_limpio["Formato"] == 'E'].iterrows():
            archivo.write(f"{row['Link']}\n")

    # Guardar URLs dinámicas con captcha
    with open(ruta_dinamicas, 'w', encoding='utf-8') as archivo:
        for _, row in df_limpio[df_limpio["Formato"] == 'D'].iterrows():
            archivo.write(f"{row['Link']}\n")

    print(f"URLs estáticas guardadas en: {ruta_estaticas} ({len(df_limpio[df_limpio['Formato'] == 'E'])} URLs)")
    print(f"URLs dinámicas guardadas en: {ruta_dinamicas} ({len(df_limpio[df_limpio['Formato'] == 'D'])} URLs)")

    return len(df_limpio[df_limpio["Formato"] == 'E']), len(df_limpio[df_limpio["Formato"] == 'D'])


def descargar_paginas_scrapy_y_selenium():
    try:
        project_dir = os.path.join(os.getcwd(), 'web_scraper_spi')
        subprocess.run(["scrapy", "crawl", "page_downloader_variables"], cwd=project_dir, check=True)
    except Exception as e:
        print(f"Error al ejecutar Scrapy Variables: {e}")


def extraccion_controller():
    try:
        num_estaticas, num_dinamicas = extraccion_eda(hoja=0)

        if num_estaticas == 0 and num_dinamicas == 0:
            print("No se procesaron URLs Variables. Verificar archivo Excel.")
            return

        descargar_paginas_scrapy_y_selenium()
    except Exception as e:
        print(f"Error en el proceso de extracción: {e}")
