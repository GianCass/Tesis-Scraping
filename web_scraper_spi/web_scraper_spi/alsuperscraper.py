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
    "https://www.alsuper.com/producto/arroz-super-extra-374296",
    "https://www.alsuper.com/producto/arroz-379848",
    "https://www.alsuper.com/producto/arroz-extra-404441",
    "https://www.alsuper.com/producto/arroz-super-extra-406506",
    "https://www.alsuper.com/producto/arroz-instantaneo-403429",
    "https://www.alsuper.com/producto/aceite-vegetal-329635",
    "https://www.alsuper.com/producto/aceite-vegetal-356595",
    "https://www.alsuper.com/producto/aceite-vegetal-383758",
    "https://www.alsuper.com/producto/aceite-vegetal-449166",
    "https://www.alsuper.com/producto/aceite-vegetal-comestible-472840",
    "https://www.alsuper.com/producto/leche-entera-uht-451075",
    "https://www.alsuper.com/producto/leche-uht-entera-premium-424114",
    "https://www.alsuper.com/producto/leche-uht-entera-396619",
    "https://www.alsuper.com/producto/leche-uht-entera-426702",
    "https://www.alsuper.com/producto/leche-entera-uht-467449",
    "https://www.alsuper.com/producto/%28t%29pan-blanco-361791",
    "https://www.alsuper.com/producto/%28t%29pan-blanco-perfect-crafted-435449",
    "https://www.alsuper.com/producto/pan-blanco--paquete-495977",
    "https://www.alsuper.com/producto/azucar-estandar-363113",
    "https://www.alsuper.com/producto/azucar-organica-365405",
    "https://www.alsuper.com/producto/azucar-refinada-404071",
    "https://www.alsuper.com/producto/cafe-soluble-mezclado-con-azucar-135296",
    "https://www.alsuper.com/producto/cafe-soluble-337987",
    "https://www.alsuper.com/producto/cafe-soluble-351220",
    "https://www.alsuper.com/producto/cafe--instantaneo-.-37629",
    "https://www.alsuper.com/producto/cafe-tostado-y-molido-402366",
    "https://www.alsuper.com/producto/huevo-blanco-con-30-653",
    "https://www.alsuper.com/producto/huevo-blanco-con-30-467225",
    "https://www.alsuper.com/producto/huevo-blanco-con-30-394553",
    "https://www.alsuper.com/producto/huevo-blanco-con-30-410581",
    "https://www.alsuper.com/producto/huevo-blanco-con-30-323673",
    "https://www.alsuper.com/producto/harina-de-trigo-pasta-fresca-411665",
    "https://www.alsuper.com/producto/%28t%29harina-fina-de-trigo-5131735",
    "https://www.alsuper.com/producto/harina-de-trigo-440582",
    "https://www.alsuper.com/producto/harina-de-trigo-438821",
    "https://www.alsuper.com/producto/harina-de-trigo-323310",
    "https://www.alsuper.com/producto/papa-cambray-47",
    "https://www.alsuper.com/producto/cebolla-blanca-924"
]

def buscar_precio_alsuper(soup):
    # Busca cualquier mat-label con ambas clases as-font-24 y as-font-bold
    for tag in soup.find_all('mat-label'):
        clases = tag.get('class', [])
        if 'as-font-24' in clases and 'as-font-bold' in clases:
            text = tag.get_text(strip=True)
            match = re.search(r'\$?\s*([\d,.]+)', text)
            if match:
                return float(match.group(1).replace(',', ''))
    # Fallback: busca cualquier número tipo precio en todos los mat-label
    for tag in soup.find_all('mat-label'):
        text = tag.get_text(strip=True)
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
    descripcion_tag = soup.find('div', class_=re.compile('descripcion', re.IGNORECASE))
    if descripcion_tag:
        return descripcion_tag.get_text(separator=" ", strip=True)
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

def parse_alsuper(html, url):
    soup = BeautifulSoup(html, 'html.parser')

    nombre = buscar_nombre(soup)
    precio = buscar_precio_alsuper(soup)
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
options.add_argument("--headless=new")
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--window-size=1920,1080')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
driver = webdriver.Chrome(options=options)

resultados = []
for url in urlsaScrapear:
    driver.get(url)
    # Espera explícitamente a que aparezca cualquier mat-label con clase as-font-bold
    try:
        WebDriverWait(driver, 12).until(
            EC.presence_of_element_located((By.CLASS_NAME, "as-font-bold"))
        )
    except:
        print(f"No se encontró el precio a tiempo en: {url}")
    html = driver.page_source
    data = parse_alsuper(html, url)
    resultados.append(data)

driver.quit()

df = pd.DataFrame(resultados)
df.to_csv("datos_estructurados_alsuper.csv", index=False, encoding='utf-8')
print("¡Datos guardados exitosamente!")
