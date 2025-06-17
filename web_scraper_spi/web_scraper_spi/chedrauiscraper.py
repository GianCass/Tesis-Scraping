from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

urlsaScrapear = [
    "https://www.chedraui.com.mx/arroz-schettino-verde-900g-3008386/p",
    "https://www.chedraui.com.mx/arroz-verde-valle-super-extra-900g-3008380/p",
    "https://www.chedraui.com.mx/arroz-sos-super-extra-rojo-900g-3008327/p",
    "https://www.chedraui.com.mx/arroz-super-extra-chedraui-900g-3250655/p",
    "https://www.chedraui.com.mx/arroz-la-merced-super-extra-900g-3247692/p",
    "https://www.chedraui.com.mx/aceite-vegetal-nutrioli-antigoteo-puro-de-soya-700ml-3738492/p",
    "https://www.chedraui.com.mx/aceite-chedraui-mixto-800ml-3717376/p",
    "https://www.chedraui.com.mx/aceite-patrona-mixto-1-l-3009886/p",
    "https://www.chedraui.com.mx/aceite-pam-original-170g-3010037/p",
    "https://www.chedraui.com.mx/aceite-123-vegetal-123-1l-3009948/p",
    "https://www.chedraui.com.mx/leche-fresca-lala-entera-1l-3012021/p",
    "https://www.chedraui.com.mx/leche-alpura-selecta-entera-1l-3019413/p",
    "https://www.chedraui.com.mx/leche-alpura-clasica-4-piezas-de-1l-cu-3713405/p",
    "https://www.chedraui.com.mx/leche-santa-clara-entera-1l-3019421/p",
    "https://www.chedraui.com.mx/leche-barista-bove-entera-946ml-3804250/p",
    "https://www.chedraui.com.mx/pan-bimbo-blanco-620g-3817240/p",
    "https://www.chedraui.com.mx/pan-butter-krust-blanco-567g-3851928/p",
    "https://www.chedraui.com.mx/pan-natures-own-blanco-624g-3750236/p",
    "https://www.chedraui.com.mx/pan-blanco-de-caja-selecto-675g-3105808/p",
    "https://www.chedraui.com.mx/pan-wonder-super-blanco-ajonjoli-567g-3271695/p",
    "https://www.chedraui.com.mx/azucar-chedraui-estandar-900g-3793492/p",
    "https://www.chedraui.com.mx/azucar-zulka-glass-500g-3546184/p",
    "https://www.chedraui.com.mx/cafe-nescafe-clasico-300g-3822396/p",
    "https://www.chedraui.com.mx/cafe-legal-soluble-regular-180-g-3278434/p",
    "https://www.chedraui.com.mx/cafe-gold-los-portales-de-cordoba-de-170g-3734679/p",
    "https://www.chedraui.com.mx/cafe-molido-blason-gourmet-americano-400g-3202009/p",
    "https://www.chedraui.com.mx/cafe-garat-americano-molido-340g-3019146/p",
    "https://www.chedraui.com.mx/huevo-blanco-bachoco-30-piezas-3101196/p",
    "https://www.chedraui.com.mx/huevo-san-juan-blanco-30-piezas-3101215/p",
    "https://www.chedraui.com.mx/huevos-blancos-tehuacan-30-piezas-3101222/p",
    "https://www.chedraui.com.mx/huevo-blanco-el-calvario-30-piezas-3295668/p",
    "https://www.chedraui.com.mx/huevo-rojo-del-rancho-30-piezas-3793290/p",
    "https://www.chedraui.com.mx/harina-san-blas-trigo-500g-3775966/p",
    "https://www.chedraui.com.mx/harina-de-trigo-selecta-1kg-3018596/p",
    "https://www.chedraui.com.mx/harina-chedraui-trigo-1kg-3793489/p",
    "https://www.chedraui.com.mx/harina-de-trigo-la-moderna-1kg-3256831/p",
    "https://www.chedraui.com.mx/harina-de-trigo-sol-de-oro-1kg-3168625/p",
    "https://www.chedraui.com.mx/papa-blanca-por-kg-3102855/p",
    "https://www.chedraui.com.mx/cebolla-blanca-por-kg-3102851/p"
]

def buscar_precio_chedraui(soup):
    # Extrae las partes del precio
    entero = soup.find('span', class_=re.compile('currencyInteger'))
    decimal = soup.find('span', class_=re.compile('currencyFraction'))
    if entero and decimal:
        precio = f"{entero.get_text(strip=True)}.{decimal.get_text(strip=True)}"
        try:
            return float(precio)
        except:
            return None
    return None

def buscar_nombre(soup):
    nombre_tag = soup.find('h1')
    if nombre_tag:
        return nombre_tag.get_text(strip=True)
    title_tag = soup.find('title')
    if title_tag:
        return title_tag.get_text(strip=True)
    return ""

def buscar_descripcion(soup):
    meta_desc = soup.find('meta', {'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        return meta_desc['content'].strip()
    return ""

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

def parse_chedraui(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    nombre = buscar_nombre(soup)
    precio = buscar_precio_chedraui(soup)
    descripcion = buscar_descripcion(soup)
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

# --- Configuración Selenium ---
options = Options()
# Quita headless si quieres ver el proceso y evitar bloqueo
# options.add_argument("--headless=new")
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--window-size=1920,1080')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

driver = webdriver.Chrome(options=options)

resultados = []
for url in urlsaScrapear:
    driver.get(url)
    try:
        # Espera a que aparezca la parte entera del precio
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "vtex-product-price-1-x-currencyInteger"))
        )
    except:
        print(f"No se encontró el precio a tiempo en: {url}")

    time.sleep(3)
    html = driver.page_source
    data = parse_chedraui(html, url)
    resultados.append(data)

driver.quit()

df = pd.DataFrame(resultados)
df.to_csv("datos_estructurados_chedraui.csv", index=False, encoding='utf-8')
print("¡Datos guardados exitosamente!")
