from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import json

# URLs de Unimarc
urlsaScrapear = [
   "https://www.unimarc.cl/product/cafe-nescafe-tradicion-lata-170-g",
  "https://www.unimarc.cl/product/cafe-molido-italiano-waitrose-227-gr",
  "https://www.unimarc.cl/product/marley-coffee-buffalo-s-organic-227-gr",
  "https://www.unimarc.cl/product/cafe-haiti-molido-mezcla-super-moka-3-250-g",
  "https://www.unimarc.cl/product/cafe-molido-mezcla-excels-250-gr",
  "https://www.unimarc.cl/product/papas-malla-2-kg",
  "https://www.unimarc.cl/product/papa-granel-kg",
  "https://www.unimarc.cl/product/papas-huertos-del-ranco-malla-1-3kg",
  "https://www.unimarc.cl/product/pan-molde-integral-xl-castano-700gr",
  "https://www.unimarc.cl/product/pan-molde-blanco-grande-ideal-750-g",
  "https://www.unimarc.cl/product/pan-molde-integral-cena-xl-750g",
  "https://www.unimarc.cl/product/pan-molde-integral-stuttgart-fuchs-650-g",
  "https://www.unimarc.cl/product/pan-de-molde-blanco-xl-amada-masa-750-gr",
  "https://www.unimarc.cl/product/beb-coca-cola-1-5-l-no-retor-3",
  "https://www.unimarc.cl/product/pepsi-desechable-15-l",
  "https://www.unimarc.cl/product/ginger-ale-canada-dry-desechable-1-5-lt",
  "https://www.unimarc.cl/product/kem-pina-desechable-1-5-lt",
  "https://www.unimarc.cl/product/bebida-piri-cola-zero-2-l",
  "https://www.unimarc.cl/product/tomate-1-kg-5-u-aprox",
  "https://www.unimarc.cl/product/tomate-malla-1-kg",
  "https://www.unimarc.cl/product/tomate-regy-agricola-ramos-300-gr",
  "https://www.unimarc.cl/product/tomate-snacky-pote-250-gr",
  "https://www.unimarc.cl/product/huevo-grande-color-nuestra-cocina-12-un",
  "https://www.unimarc.cl/product/huevos-yemita-grande-blanco-12-u",
  "https://www.unimarc.cl/product/huevo-extra-color-santa-marta-20-un",
  "https://www.unimarc.cl/product/huevo-grande-color-santa-elvira-12-un",
  "https://www.unimarc.cl/product/huevo-grande-color-la-granja-12-un",
  "https://www.unimarc.cl/product/pollo-entero-c-menudencia-ariztia-1-8-a-2-2kg",
  "https://www.unimarc.cl/product/pollo-entero-super-pollo-con-menudencias-3-kg",
  "https://www.unimarc.cl/product/leche-entera-natural-colun-sin-tapa-1-l-2",
  "https://www.unimarc.cl/product/leche-entera-natural-soprole-con-tapa-1-l-2",
  "https://www.unimarc.cl/product/leche-entera-natural-surlat-1-lt",
  "https://www.unimarc.cl/product/leche-entera-sin-lactosa-loncoleche-con-tapa-1-l",
  "https://www.unimarc.cl/product/manzana-royal-gala-kg",
  "https://www.unimarc.cl/product/carozzi-spaghetti-n-5-400-g",
  "https://www.unimarc.cl/product/spaghetti-5-integral-1881-500-gr",
  "https://www.unimarc.cl/product/talliani-spaghetti-n-5-al-huevo-400-g",
  "https://www.unimarc.cl/product/lucchetti-spaghetti-n-5-400-g",
  "https://www.unimarc.cl/product/spaghetti-n-5-merkat-400-gr"
]

def buscar_precio_jsonld(soup):
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            # Unimarc tiene 'offers' o 'price'
            if isinstance(data, dict):
                if "offers" in data:
                    offers = data["offers"]
                    if isinstance(offers, list):
                        return offers[0].get("price")
                    else:
                        return offers.get("price")
                elif "price" in data:
                    return data.get("price")
        except Exception:
            continue
    return None

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

def parse_unimarc(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Nombre
    nombre_tag = soup.find('h1')
    nombre = nombre_tag.get_text(strip=True) if nombre_tag else None

    # Precio
    precio = None
    precio_tag = soup.find('span', class_='ui-pdp-price__second-val')
    if precio_tag:
        # Ejemplo: "$2.590"
        precio = re.sub(r'[^\d,.]', '', precio_tag.get_text(strip=True)).replace('.', '')
    if not precio:
        precio = buscar_precio_jsonld(soup)
    if precio:
        try:
            precio = float(str(precio).replace(',', '').replace(' ', ''))
        except:
            precio = None

    # Descripción (Unimarc la tiene en un div de clase 'product-info__description' o en meta)
    descripcion = ""
    descripcion_tag = soup.find('div', class_='product-info__description')
    if descripcion_tag:
        descripcion = descripcion_tag.get_text(separator=" ", strip=True)
    else:
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
        html = driver.page_source
        nombre, precio, descripcion, unidad, precio_unidad = parse_unimarc(html)
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
df.to_csv("datos_estructurados_unimarc.csv", index=False, encoding='utf-8')
print("¡Datos guardados en 'datos_estructurados_unimarc.csv'!")
