from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import json

urlsaScrapear = [
    "https://www.makro.plazavea.com.pe/arroz-superior-faraon-rojo-bolsa-10kg/p",
    "https://www.makro.plazavea.com.pe/arroz-reserva-extra-anejado-campero-bolsa-5kg/p",
    "https://www.makro.plazavea.com.pe/arroz-superior-nir-tazon-norteno-saco-49kg/p",
    "https://www.makro.plazavea.com.pe/arroz-naranja-gran-arroz-pacasmayo-saco-49kg/p",
    "https://www.makro.plazavea.com.pe/arroz-superior-vallenorte-bolsa-5kg/p",
    "https://www.makro.plazavea.com.pe/pollo-entero-perdix-sin-menudencia-congelado-bolsa-1-5kg/p",
    "https://www.makro.plazavea.com.pe/pollo-entero-sin-menudencia-frangosul-congelado-bolsa-1-3kg/p",
    "https://www.makro.plazavea.com.pe/pollo-sin-menudencia-a-granel-san-fernando-xkg/p",
    "https://www.makro.plazavea.com.pe/pollo-avinka-x-kg/p",
    "https://www.makro.plazavea.com.pe/cafe-tostado-y-molido-kaphiy-500g/p",
    "https://www.makro.plazavea.com.pe/cafe-instantaneo-altomayo-armonico-doypack-150g/p",
    "https://www.makro.plazavea.com.pe/cafe-instantaneo-colcafe-clasico-frasco-170g/p",
    "https://www.makro.plazavea.com.pe/cafe-instantaneo-cafetal-doypack-150g/p",
    "https://www.makro.plazavea.com.pe/cafe-instantaneo-nescafe-tradicion-lata-500g/p",
    "https://www.makro.plazavea.com.pe/aceite-de-soya-aro-bidon-3l/p",
    "https://www.makro.plazavea.com.pe/aceite-vegetal-beltran-botella-900ml/p",
    "https://www.makro.plazavea.com.pe/aceite-de-oliva-el-olivar-puro-botella-1l/p",
    "https://www.makro.plazavea.com.pe/aceite-vegetal-deleite-premium-bidon-5l/p",
    "https://www.makro.plazavea.com.pe/aceite-vegetal-primor-clasico-botella-900ml/p",
    "https://www.makro.plazavea.com.pe/leche-gloria-uht-fresca-ninos-1-a-5-anos-caja-1l/p",
    "https://www.makro.plazavea.com.pe/leche-sin-lactosa-vigor-bolsa-800ml/p",
    "https://www.makro.plazavea.com.pe/leche-entera-aro-caja-1l/p",
    "https://www.makro.plazavea.com.pe/leche-fresca-laive-light-bolsa-900ml/p",
    "https://www.makro.plazavea.com.pe/leche-fresca-danlac-botella-900ml/p",
    "https://www.makro.plazavea.com.pe/huevo-rosado-con-dha-aro-paquete-30un/p",
    "https://www.makro.plazavea.com.pe/azucar-rubia-aro-bolsa-5kg/p",
    "https://www.makro.plazavea.com.pe/azucar-rubia-cartavio-bolsa-5kg/p",
    "https://www.makro.plazavea.com.pe/azucar-rubia-dulfina-bolsa-1-kg/p",
    "https://www.makro.plazavea.com.pe/azucar-blanca-mk-bolsa-1kg/p",
    "https://www.makro.plazavea.com.pe/azucar-rubia-san-jacinto-25-kg/p",
    "https://www.makro.plazavea.com.pe/pan-molde-integral-aro-bolsa-600g/p",
    "https://www.makro.plazavea.com.pe/pan-de-molde-integral-union-bolsa-495g/p",
    "https://www.makro.plazavea.com.pe/pan-de-molde-integral-pyc-mediano-bolsa-500g/p",
    "https://www.makro.plazavea.com.pe/pan-de-molde-integral-dolcezza-bolsa-500g/p",
    "https://www.makro.plazavea.com.pe/pan-de-molde-integral-xl-bimbo-extra-grande-bolsa-810g/p",
    "https://www.makro.plazavea.com.pe/spaghetti-grano-de-oro-bolsa-500g/p",
    "https://www.makro.plazavea.com.pe/spaghetti-nicolini-paquete-1kg/p",
    "https://www.makro.plazavea.com.pe/spaghetti-marco-polo-bolsa-450g/p",
    "https://www.makro.plazavea.com.pe/spaghetti-don-vittorio-paquete-950g/p",
    "https://www.makro.plazavea.com.pe/fideos-spaghetti-barilla-caja-500g/p",
    "https://www.makro.plazavea.com.pe/grated-de-atun-campomar-en-aceite-vegetal-lata-160g-paquete-6un/p",
    "https://www.makro.plazavea.com.pe/filete-de-atun-beltran-en-aceite-vegetal-lata-1000g/p",
    "https://www.makro.plazavea.com.pe/filete-de-bonito-dorita-en-aceite-vegetal-lata-170g/p"
]

