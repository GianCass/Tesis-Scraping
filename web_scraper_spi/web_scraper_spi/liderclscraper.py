from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re

# URLs de productos de Lider.cl
urlsaScrapear = [
    "https://www.lider.cl/supermercado/product/sku/43765/nescafe-cafe-instantaneo-tradicion-tarro-400-g"
    # Agrega más URLs aquí
]

def human_scroll(driver):
    # Simula un desplazamiento humano
    body = driver.find_element(By.TAG_NAME, 'body')
    for _ in range(random.randint(2,4)):
        for _ in range(random.randint(1,5)):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(random.uniform(0.4, 1.2))

def buscar_precio_lider(soup):
    # Busca el precio en el span correcto
    precio_tag = soup.find('span', class_='pdp-mobile-sales-price')
    if precio_tag:
        text = precio_tag.get_text()
        match = re.search(r'([\d\.,]+)', text)
        if match:
            precio = match.group(1).replace('.', '').replace(',', '.')
            try:
                return float(precio)
            except:
                return precio
    # Fallback: otros selectores posibles
    precio_alt = soup.find('span', class_='pdp-desktop-sales-price')
    if precio_alt:
        text = precio_alt.get_text()
        match = re.search(r'([\d\.,]+)', text)
        if match:
            precio = match.group(1).replace('.', '').replace(',', '.')
            try:
                return float(precio)
            except:
                return precio
    return None

def buscar_nombre_lider(soup):
    h1 = soup.find('h1')
    if h1:
        return h1.get_text(strip=True)
    title = soup.find('title')
    if title:
        return title.get_text(strip=True)
    return None

def buscar_descripcion_lider(soup):
    desc = soup.find('div', class_='pdp-description-body')
    if desc:
        return desc.get_text(separator=" ", strip=True)
    meta = soup.find('meta', {'name': 'description'})
    if meta:
        return meta.get('content')
    return None

def extraer_unidad(nombre, descripcion):
    patrones = [
        r'(\d+\.?\d*)\s*(kg|g|ml|l|unidades?|und)',
        r'(\d+\.?\d*)\s*x\s*(kg|g|ml|l|unidades?|und)'
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
    match = re.search(r'(\d+\.?\d*)\s?(kg|g|ml|l|unidades?|und)', str(unidad), re.IGNORECASE)
    if match:
        cantidad = float(match.group(1).replace(',', '.'))
        tipo = match.group(2).lower()
        if cantidad != 0:
            precio_unidad = float(precio) / cantidad
            return f"{precio_unidad:.2f}/{tipo}"
    return None

def parse_lider(html):
    soup = BeautifulSoup(html, 'html.parser')
    nombre = buscar_nombre_lider(soup)
    precio = buscar_precio_lider(soup)
    descripcion = buscar_descripcion_lider(soup)
    unidad = extraer_unidad(nombre, descripcion)
    precio_unidad = calcular_precio_por_unidad(precio, unidad)
    return nombre, precio, descripcion, unidad, precio_unidad

# --- Configuración avanzada de Selenium ---
options = Options()
options.add_argument("--window-size=1200,800")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-infobars')
options.add_argument("--lang=es-ES,es")

driver = webdriver.Chrome(options=options)

stealth(driver,
        languages=["es-ES", "es"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
)

resultados = []
for url in urlsaScrapear:
    try:
        print(f"Procesando: {url}")
        driver.get(url)
        # Espera de humano aleatorio
        t = random.uniform(6, 10)
        print(f"Esperando {t:.2f} segundos en {url} ...")
        time.sleep(t)
        human_scroll(driver)
        time.sleep(random.uniform(2, 5))
        html = driver.page_source
        nombre, precio, descripcion, unidad, precio_unidad = parse_lider(html)
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
df.to_csv("datos_estructurados_lider.csv", index=False, encoding='utf-8')
print("¡Datos guardados exitosamente!")
