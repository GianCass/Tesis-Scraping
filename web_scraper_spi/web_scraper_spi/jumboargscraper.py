from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import json

# Lista de URLs de productos Jumbo
urlsaScrapear = [
    "https://www.jumbo.com.ar/leche-entera-la-serenisima-3sachet-1lt/p",
    "https://www.jumbo.com.ar/leche-entera-1-l-cuisine-co-nbe-mp/p",
    "https://www.jumbo.com.ar/leche-tregar-enterax-1-litro/p",
    "https://www.jumbo.com.ar/leche-manfrey-entera-u-a-t-sin-atributo-sin-atributo-sin-atributo-sin-atributo/p",
    "https://www.jumbo.com.ar/leche-entera-lechelita-uat-1-l/p",
    "https://www.jumbo.com.ar/pan-lacteado-x-585-gr-fargo/p",
    "https://www.jumbo.com.ar/pan-blanco-x-400-gr-bimbo/p",
    "https://www.jumbo.com.ar/pan-de-mesa-tradicional-la-perla-330-gr/p",
    "https://www.jumbo.com.ar/pan-blanco-lactal-460-gr/p",
    "https://www.jumbo.com.ar/pan-lactal-artesanal-premiun-semillas-590-grs-2/p",
    "https://www.jumbo.com.ar/azucar-ledesma-x-1kg/p",
    "https://www.jumbo.com.ar/azucar-premium-refinada-chango-x-1-kg/p",
    "https://www.jumbo.com.ar/azucar-1-kg-cuisine-co-nbe-mp/p",
    "https://www.jumbo.com.ar/azucar-impalpable-sin-tacc-250-gr-pergola/p",
    "https://www.jumbo.com.ar/fideos-lucchetti-tallarin-n5-x500g/p",
    "https://www.jumbo.com.ar/fideos-matarazzo-spaghetti-n7-x-500-gr/p",
    "https://www.jumbo.com.ar/fideos-don-vicente-tallarin-x500g/p",
    "https://www.jumbo.com.ar/fideos-tallarines-molto-500-gr/p",
    "https://www.jumbo.com.ar/fideos-spaghetti-barilla-500-gr/p",
    "https://www.jumbo.com.ar/pollo-campo-de-areco/p",
    "https://www.jumbo.com.ar/pollo-fresco-con-menudos-2/p",
    "https://www.jumbo.com.ar/huevos-blancos-avicoper-12-u-1-paquete-2/p",
    "https://www.jumbo.com.ar/huevos-blancos-12-un-maxima-mp-3/p",
    "https://www.jumbo.com.ar/huevos-blancos-dona-lala-x-6u-carton/p",
    "https://www.jumbo.com.ar/huevos-blancos-extra-grandes-12-un-cuisine-co-nbe-mp/p",
    "https://www.jumbo.com.ar/huevos-blancos-carnave-docena/p",
    "https://www.jumbo.com.ar/mozzarella-la-serenisima-220gr/p",
    "https://www.jumbo.com.ar/queso-cremoso-la-paulina-doble-crema-hma-x-kg/p",
    "https://www.jumbo.com.ar/queso-cremoso-punta-del-agua-horma-x-kg-2/p",
    "https://www.jumbo.com.ar/queso-cheddar-milkaut-x-145-gr/p",
    "https://www.jumbo.com.ar/queso-adler-feteado-danbo-144-gr/p",
    "https://www.jumbo.com.ar/gaseosa-coca-cola-sabor-original-2-25-l/p",
    "https://www.jumbo.com.ar/gaseosa-pepsi-botella-2-l/p",
    "https://www.jumbo.com.ar/gaseosa-paso-de-los-toros-pomelo-botella-500mlx1/p",
    "https://www.jumbo.com.ar/gaseosa-cunnington-cola-suave-2-25lt/p",
    "https://www.jumbo.com.ar/gaseosa-crush-pomelo-2-25lt/p",
    "https://www.jumbo.com.ar/papa-negra-por-kg/p",
    "https://www.jumbo.com.ar/papas-andinas-sueno-verde-600-gr/p",
    "https://www.jumbo.com.ar/papas-plychaco-noisette-500-gr/p",
    "https://www.jumbo.com.ar/tomate-redondo-grande-por-kg/p",
    "https://www.jumbo.com.ar/tomate-cherry-buy-eat-250-gr/p",
    "https://www.jumbo.com.ar/cherry-rojo-sueno-verde/p"
]

def buscar_precio_jumbo(soup):
    texto = soup.get_text()
    m = re.search(r'PRECIO SIN IMPUESTOS NACIONALES:\s*\$\s*([\d\.,]+)', texto)
    if m:
        return m.group(1).replace('.', '').replace(',', '.')
    return None

def extraer_unidad(nombre, descripcion):
    patrones = [
        r'(\d+\.?\d*)\s*l',
        r'(\d+\.?\d*)\s*ml',
        r'(\d+\.?\d*)\s*kg',
        r'(\d+\.?\d*)\s*g',
        r'(\d+\.?\d*)\s*und'
    ]
    for texto in [nombre, descripcion]:
        if texto:
            for p in patrones:
                m = re.search(p, texto, re.IGNORECASE)
                if m:
                    cantidad = m.group(1).replace(',', '.')
                    tipo = re.sub(r'[\d\.,\s]', '', p.split(r'\s*')[-1])
                    return f"{cantidad} {tipo}"
    return None

def calcular_precio_por_unidad(precio, unidad):
    if not precio or not unidad:
        return None
    try:
        precio = float(precio)
    except:
        return None
    m = re.match(r'(\d+\.?\d*)\s*([a-zA-Z]+)', unidad)
    if m:
        cantidad = float(m.group(1))
        tipo = m.group(2)
        if cantidad:
            return f"{precio / cantidad:.2f}/{tipo}"
    return None

def parse_jumbo(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Nombre
    nombre = soup.find('h1').get_text(strip=True) if soup.find('h1') else None

    # Precio
    precio = buscar_precio_jumbo(soup)

    # Descripción mejorada
    descripcion = None
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and "description" in data:
                descripcion = data["description"]
                break
        except Exception:
            continue
    if not descripcion:
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            descripcion = meta_desc['content']
    if not descripcion:
        desc_tags = soup.find_all('div')
        for tag in desc_tags:
            if 'descrip' in tag.get_text().lower():
                descripcion = tag.get_text(separator=" ", strip=True)
                break

    # Unidad y precio por unidad
    unidad = extraer_unidad(nombre, descripcion)
    precio_unidad = calcular_precio_por_unidad(precio, unidad)

    return nombre, precio, descripcion, unidad, precio_unidad

# --- Configuración Selenium
options = Options()
options.add_argument("--headless=new")
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(options=options)

# --- Bucle de scraping
resultados = []
for url in urlsaScrapear:
    try:
        print(f"Procesando: {url}")
        driver.get(url)
        time.sleep(4)
        html = driver.page_source
        nombre, precio, descripcion, unidad, precio_unidad = parse_jumbo(html)
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

# --- Guardar resultados
df = pd.DataFrame(resultados)
df.to_csv("datos_estructurados_jumbo.csv", index=False, encoding='utf-8')
print("Datos guardados en 'datos_estructurados_jumbo.csv'")
