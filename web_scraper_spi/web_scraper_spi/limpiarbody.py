import os
import re
import json
from bs4 import BeautifulSoup

# Configuración de rutas
CARPETA_HTMLS = os.path.join("extraccion", "dataset", "paginas_descargadas")
SALIDA_JSONL = os.path.join("extraccion", "dataset", "productos_extraidos.jsonl")

def limpiar_html(html):
    """Limpia el HTML eliminando elementos no deseados."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Elementos a eliminar (ampliado)
    TAGS_A_ELIMINAR = [
        "script", "style", "svg", "noscript", "footer", "header",
        "iframe", "nav", "form", "img", "button", "label", "select",
        "input", "textarea", "meta", "link"
    ]
    
    for tag in soup(TAGS_A_ELIMINAR):
        tag.decompose()
        
    # Eliminar elementos con clases específicas que contienen texto genérico
    CLASES_A_ELIMINAR = [
        "legal", "disclaimer", "footer", "header", "notification",
        "banner", "advertisement", "cookie"
    ]
    
    for clase in CLASES_A_ELIMINAR:
        for tag in soup.find_all(class_=re.compile(clase, re.I)):
            tag.decompose()
            
    # Eliminar atributos innecesarios
    for tag in soup.find_all():
        for attr in ["style", "class", "id", "onclick"]:
            if attr in tag.attrs:
                del tag[attr]
                
    return soup

def extraer_datos_directos(soup, archivo_origen):
    """Extrae datos directamente de elementos específicos del producto."""
    datos = {
        "archivo_origen": archivo_origen,
        "nombre": None,
        "descripcion": None,
        "precio_total": None,
        "precio_unidad": None
    }
    
    # Extraer nombre del producto
    nombre_tag = soup.find('h1') or soup.find('h2') or soup.find('h3')
    if nombre_tag:
        datos["nombre"] = nombre_tag.get_text(strip=True)
    
    # Extraer descripción - buscamos en párrafos largos
    desc_tags = soup.find_all('p')
    for tag in desc_tags:
        texto = tag.get_text(strip=True)
        if len(texto) > 50:  # Consideramos solo párrafos largos
            datos["descripcion"] = texto
            break
    
    # Extraer precios - buscamos patrones específicos
    def extraer_precio(texto):
        match = re.search(r'(?:\$|USD)\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)', texto)
        if match:
            return float(match.group(1).replace('.', '').replace(',', '.'))
        return None
    
    # Buscar precio total
    precio_tags = soup.find_all(string=re.compile(r'\$|USD|precio', re.I))
    for texto in precio_tags:
        precio = extraer_precio(texto)
        if precio:
            datos["precio_total"] = precio
            break
    
    # Buscar precio por unidad
    unidad_tags = soup.find_all(string=re.compile(r'\d+\s*(?:g|ml|kg|l)\b', re.I))
    for texto in unidad_tags:
        match = re.search(r'(\d+)\s*(g|ml|kg|l)', texto, re.I)
        if match:
            datos["precio_unidad"] = {
                "valor": extraer_precio(texto.parent.get_text()) if texto.parent else None,
                "unidad": match.group(2).lower()
            }
            break
    
    return datos

def procesar_archivos():
    """Procesa todos los archivos HTML en la carpeta."""
    resultados = []
    
    if not os.path.exists(CARPETA_HTMLS):
        raise FileNotFoundError(f"No se encontró la carpeta {CARPETA_HTMLS}")
    
    for archivo in os.listdir(CARPETA_HTMLS):
        if archivo.endswith(".html"):
            ruta = os.path.join(CARPETA_HTMLS, archivo)
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    html = f.read()
                
                soup = limpiar_html(html)
                datos = extraer_datos_directos(soup, archivo)
                
                resultados.append(datos)
                
                with open(SALIDA_JSONL, "a", encoding="utf-8") as out:
                    out.write(json.dumps(datos, ensure_ascii=False) + "\n")
                    
                print(f"Procesado: {archivo}")
                
            except Exception as e:
                print(f"Error procesando {archivo}: {str(e)}")
    
    print(f"\nProceso completado. Archivos procesados: {len(resultados)}")
    print(f"Resultados guardados en: {SALIDA_JSONL}")
    return resultados

if __name__ == "__main__":
    procesar_archivos()