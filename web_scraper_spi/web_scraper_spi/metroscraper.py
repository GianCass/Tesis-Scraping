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
    "https://www.metro.pe/arroz-extra-costeno-5kg-14974/p",
    "https://www.metro.pe/arroz-extra-valle-norte-mejorado-bolsa-5-kg-107169/p",
    "https://www.metro.pe/arroz-superior-paisana-x-5kg/p",
    "https://www.metro.pe/arroz-extra-metro-5kg-391214/p",
    "https://www.metro.pe/arroz-familiar-maxima-bolsa-5-kg-498326/p",
    "https://www.metro.pe/pollo-entero-marinado-sazon-brasa-san-fernando-1-4kg/p",
    "https://www.metro.pe/pechuga-entera-de-pollo-redondos-x-kg-1001792/p",
    "https://www.metro.pe/caf-instant-neo-altomayo-gourmet-170g-caf-instant-neo-altomayo-gourmet-170g/p",
    "https://www.metro.pe/cafe-molido-cafetal-selecto-454g/p",
    "https://www.metro.pe/cafe-instantaneo-nescafe-fina-seleccion-200g/p",
    "https://www.metro.pe/cafe-molido-descafeinado-britt-250g-133095004/p",
    "https://www.metro.pe/cafe-molido-y-tostado-cuisine-co-500g/p",
    "https://www.metro.pe/aceite-vegetal-primor-premium-botella-900ml-3198/p",
    "https://www.metro.pe/aceite-vegetal-metro-botella-900-ml-717239/p",
    "https://www.metro.pe/aceite-de-soya-sao-botella-900ml-31484/p",
    "https://www.metro.pe/aceite-vegetal-maxima-botella-900-ml-717238/p",
    "https://www.metro.pe/aceite-vegetal-cuisine-co-900ml-786936/p",
    "https://www.metro.pe/leche-parcialmente-descremada-gloria-light-caja-1l-59533001/p",
    "https://www.metro.pe/leche-semidescremada-uht-laive-sin-lactosa-light-caja-946ml-998405/p",
    "https://www.metro.pe/leche-uht-vigor-bolsa-800ml/p",
    "https://www.metro.pe/leche-deslactosada-danlac-light-botella-900ml-986461/p",
    "https://www.metro.pe/leche-uht-light-cuisine-co-caja-1-lt/p",
    "https://www.metro.pe/huevos-clasicos-pardos-la-calera-30un-2/p",
    "https://www.metro.pe/huevos-pardos-metro-30un-1009776/p",
    "https://www.metro.pe/huevos-pardos-artisan-15un-964245/p",
    "https://www.metro.pe/huevos-gallinas-libres-12un-2/p",
    "https://www.metro.pe/huevos-pardo-san-fernando-30un-1035943/p",
    "https://www.metro.pe/azucar-rubia-metro-5kg-127643/p",
    "https://www.metro.pe/azucar-rubia-maxima-bolsa-5-kg-714287/p",
    "https://www.metro.pe/azucar-rubia-paramonga-bolsa-5-kg-566556/p",
    "https://www.metro.pe/azucar-rubia-dulfina-bolsa-5-kg-465118/p",
    "https://www.metro.pe/az-car-rubia-cuisine-co-5kg-902155/p",
    "https://www.metro.pe/pan-de-molde-blanco-bimbo-xl-770g-1033017/p",
    "https://www.metro.pe/pan-de-molde-de-semillas-bimbo-vital-bolsa-600-g/p",
    "https://www.metro.pe/pan-de-molde-don-mamino-blanco-sin-corteza-bolsa-560-g/p",
    "https://www.metro.pe/pan-de-molde-union-multisemillas-con-avena-540g/p",
    "https://www.metro.pe/pan-de-molde-blanco-cuisine-co-600g-115504/p",
    "https://www.metro.pe/spaguetti-nro-5-cuisine-co-500g-569514/p",
    "https://www.metro.pe/spaguetti-quadratto-la-molisana-paquete-500-g-2/p",
    "https://www.metro.pe/spaguetti-barilla-integral-caja-500-g-2/p",
    "https://www.metro.pe/fideo-spaghetti-nicolini-1kg-962247/p",
    "https://www.metro.pe/lomos-de-at-n-en-aceite-campomar-lata-150g-147017001/p",
    "https://www.metro.pe/solido-de-atun-florida-lata-140g/p",
    "https://www.metro.pe/trozos-de-atun-en-aceite-primor-140g/p",
    "https://www.metro.pe/filete-de-atun-en-agua-y-sal-metro-140g-756790/p",
    "https://www.metro.pe/trozos-de-atun-en-aceite-vegetal-cuisine-co-140g-789708/p"
]

def buscar_precio_metro(soup):
    # Busca las partes del precio según las clases VTEX
    entero = soup.find('span', class_=re.compile('vtex-product-price-1-x-currencyInteger'))
    fraccion = soup.find('span', class_=re.compile('vtex-product-price-1-x-currencyFraction'))
    if entero:
        entero_txt = entero.get_text(strip=True)
        fraccion_txt = fraccion.get_text(strip=True) if fraccion else "00"
        try:
            return float(f"{entero_txt}.{fraccion_txt}")
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

def parse_metro(html, url):
    soup = BeautifulSoup(html, 'html.parser')

    # Nombre
    nombre_tag = soup.find('h1')
    nombre = nombre_tag.get_text(strip=True) if nombre_tag else ""

    # Precio
    precio = buscar_precio_metro(soup)

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
    # Espera explícitamente a que esté la parte entera del precio
    try:
        WebDriverWait(driver, 12).until(
            EC.presence_of_element_located((By.CLASS_NAME, "vtex-product-price-1-x-currencyInteger"))
        )
    except:
        print(f"No se encontró el precio a tiempo en: {url}")
    html = driver.page_source
    data = parse_metro(html, url)
    resultados.append(data)

driver.quit()

df = pd.DataFrame(resultados)
df.to_csv("datos_estructurados_metro.csv", index=False, encoding='utf-8')
print("¡Datos guardados exitosamente!")
