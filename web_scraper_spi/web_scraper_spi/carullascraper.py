from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import json

# Lista de URLs de Carulla
urlsaScrapear = [
    "https://secure.carulla.com/huevo-aa-rojo-30und-pet-744836/p",
  "https://www.carulla.com/huevo-rojo-aa-x-30-unidades-120829/p",
  "https://www.carulla.com/huevo-aa-rojo-x-12-unidades-315269/p",
  "https://www.carulla.com/huevo-oro-de-12und-aa-rosado-huevos-oro-12-und-494306/p",
  "https://www.carulla.com/huevo-rojo-aa-15und-cryovac-napoles-15-und-315309/p",
  "https://www.carulla.com/gallina-feliz?srsltid=AfmBOopXDY7hGWpePqDjAe3yqae-1WGGTosM_pL5gwuq_NrgihKflkhb",
  "https://www.carulla.com/arroz-diana-5000-gr-498671/p",
  "https://www.carulla.com/arroz-roa-1-kilo-477377/p",
  "https://www.carulla.com/arroz-882120/p",
  "https://www.carulla.com/arroz-super-premium-arroz-sonora-premium-1000-gr-3147998/p",
  "https://www.carulla.com/arroz-golondrina-blanco-450-gr-3193795/p",
  "https://www.carulla.com/arroz-blanco-carulla-1000-gr-3064261/p",
  "https://www.carulla.com/arroz-parbolizado-x-1kg-624010/p",
  "https://www.carulla.com/pan-bimbo-pan-integral-1p-480g-flow-bim-480-gr-3188672/p",
  "https://www.carulla.com/pan-integral-centeno-malteado-comapan-400-gramo-3002682/p",
  "https://www.carulla.com/pan-tajado-vital-semillas-500-gr-93997/p",
  "https://www.carulla.com/pan-de-sagu-sin-gluten-mauka-snacks-450-gramo-122829/p",
  "https://www.carulla.com/pan-6-granos-integral-873956/p",
  "https://www.carulla.com/pan-tajado-blanco-carulla-600-gr-3098267/p",
  "https://www.carulla.com/pan-integral-extralargo-827180/p",
  "https://www.carulla.com/leche-entera-sixpack-en-bolsa-x-1100-ml-cu-211920/p",
  "https://www.carulla.com/leche-entera-en-bolsa-x-900-ml-627376/p",
  "https://www.carulla.com/leche-entera-uht-paquete-carulla-6600-ml-3119441/p",
  "https://www.carulla.com/leche-exito-marca-propia-en-caja-entera-900-ml-3189646/p",
  "https://www.carulla.com/tomate-chonto-unidad-sel-carul-919757/p",
  "https://www.carulla.com/tomate-chonto-frescampo-x-1000-gr-120787/p",
  "https://www.carulla.com/banano-unidad-937109/p",
  "https://www.carulla.com/cebolla-blanca-unidad-956928/p",
  "https://www.carulla.com/cebolla-blanca-organico-x-500gr-84781/p",
  "https://www.carulla.com/papa-pastusa-a-granel-x180gr-439761/p",
  "https://www.carulla.com/papa-rapi-trad-megapack-mccain-2000-gr-3026307/p",
  "https://www.carulla.com/queso-mozarella-light-x6-unds-pasco-240-gramo-981065/p",
  "https://www.carulla.com/queso-mozzarella-colanta-475057/p",
  "https://www.carulla.com/queso-mozarella-x-25-tajadas-417-gr-268748/p",
  "https://www.carulla.com/queso-mozarella-tajado-superior-400-gr-3127727/p",
  "https://www.carulla.com/queso-semigraso-7cueros-enroll-11242/p",
  "https://www.carulla.com/queso-pera-relleno-con-bocadillo-de-guayaba-tripack-x-210-gr-539595/p",
  "https://www.carulla.com/azucar-alta-pureza-2-kg-278588/p",
  "https://www.carulla.com/azucar-morena-1-kg-448916/p"
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

def parse_carulla(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Nombre
    nombre_tag = soup.find('h1')
    nombre = nombre_tag.get_text(strip=True) if nombre_tag else None

    # Precio
    precio_tag = soup.find('span', class_='vtex-product-price-1-x-sellingPriceValue')
    precio = None
    if precio_tag:
        precio = re.sub(r'[^\d,.]', '', precio_tag.get_text(strip=True)).replace(',', '.')
    if not precio:
        precio = buscar_precio_jsonld(soup)

    # Descripción
    descripcion_tag = soup.find('div', class_='vtex-store-components-3-x-productDescriptionText')
    descripcion = descripcion_tag.get_text(separator=" ", strip=True) if descripcion_tag else None
    if not descripcion:
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
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
        time.sleep(3)
        # --- Intentar cerrar/aceptar banner de cookies ---
        try:
            # El botón puede tener texto como "Aceptar", "Cerrar", etc.
            # Puedes inspeccionar el HTML para confirmar el selector si este no funciona
            # Ejemplo: botón con id "onetrust-accept-btn-handler" (ajusta si cambia)
            accept_btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")
            accept_btn.click()
            print("Cookies aceptadas.")
            time.sleep(2)
        except (NoSuchElementException, ElementNotInteractableException):
            pass  # No apareció el banner o ya estaba aceptado

        time.sleep(3)  # Da tiempo extra para que cargue todo el contenido

        html = driver.page_source
        nombre, precio, descripcion, unidad, precio_unidad = parse_carulla(html)
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
df.to_csv("datos_estructurados_carulla.csv", index=False, encoding='utf-8')
print("¡Datos guardados en 'datos_estructurados_carulla.csv'!")
