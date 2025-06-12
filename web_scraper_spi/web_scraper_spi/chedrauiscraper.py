from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# URLs de Chedraui
urlsaScrapear = [
    "https://www.chedraui.com.mx/arroz-schettino-verde-900g-3008386/p",
    # Agrega más URLs aquí...
]

def extraer_unidad(nombre, descripcion):
    patrones = [
        r'(\d+\.?\d*)\s*(kg|gr|g|ml|l|un|und|unidades?)',
        r'x\s*(\d+\.?\d*)\s*(kg|gr|g|ml|l|un|und|unidades?)'
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
    match = re.search(r'(\d+\.?\d*)\s*(kg|gr|g|ml|l|un|und|unidades?)', str(unidad), re.IGNORECASE)
    if match:
        cantidad = float(match.group(1).replace(',', '.'))
        tipo = match.group(2).lower()
        if cantidad != 0:
            precio_unidad = precio / cantidad
            return f"{precio_unidad:.2f}/{tipo}"
    return None

def parse_chedraui(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Nombre del producto
    nombre_tag = soup.find('h1')
    nombre = nombre_tag.get_text(strip=True) if nombre_tag else None

    # Precio (en span con data-testid="price-value")
    precio = None
    precio_tag = soup.find('span', {'data-testid': 'price-value'})
    if precio_tag:
        precio_raw = precio_tag.get_text(strip=True)
        precio = re.sub(r'[^\d.]', '', precio_raw)
        try:
            precio = float(precio)
        except:
            precio = None

    # Descripción
    descripcion = None
    descripcion_tag = soup.find('div', class_=re.compile("productDescriptionText", re.I))
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
        time.sleep(6)  # Dale un poco más de tiempo para cargar el precio
        html = driver.page_source
        # Si quieres guardar el HTML para debug, descomenta:
        # with open("chedraui_debug.html", "w", encoding="utf-8") as f:
        #     f.write(html)
        nombre, precio, descripcion, unidad, precio_unidad = parse_chedraui(html)
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
df.to_csv("datos_estructurados_chedraui.csv", index=False, encoding='utf-8')
print("¡Datos guardados en 'datos_estructurados_chedraui.csv'!")
