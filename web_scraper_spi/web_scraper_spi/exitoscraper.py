from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import json

# Lista de URLs de Éxito (pon aquí todas tus URLs)
urlsaScrapear = [
    "https://www.exito.com/huevo-aa-rojo-30und-pet-744836/p",
"https://www.exito.com/huevo-rojo-aa-x-30-unidades-120829/p",
"https://www.exito.com/huevo-30und-omega-rojo-santa-anita-30-unidad-867527/p",
"https://www.exito.com/huevo-campesino-rojo-aa-huevos-oro-30-und-425721/p",
"https://www.exito.com/huevo-gallina-feliz-rojo-aa-x-32-und-cu-908166/p",
"https://www.exito.com/arroz-premium-1000-gr-130605/p",
"https://www.exito.com/arroz-roa-1-kilo-477377/p",
"https://www.exito.com/arroz-flor-huila-1000-gr-491125/p",
"https://www.exito.com/arroz-blanco-x-1000-gr-622811/p",
"https://www.exito.com/arroz-golondrina-2500-gr-3172659/p",
"https://www.exito.com/arroz-premium-alto-rendimiento-x-2500-gr-949864/p",
"https://www.exito.com/pan-bimbo-blanco-suave-esponjoso-730-gr-3202794/p",
"https://www.exito.com/pan-tajado-extralargo-476498/p",
"https://www.exito.com/pan-tajado-vital-semillas-500-gr-93997/p",
"https://www.exito.com/pan-de-sagu-sin-gluten-mauka-snacks-450-gramo-122829/p",
"https://www.exito.com/pan-pullman-extralargo-34470/p",
"https://www.exito.com/pan-tajado-mantequilla-exito-marca-propia-550-gr-3098991/p",
"https://www.exito.com/leche-deslactosada-sixpack-en-bolsa-x-11-litros-cu-957267/p",
"https://www.exito.com/leche-uht-entera-colanta-6000-ml-3069107/p",
"https://www.exito.com/leche-sabor-original-alqueria-1300-ml-3141762/p",
"https://www.exito.com/leche-entera-uht-paquete-exito-marca-propia-5400-ml-3101114/p",
"https://www.exito.com/tomate-chonto-unidad-937107/p",
"https://www.exito.com/tomate-chonto-frescampo-x-1000-gr-120787/p",
"https://www.exito.com/tomate-picado-oregano-y-albaca-376826/p",
"https://www.exito.com/banano-unidad-937109/p",
"https://www.exito.com/banano-deshidratado-103939955-mp/p",
"https://www.exito.com/banano-crocante-liofilizado-15g-101283837-mp/p",
"https://www.exito.com/cebolla-blanca-organico-x-500gr-84781/p",
"https://www.exito.com/cebolla-blanca-unidad-956928/p",
"https://www.exito.com/cebolla-roja-unidad-170530/p",
"https://www.exito.com/papa-criolla-a-granel-436803/p",
"https://www.exito.com/papa-criolla-ekono-1000g-824255/p",
"https://www.exito.com/papa-rusticas-mccain-500-gr-3026309/p",
"https://www.exito.com/queso-mozarella-486014/p",
"https://www.exito.com/queso-mozarella-x-25-tajadas-417-gr-268748/p",
"https://www.exito.com/queso-mozarella-tajado-superior-400-gr-3127727/p",
"https://www.exito.com/queso-semigraso-7cueros-enroll-11242/p",
"https://www.exito.com/queso-pera-relleno-con-bocadillo-de-guayaba-tripack-x-210-gr-539595/p",
"https://www.exito.com/queso-light-bloque-560384/p",
"https://www.exito.com/azucar-alta-pureza-2-kg-278588/p",
"https://www.exito.com/azucar-blanca-475197/p",
"https://www.exito.com/azucar-blanco-in-cauca-2500-gramo-15867/p",
"https://www.exito.com/azucar-mayaguez-492336/p",
"https://www.exito.com/azucar-organica-doypack-454-gr-282344/p"
]

def buscar_precio_jsonld(soup):
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and "offers" in data:
                offers = data["offers"]
                if isinstance(offers, list):
                    return offers[0].get("price")
                else:
                    return offers.get("price")
        except Exception:
            continue
    return None

def extraer_unidad(nombre, descripcion):
    patrones = [
        r'\(?\s*(\d+\.?\d*)\s*(und|kg|gr|g|ml|l|unidades?)\s*\)?',   # permite paréntesis y espacios
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

def parse_exito(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Nombre del producto
    nombre = None
    nombre_tag = soup.find('h1')
    if nombre_tag:
        nombre = nombre_tag.get_text(strip=True)

    # Precio (primero por HTML, si no por JSON-LD)
    precio = None
    precio_tag = soup.find('span', class_='vtex-product-price-1-x-sellingPriceValue')
    if precio_tag:
        precio = re.sub(r'[^\d,.]', '', precio_tag.get_text(strip=True)).replace(',', '.')
    if not precio:
        precio = buscar_precio_jsonld(soup)

    # Descripción
    descripcion = ""
    descripcion_tag = soup.find('div', class_='vtex-store-components-3-x-productDescriptionText')
    if descripcion_tag:
        descripcion = descripcion_tag.get_text(separator=" ", strip=True)
    else:
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            descripcion = meta_desc['content']

    # Unidad y precio por unidad (usando las funciones mejoradas)
    unidad = extraer_unidad(nombre, descripcion)
    precio_unidad = calcular_precio_por_unidad(precio, unidad)

    return nombre, precio, descripcion, unidad, precio_unidad

# --- Configuración de Selenium (headless) ---
options = Options()
options.add_argument("--headless=new")
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(options=options)

# --- Scraping loop ---
resultados = []
for url in urlsaScrapear:
    try:
        print(f"Procesando: {url}")
        driver.get(url)
        time.sleep(5)
        html = driver.page_source
        nombre, precio, descripcion, unidad, precio_unidad = parse_exito(html)
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
df.to_csv("datos_estructurados_exito.csv", index=False, encoding='utf-8')
print("¡Datos guardados en 'datos_estructurados_exito.csv'!")
