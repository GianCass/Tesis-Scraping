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
    "https://www.plazavea.com.pe/arroz-extra-costeno-bolsa-5kg/p",
    "https://www.plazavea.com.pe/arroz-extra-vallenorte-bolsa-5kg/p",
    "https://www.plazavea.com.pe/arroz-extra-paisana-bolsa-5kg/p",
    "https://www.plazavea.com.pe/arroz-extra-bell-s-bolsa-5kg/p",
    "https://www.plazavea.com.pe/arroz-extra-faraon-bolsa-5kg/p",
    "https://www.plazavea.com.pe/piernas-y-muslos-aderezadas-redondos-oriental-bolsa-780g/p",
    "https://www.plazavea.com.pe/filete-de-pechuga-importado-sadia-empaque-1kg/p",
    "https://www.plazavea.com.pe/muslitos-de-pollo-copacol-bolsa-800g/p",
    "https://www.plazavea.com.pe/pollo-entero-sin-menudencia-congelado-perdix-1300g/p",
    "https://www.plazavea.com.pe/pollo-entero-artisan-libre-de-antibioticos-x-kg/p",
    "https://www.plazavea.com.pe/cafe-instantaneo-nescafe-fina-seleccion-frasco-200g/p",
    "https://www.plazavea.com.pe/cafe-liofilizado-juan-valdez-regular-frasco-190g/p",
    "https://www.plazavea.com.pe/cafe-instantaneo-altomayo-gourmet-frasco-170g/p",
    "https://www.plazavea.com.pe/cafe-tostado-y-molido-cafetal-selecto-bolsa-900g/p",
    "https://www.plazavea.com.pe/cafe-instantaneo-bells-granulado-frasco-200g/p",
    "https://www.plazavea.com.pe/aceite-vegetal-premium-primor-botella-900ml/p",
    "https://www.plazavea.com.pe/aceite-de-oliva-y-girasol-carbonell-botella-1l/p",
    "https://www.plazavea.com.pe/aceite-vegetal-cocinero-botella-900ml/p",
    "https://www.plazavea.com.pe/aceite-vegetal-bells-botella-900ml/p",
    "https://www.plazavea.com.pe/aceite-de-oliva-el-olivar-extra-virgen-botella-200ml/p",
    "https://www.plazavea.com.pe/leche-uht-sin-lactosa-gloria-zero-caja-1l/p",
    "https://www.plazavea.com.pe/leche-fresca-laive-entera-bolsa-900ml/p",
    "https://www.plazavea.com.pe/leche-uht-vigor-bolsa-800ml/p",
    "https://www.plazavea.com.pe/leche-descremada-gloria-slim-uht-triple-zero-caja-1l/p",
    "https://www.plazavea.com.pe/leche-entera-bells-caja-1l/p",
    "https://www.plazavea.com.pe/huevos-pardos-bells-bandeja-30un/p",
    "https://www.plazavea.com.pe/huevos-pardos-la-calera-paquete-30un/p",
    "https://www.plazavea.com.pe/huevos-pardos-artisan-bandeja-15un/p",
    "https://www.plazavea.com.pe/huevos-pardos-gallinas-libres-bandeja-12un/p",
    "https://www.plazavea.com.pe/azucar-rubia-dulfina-bolsa-5-kg/p",
    "https://www.plazavea.com.pe/azucar-rubia-cartavio-bolsa-5kg/p",
    "https://www.plazavea.com.pe/azucar-rubia-bells-bolsa-1kg/p",
    "https://www.plazavea.com.pe/azucar-rubia-costeno-bolsa-1kg/p",
    "https://www.plazavea.com.pe/azucar-rubia-casa-grande-bolsa-5kg/p",
    "https://www.plazavea.com.pe/pan-de-molde-blanco-xl-bimbo-extra-grande-bolsa-770g/p",
    "https://www.plazavea.com.pe/pan-de-molde-blanco-bells-mediano-bolsa-500g/p",
    "https://www.plazavea.com.pe/pan-de-molde-union-multisemillas-y-avena-bolsa-540g/p",
    "https://www.plazavea.com.pe/pan-de-molde-blanco-don-mamino-sin-corteza-bolsa-560g/p",
    "https://www.plazavea.com.pe/pan-de-molde-integral-bimbo-vital-multicereal-bolsa-600g/p",
    "https://www.plazavea.com.pe/spaghetti-don-vittorio-paquete-950g/p",
    "https://www.plazavea.com.pe/fideo-cabello-de-angel-lavaggi-bolsa-250g/p",
    "https://www.plazavea.com.pe/fideos-spaguetti-bells-bolsa-900g/p",
    "https://www.plazavea.com.pe/fideos-spaghetti-barilla-caja-500g/p",
    "https://www.plazavea.com.pe/pasta-tornillo-molitalia-bolsa-500g/p",
    "https://www.plazavea.com.pe/filete-de-atun-en-aceite-vegetal-florida-lata-140g/p",
    "https://www.plazavea.com.pe/filete-de-atun-campomar-en-aceite-lata-150g/p",
    "https://www.plazavea.com.pe/trozos-de-atun-bells-en-aceite-lata-150gr/p",
    "https://www.plazavea.com.pe/filete-de-atun-en-agua-y-sal-gloria-lata-140g/p",
    "https://www.plazavea.com.pe/trozos-de-atun-primor-en-aceite-vegetal-lata-140g/p"
]

def buscar_precio_plazavea(soup):
    # Busca las partes del precio
    entero = soup.find('span', class_='ProductCard__price__integer')
    decimal = soup.find('span', class_='ProductCard__price__decimal')
    if entero:
        entero_txt = entero.get_text(strip=True)
        decimal_txt = decimal.get_text(strip=True) if decimal else ".00"
        try:
            return float(entero_txt.replace(',', '') + decimal_txt)
        except:
            pass

    # Fallback: intenta JSON-LD (por si acaso)
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

def parse_plazavea(html, url):
    soup = BeautifulSoup(html, 'html.parser')

    # Nombre
    nombre_tag = soup.find('h1')
    nombre = nombre_tag.get_text(strip=True) if nombre_tag else ""

    # Precio
    precio = buscar_precio_plazavea(soup)

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
    # Espera explícitamente que aparezca el precio
    try:
        WebDriverWait(driver, 12).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ProductCard__price__integer"))
        )
    except:
        print(f"No se encontró el precio a tiempo en: {url}")
    html = driver.page_source
    data = parse_plazavea(html, url)
    resultados.append(data)

driver.quit()

df = pd.DataFrame(resultados)
df.to_csv("datos_estructurados_plazavea.csv", index=False, encoding='utf-8')
print("¡Datos guardados exitosamente!")