def buscar_precio_makro(soup):
    # Busca el contenedor 'pricebox'
    pricebox = soup.find('div', class_='pricebox')
    if pricebox:
        # Busca decimal
        decimal = pricebox.find('span', class_='decimal-price')
        decimal_txt = decimal.get_text(strip=True) if decimal else ".00"
        # El entero está como texto (junto con "S/" y antes del span decimal)
        # Eliminar "S/" y otros espacios
        texto = pricebox.get_text(" ", strip=True)
        texto = texto.replace('S/', '').strip()
        # Extraer entero antes del punto decimal
        match = re.search(r'(\d+)', texto)
        entero_txt = match.group(1) if match else "0"
        try:
            return float(f"{entero_txt}{decimal_txt}")
        except:
            pass
    # Fallback: intenta JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and "offers" in data:
                offers = data["offers"]
                if isinstance(offers, dict) and "price" in offers:
                    return float(offers["price"])
        except:
            continue
    return None

def extraer_unidad(nombre, descripcion):
    patrones = [
        r'(\d+\.?\d*)\s*(kg|und|g|ml|l|unidades?)',
        r'x\s*(\d+\.?\d*)\s*(kg|und|g|ml|l|unidades?)'
    ]
    for texto in [nombre, descripcion]:
        if texto:
            for p in patrones:
                m = re.search(p, texto, re.IGNORECASE)
                if m:
                    return f"{m.group(1).replace(',', '.')} {m.group(2).lower()}"
    return None

def calcular_precio_por_unidad(precio, unidad):
    if not precio or not unidad:
        return None
    try:
        precio = float(precio)
    except:
        return None
    m = re.match(r'(\d+\.?\d*)\s*([a-zA-Z]+)', unidad)
    if m and float(m.group(1)) != 0:
        return f"{precio / float(m.group(1)):.2f}/{m.group(2)}"
    return None

def parse_makro(html, url):
    soup = BeautifulSoup(html, 'html.parser')

    # Nombre
    nombre_tag = soup.find('h1')
    nombre = nombre_tag.get_text(strip=True) if nombre_tag else ""

    # Precio
    precio = buscar_precio_makro(soup)

    # Descripción
    descripcion = ""
    descripcion_tag = soup.find('div', class_='ProductDescription_description__text')
    if descripcion_tag:
        descripcion = descripcion_tag.get_text(separator=" ", strip=True)
    else:
        meta = soup.find('meta', {'name': 'description'})
        if meta and meta.get('content'):
            descripcion = meta['content']

    unidad = extraer_unidad(nombre, descripcion)
    precio_unidad = calcular_precio_por_unidad(precio, unidad)

    return {
        "url": url,
        "nombre": nombre,
        "precio": precio,
        "descripcion": descripcion,
        "unidad": unidad,
        "precio_unidad": precio_unidad
    }

# --- Configuración Selenium
options = Options()
options.add_argument("--headless=new")
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(options=options)

resultados = []
for url in urlsaScrapear:
    driver.get(url)
    # Espera explícitamente la clase 'pricebox'
    try:
        WebDriverWait(driver, 12).until(
            EC.presence_of_element_located((By.CLASS_NAME, "pricebox"))
        )
    except:
        print(f"No se encontró el precio a tiempo en: {url}")
    html = driver.page_source
    data = parse_makro(html, url)
    resultados.append(data)

driver.quit()

df = pd.DataFrame(resultados)
df.to_csv("datos_estructurados_makro.csv", index=False, encoding='utf-8')
print("¡Datos guardados exitosamente!")
