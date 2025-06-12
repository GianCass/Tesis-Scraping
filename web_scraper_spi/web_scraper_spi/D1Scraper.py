from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# URLs de Tiendas D1 (agrega más si quieres)
urlsaScrapear = [
    "https://domicilios.tiendasd1.com/p/huevos-tipo-l-kikes-30-und-12006002",
    
]

def extraer_unidad(nombre, descripcion):
    patrones = [
        r'\(?\s*(\d+\.?\d*)\s*(und|kg|gr|g|ml|l|unidades?)\s*\)?',
        r'x\s*(\d+\.?\d*)\s*(und|kg|gr|g|ml|l|unidades?)'
    ]
    for texto in [nombre, descripcion]:
        if texto:
            for patron in patrones:
                match = re.search(patron, texto, re.IGNORECASE)
                if match:
                    cantidad = match.group(1).replace(',', '.')
                    tipo = match.group(2).lower()
                    return f"{cantidad} {tipo}"
    return None

def calcular_precio_por_unidad(precio, unidad):
    if not precio or not unidad:
        return None
    try:
        precio = float(str(precio).replace(',', '').replace(' ', ''))
    except Exception:
        return None
    match = re.search(r'(\d+\.?\d*)\s?(und|kg|gr|g|ml|l|unidades?)', str(unidad), re.IGNORECASE)
    if match:
        cantidad = float(match.group(1).replace(',', '.'))
        tipo = match.group(2).lower()
        if cantidad != 0:
            precio_unidad = precio / cantidad
            return f"{precio_unidad:.2f}/{tipo}"
    return None

def parse_tiendasd1(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Nombre (está en un <h1>)
    nombre_tag = soup.find('h1')
    nombre = nombre_tag.get_text(strip=True) if nombre_tag else None

    # Precio (en span con clase 'vtex-product-price-1-x-sellingPriceValue')
    precio_tag = soup.find('span', class_='vtex-product-price-1-x-sellingPriceValue')
    precio = None
    if precio_tag:
        precio = re.sub(r'[^\d,.]', '', precio_tag.get_text(strip=True)).replace(',', '').replace('.', '')
    if precio:
        try:
            precio = float(precio)
        except:
            precio = None

    # Descripción
    descripcion_tag = soup.find('div', class_='vtex-store-components-3-x-productDescriptionText')
    descripcion = descripcion_tag.get_text(separator=" ", strip=True) if descripcion_tag else None
    if not descripcion:
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            descripcion = meta_desc['content']

    unidad = extraer_unidad(nombre, descripcion)
    precio_unidad = calcular_precio_por_unidad(precio, unidad)

    return nombre, precio, descripcion, unidad, precio_unidad

# --- Configuración de Selenium ---
options = Options()
options.add_argument("--headless=new")
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(options=options)

resultados = []
for url in urlsaScrapear:
    try:
        print(f"Procesando: {url}")
        driver.get(url)
        time.sleep(5)

        with open("tiendasd1_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("HTML guardado como tiendasd1_debug.html")


        html = driver.page_source
        nombre, precio, descripcion, unidad, precio_unidad = parse_tiendasd1(html)
        resultados.append({
            "url": url,
            "nombre": nombre,
            "precio": precio,
            "descripcion": descripcion,
            "unidad": unidad,
            "precio_unidad": precio_unidad
        })
    except Exception as e:
        print(f"Error en {url}: {e}")

driver.quit()
df = pd.DataFrame(resultados)
df.to_csv("datos_estructurados_tiendasd1.csv", index=False, encoding='utf-8')
print("¡Datos guardados en 'datos_estructurados_tiendasd1.csv'!")
