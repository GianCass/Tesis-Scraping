from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import json

# URLs de Olimpica (agrega más URLs si lo deseas)
urlsaScrapear = [
   "https://www.olimpica.com/huevo-aa-rojo-pet-kikes-30un-7707304621100-1353948/p",
  "https://www.olimpica.com/huevo-aa-rojo-vinipel-30-un-7702420910015/p",
  "https://www.olimpica.com.co/huevo-santa-anita-aa-rojo-24un-7706772100582-973681/p",
  "https://www.olimpica.com/huevo-campesino-nutriavicola-rojo-x30un-7702349030375-1006331/p",
  "https://www.olimpica.com/arroz-diana-5-kg-7702511000045-566554/p",
  "https://www.olimpica.com/arroz-sabroson-5-kg-7707105805105-2000025/p",
  "https://www.olimpica.com/arroz-olimpica-10-kg-m-bult/p",
  "https://www.olimpica.com/arroz-donapepa-153-5kg-7702231300043-1393182/p",
  "https://www.olimpica.com/arroz-mi-arroz-3-kg-7707105814060-1635734/p",
  "https://www.olimpica.com/arroz-dona-rosa-paca-25-und-12-5-kg/p",
  "https://www.olimpica.com/pan-tajado-bimbo-integral-650-g-7705326073365--754200/p",
  "https://www.olimpica.com/pan-tajado-integral-centeno-malta-comapan-400g-7702432217928--5085884/p",
  "https://www.olimpica.com/pan-bimbo-vital-multicereal-500-g-7705326073907--811942/p",
  "https://www.olimpica.com/pan-sagu-mauka-450g/p",
  "https://www.olimpica.com/pan-integral-olimpica-molde-540-g-25060263--350168/p",
  "https://www.olimpica.com/pan-tajado-mama-ines-integral-440-g-7705326019264--691537/p",
  "https://www.olimpica.com/leche-uht-alpina-ent-cj-1-l/p",
  "https://www.olimpica.com/leche-uht-colanta-entera-1000ml-x6/p",
  "https://www.olimpica.com/leche-alqueria-original-1100ml-x-6un/p",
  "https://www.olimpica.com/leche-uht-olimpica/p",
  "https://www.olimpica.com/leche-uht-medalla-oro-entera-900ml-x6-7701008629332-2146935/p",
  "https://www.olimpica.com/tomate-pera-la-economica-1-kg-7701008112605-2569/p?skuId=2569",
  "https://www.olimpica.com/tomat-chonto-selecto-la-giralda-24045223-12848/p?skuId=12848",
  "https://www.olimpica.com/tomate-tamarillo-24030519-6572/p?skuId=6572",
  "https://www.olimpica.com/tomate-rio-grande-ciruelo/p?skuId=747",
  "https://www.olimpica.com/tomate-picados-hunts-411-g-27000380406--1104106/p",
  "https://www.olimpica.com/banano-bocadillo-7704862182463-4456/p?skuId=4456",
  "https://www.olimpica.com/banano-maduro/p?skuId=750",
  "https://www.olimpica.com/cebolla-cabezona-blanca/p?skuId=613",
  "https://www.olimpica.com/cebolla-frescocampo-cabezona-blanca-kosher-1kg-7709631567830-12180/p?skuId=12180",
  "https://www.olimpica.com/cebolla-blanca-selecta-la-giralda-24045186-12846/p?skuId=12846",
  "https://www.olimpica.com/papa-olimpica--pastusa-por-2-5-kg-7701008005280-724/p?skuId=724",
  "https://www.olimpica.com/papa-tradicional-mc-cain-1-kg-7707203350071-830476/p",
  "https://www.olimpica.com/papa-medalla-oro-francesa-1000-g-7701008629578-2142591/p",
  "https://www.olimpica.com/papa-mc-cain-facil-1-kg-7707203351184-1650663/p",
  "https://www.olimpica.com/qso-bco-colanta-500-g/p",
  "https://www.olimpica.com/quesito-alpina-fresco-blando-375g-7702001133628-2047338/p",
  "https://www.olimpica.com/qso-del--vecch-3-und-210-g/p",
  "https://www.olimpica.com/qso-medalla-oro-t-mozar-taj-250-g/p",
  "https://www.olimpica.com/alimento-violife-mozzarella-200g/p",
  "https://www.olimpica.com/azucar-riopaila-blanca-500-gr-7702127107022-798301/p",
  "https://www.olimpica.com/azucar-manuelita-1-kg/p",
  "https://www.olimpica.com/azucar-cauca-1-kg-7702059402028-26770/p",
  "https://www.olimpica.com/azucar-mayaguez-bca-2-5kg/p",
  "https://www.olimpica.com/azucar-blanca-olimpica-2-5-kg/p",
  "https://www.olimpica.com/azucar-providen-blanca--2-5-kg-7702104010307-73470/p"
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

def buscar_nombre(soup):
    # Primero intenta con h1
    nombre_tag = soup.find('h1')
    if nombre_tag:
        return nombre_tag.get_text(strip=True)
    # Luego con el título de la página
    title_tag = soup.find('title')
    if title_tag:
        return title_tag.get_text(strip=True)
    # Luego en meta 'og:title'
    meta_og = soup.find('meta', {'property': 'og:title'})
    if meta_og and meta_og.get('content'):
        return meta_og['content'].strip()
    return None

def buscar_precio(soup):
    # Busca span con $ y números
    for span in soup.find_all('span'):
        text = span.get_text(strip=True)
        if re.match(r'^\$[\d\.,]+$', text):
            return re.sub(r'[^\d,.]', '', text).replace(',', '')
    # Busca en JSON-LD
    precio_jsonld = buscar_precio_jsonld(soup)
    if precio_jsonld:
        return precio_jsonld
    # Busca en meta 'product:price:amount'
    meta_price = soup.find('meta', {'property': 'product:price:amount'})
    if meta_price and meta_price.get('content'):
        return meta_price['content'].strip()
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

def parse_olimpica(html):
    soup = BeautifulSoup(html, 'html.parser')

    nombre = buscar_nombre(soup)
    precio = buscar_precio(soup)
    if precio:
        try:
            precio = float(str(precio).replace(',', '').replace(' ', ''))
        except:
            precio = None

    descripcion_tag = soup.find('div', class_='product-description')
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

# --- Scraping loop ---
resultados = []
for url in urlsaScrapear:
    try:
        print(f"Procesando: {url}")
        driver.get(url)
        time.sleep(5)
        html = driver.page_source
        nombre, precio, descripcion, unidad, precio_unidad = parse_olimpica(html)
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
df.to_csv("datos_estructurados_olimpica.csv", index=False, encoding='utf-8')
print("¡Datos guardados en 'datos_estructurados_olimpica.csv'!")
