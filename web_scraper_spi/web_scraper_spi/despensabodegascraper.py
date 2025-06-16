import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import re


urlsaScrapear = [
    "https://despensa.bodegaaurrera.com.mx/ip/arroz-italriso-super-extra-900-g/00750107931001",
    "https://despensa.bodegaaurrera.com.mx/ip/arroz-sos-grano-largo-uruguayo-1-kg/00750137281256",
    "https://despensa.bodegaaurrera.com.mx/ip/arroz-schettino-super-extra-907-g/00750137281167",
    "https://despensa.bodegaaurrera.com.mx/ip/arroz-la-merced-super-extra-907-g/00750104720340",
    "https://despensa.bodegaaurrera.com.mx/ip/arroz-aurrera-super-extra-900-g/00750179163862",
    "https://despensa.bodegaaurrera.com.mx/ip/aceite-aurrera-puro-de-soya-800-ml/00750649501087",
    "https://despensa.bodegaaurrera.com.mx/ip/aceite-vegetal-123-1-l/00000007500234",
    "https://despensa.bodegaaurrera.com.mx/ip/aceite-puro-de-canola-capullo-750-ml/00750222377259",
    "https://despensa.bodegaaurrera.com.mx/ip/aceite-vegetal-gran-tradicion-850-ml/00750103912389",
    "https://despensa.bodegaaurrera.com.mx/ip/aceite-great-value-puro-de-canola-946-ml/00750179160986",
    "https://despensa.bodegaaurrera.com.mx/ip/leche-santa-clara-entera-1-5-l/00750105537546",
    "https://despensa.bodegaaurrera.com.mx/ip/producto-lacteo-combinado-nutri-entera-1-5-l/00750102054521",
    "https://despensa.bodegaaurrera.com.mx/ip/leche-alpura-selecta-entera-1-l/00750105590503",
    "https://despensa.bodegaaurrera.com.mx/ip/leche-fresca-lala-entera-1-l/00750102052606",
    "https://despensa.bodegaaurrera.com.mx/ip/leche-san-marcos-entera-ultrapasteurizada-1-l/00750115841447",
    "https://despensa.bodegaaurrera.com.mx/ip/pan-bimbo-blanco-620-g/00750081002918",
    "https://despensa.bodegaaurrera.com.mx/ip/azucar-estandar-aurrera-900-g/00750649504573",
    "https://despensa.bodegaaurrera.com.mx/ip/azucar-great-value-refinada-2-kg/00750179162335",
    "https://despensa.bodegaaurrera.com.mx/ip/cafe-soluble-nescafe-clasico-400-g/00750105862020",
    "https://despensa.bodegaaurrera.com.mx/ip/cafe-soluble-aurrera-100-puro-200-g/00750179162349",
    "https://despensa.bodegaaurrera.com.mx/ip/cafe-garat-molido-americano-454-g/00750105241901",
    "https://despensa.bodegaaurrera.com.mx/ip/cafe-soluble-oro-200-g/00750105241760",
    "https://despensa.bodegaaurrera.com.mx/ip/cafe-soluble-great-value-colombiano-gourmet-100-g/00750179160068",
    "https://despensa.bodegaaurrera.com.mx/ip/huevo-blanco-tehuacan-30-pzas/00750300024003",
    "https://despensa.bodegaaurrera.com.mx/ip/huevo-blanco-bachoco-fresco-30-pzas/00750110152551",
    "https://despensa.bodegaaurrera.com.mx/ip/huevo-blanco-dorado-30-pzas/00750110152805",
    "https://despensa.bodegaaurrera.com.mx/ip/harina-de-trigo-san-blas-1-kg/00750107933401",
    "https://despensa.bodegaaurrera.com.mx/ip/harina-de-trigo-tres-estrellas-san-antonio-extra-fina-1-kg/00750106921003",
    "https://despensa.bodegaaurrera.com.mx/ip/harina-de-trigo-selecta-1-kg/00750140460311",
    "https://despensa.bodegaaurrera.com.mx/ip/harina-de-trigo-great-value-1-kg/00750179164405",
    "https://despensa.bodegaaurrera.com.mx/ip/papa-blanca-alfa-por-kilo/00000000004083",
    "https://despensa.bodegaaurrera.com.mx/ip/cebolla-blanca-por-kilo/00000000004663"
]

def buscar_precio_bodega(soup):
    precio_tag = soup.find('span', {'itemprop': 'price'})
    if precio_tag:
        text = precio_tag.get_text(strip=True)
        match = re.search(r'\$?\s*([\d,.]+)', text)
        if match:
            return float(match.group(1).replace(',', ''))
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

def parse_bodega(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    nombre = buscar_nombre(soup)
    precio = buscar_precio_bodega(soup)
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
# ¡No usar headless!
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--window-size=1920,1080')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

driver = webdriver.Chrome(options=options)

resultados = []
for idx, url in enumerate(urlsaScrapear):
    driver.get(url)

    # Espera aleatoria antes de scrapear, como un humano leyendo la página
    sleep_time = random.uniform(10, 20)
    print(f"Esperando {sleep_time:.2f} segundos en {url} ...")
    time.sleep(sleep_time)

    # Simula scroll hacia abajo (carga diferida o JS)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(1, 3))

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span[itemprop='price']"))
        )
    except:
        print(f"No se encontró el precio a tiempo en: {url}")

    html = driver.page_source
    data = parse_bodega(html, url)

    # Si detectas challenge/captcha (nombre == "Verifica tu identidad"), espera MUCHO antes de continuar o detén el script
    if data["nombre"] and "verifica tu identidad" in data["nombre"].lower():
        print(f"⚠️  Challenge/captcha detectado en: {url} — Pausando 2 minutos.")
        time.sleep(120)  # espera 2 minutos
        # Puedes elegir saltar al siguiente, detener el script o guardar el error para intentar después

    resultados.append(data)

    # Pausa larga adicional cada 5 productos
    if (idx + 1) % 5 == 0:
        print("Descansando 5 minutos para evitar baneo...")
        time.sleep(300)

driver.quit()

df = pd.DataFrame(resultados)
df.to_csv("datos_estructurados_bodegaaurrera.csv", index=False, encoding='utf-8')
print("¡Datos guardados exitosamente!")
