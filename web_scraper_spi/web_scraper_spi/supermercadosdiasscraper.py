from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import json

urlsaScrapear = [
    "https://diaonline.supermercadosdia.com.ar/leche-multidefensa-3--la-serenisima-1-lt-274565/p",
    "https://diaonline.supermercadosdia.com.ar/leche-entera-larga-vida-lechelita-1-lt-300130/p",
    "https://diaonline.supermercadosdia.com.ar/leche-entera-dia-larga-vida-1-lt-608/p",
    "https://diaonline.supermercadosdia.com.ar/leche-fresca-entera-3--fortificada-casanto-sachet-1-lt-288868/p",
    "https://diaonline.supermercadosdia.com.ar/leche-entera-las-3-ninas-larga-vida-1-lt-58463/p",
    "https://diaonline.supermercadosdia.com.ar/pan-integral-fargo-400-gr-263877/p",
    "https://diaonline.supermercadosdia.com.ar/pan-blanco-bimbo-610-gr-263871/p",
    "https://diaonline.supermercadosdia.com.ar/pan-lacteado-noly-grande-600-gr-138110/p",
    "https://diaonline.supermercadosdia.com.ar/pan-salvado-lactal-560-gr-241835/p",
    "https://diaonline.supermercadosdia.com.ar/pan-blanco-grande-dia-460-gr-295395/p",
    "https://diaonline.supermercadosdia.com.ar/azucar-ledesma-refinado-superior-1-kg-129208/p",
    "https://diaonline.supermercadosdia.com.ar/azucar-plus-dia-comun-tipo-a-1-kg-130321/p",
    "https://diaonline.supermercadosdia.com.ar/azucar-la-providencia-1-kg-294967/p",
    "https://diaonline.supermercadosdia.com.ar/azucar-comun-arcor-tipo--a--1-kg-260592/p",
    "https://diaonline.supermercadosdia.com.ar/azucar-azucel-comun-tipo--a--500-gr-266204/p",
    "https://diaonline.supermercadosdia.com.ar/fideos-spaghetti-n7-luchetti-500-gr-40877/p",
    "https://diaonline.supermercadosdia.com.ar/fideos-spaghetti-n3-matarazzo-500-gr-38576/p",
    "https://diaonline.supermercadosdia.com.ar/fideos-spaghetti-dia-500-gr-285831/p",
    "https://diaonline.supermercadosdia.com.ar/fideos-tallarin-don-vicente-500-gr-299848/p",
    "https://diaonline.supermercadosdia.com.ar/fideos-spaghetti-favorita-500-gr-61256/p",
    "https://diaonline.supermercadosdia.com.ar/patamuslo-iqf-granja-3-arroyos-800-gr-298506/p",
    "https://diaonline.supermercadosdia.com.ar/pollo-fresco-x-1-kg-90150/p",
    "https://diaonline.supermercadosdia.com.ar/huevo-blanco-grande-12-ud-48133/p",
    "https://diaonline.supermercadosdia.com.ar/queso-cremoso-la-serenisima-1-kg-299838/p",
    "https://diaonline.supermercadosdia.com.ar/queso-cremoso-la-paulina-x-kg-90181/p",
    "https://diaonline.supermercadosdia.com.ar/queso-cremoso-vacalin-400-gr-150653/p",
    "https://diaonline.supermercadosdia.com.ar/queso-muzzarella-dona-aurora-ahumado-500-gr-268361/p",
    "https://diaonline.supermercadosdia.com.ar/queso-muzzarella-dia-250-gr-271414/p",
    "https://diaonline.supermercadosdia.com.ar/gaseosa-coca-cola-sabor-original-225-lt-14837/p",
    "https://diaonline.supermercadosdia.com.ar/gaseosa-cola-regular-pepsi-2-lt-115102/p",
    "https://diaonline.supermercadosdia.com.ar/gaseosa-cola-dia-15-lt-24841/p",
    "https://diaonline.supermercadosdia.com.ar/gaseosa-cola-cunnington-225-lt-264018/p",
    "https://diaonline.supermercadosdia.com.ar/gaseosa-crush-sin-azucar-pomelo-amarillo-225-lt-114822/p",
    "https://diaonline.supermercadosdia.com.ar/papa-negra-x-1-kg-90094/p",
    "https://diaonline.supermercadosdia.com.ar/tomate-redondo-x-1-kg-90127/p"
]

def buscar_precio_dia(soup):
    # Busca el precio usando la clase exacta que viste
    precio_tag = soup.find('span', class_='diaio-store-5-x-sellingPriceValue')
    if precio_tag:
        texto = precio_tag.get_text(strip=True)
        texto = texto.replace('$', '').replace('\xa0', '').replace('.', '').replace(',', '.').strip()
        try:
            return float(texto)
        except:
            pass

    # Fallback: intenta encontrar el precio en JSON-LD
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
        r'(\d+\.?\d*)\s*(lt|und|kg|gr|g|ml|l|unidades?)',
        r'x\s*(\d+\.?\d*)\s*(lt|und|kg|gr|g|ml|l|unidades?)'
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

def parse_dia(html, url):
    soup = BeautifulSoup(html, 'html.parser')

    nombre_tag = soup.find('h1')
    nombre = nombre_tag.get_text(strip=True) if nombre_tag else ""

    precio = buscar_precio_dia(soup)

    descripcion = ""
    descripcion_tag = soup.find('div', {'class': 'productDescription_descriptionContainer__1KvYI'})
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
    # Espera explícitamente hasta que el precio esté presente
    try:
        WebDriverWait(driver, 12).until(
            EC.presence_of_element_located((By.CLASS_NAME, "diaio-store-5-x-sellingPriceValue"))
        )
    except:
        print(f"No se encontró el precio a tiempo en: {url}")
    html = driver.page_source
    data = parse_dia(html, url)
    resultados.append(data)

driver.quit()

df = pd.DataFrame(resultados)
df.to_csv("datos_estructurados_dia.csv", index=False, encoding='utf-8')
print("¡Datos guardados exitosamente!")
