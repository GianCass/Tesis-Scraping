from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import json

# URLs de productos de Jumbo Colombia
urlsaScrapear = [
    "https://www.jumbocolombia.com/huevos-kikes-rojo-tipo-aa-x30und/p",
    "https://www.jumbocolombia.com/huevo-aa-rojo-x30-unidades-santa-reyes/p",
    "https://www.jumbocolombia.com/huevo-santa-anita-ome-ga-aaa-rojo-x-30-und/p",
    "https://www.jumbocolombia.com/campesino-termoencogido-oro-aa-x30-unidades/p",
    "https://www.jumbocolombia.com/huevo-sixpack-x-3und-gallina-feliz-100porciento-natural/p",
    "https://www.tiendasjumbo.co/arroz-diana-x-1-kg/p/",
    "https://www.tiendasjumbo.co/arroz-roa-x5kg/p",
    "https://www.tiendasjumbo.co/arroz-florhuila-x-10-kg/p",
    "https://www.tiendasjumbo.co/arroz-castellano-premium-blanco-x4000g/p",
    "https://www.tiendasjumbo.co/arroz-sonora-x3kg/p",
    "https://www.tiendasjumbo.co/arroz-dona-pepa-parbolizado-x1000g/p",
    "https://www.tiendasjumbo.co/pan-bimbo-integral-bolsa-x-480g-3643446/p",
    "https://www.jumbocolombia.com/pan-comapan-extragrande-x-750-g/p",
    "https://www.jumbocolombia.com/pan-bimbo-vital-frutos-rojos-x-460-g/p",
    "https://www.jumbocolombia.com/pan-mauka-sagu-tajado-sin-gluten-x450g/p",
    "https://www.tiendasjumbo.co/pan-blanco-extra-largo-santa-clara-x-550-g/p",
    "https://www.tiendasjumbo.co/leche-entera-alpina-bolsa-x6-und-x1100ml-0460684/p",
    "https://www.tiendasjumbo.co/leche-entera-colanta-bolsa-x6-und-x1000ml-3509862/p",
    "https://www.tiendasjumbo.co/leche-alqueria-original-pague-5-lleve-6x1100ml-c-u/p",
    "https://www.jumbocolombia.com/leche-maxima-entera-bolsa-x-900ml/p",
    "https://www.jumbocolombia.com/tomate-larga-vida-x-500g/p",
    "https://www.jumbocolombia.com/tomate-chonto-x-500-g/p",
    "https://www.jumbocolombia.com/tomate-frescocampo-kosher-x-1000-g/p",
    "https://www.jumbocolombia.com/banano-uraba-x-500-g/p",
    "https://www.jumbocolombia.com/banano-deshidratado-x-200-g/p",
    "https://www.tiendasjumbo.co/cebolla-cabezona-a-granel-x-500g/p",
    "https://www.jumbocolombia.com/cebolla-cabezona-malla-x-2000g/p",
    "https://www.jumbocolombia.com/cebolla-cabezona-frescocampo-kosher-x-1000g/p",
    "https://www.jumbocolombia.com/papa-capira-x-500-g/p",
    "https://www.jumbocolombia.com/papa-parda-pastusa-granel-x-500-g/p",
    "https://www.jumbocolombia.com/papa-pastusa-x-2500-g/p",
    "https://www.tiendasjumbo.co/papa-mccain-rapipapa-rustica-x1000g/p",
    "https://www.jumbocolombia.com/queso-blanco-x-500-g-colanta/p",
    "https://www.jumbocolombia.com/queso-mozarella-tajado-alpina-x-25-und-x-400-g/p",
    "https://www.jumbocolombia.com/queso-superior-mozarella-tajado-x400g-pn/p",
    "https://www.jumbocolombia.com/queso-campo-real-mozzarella-tajado-x500g/p",
    "https://www.jumbocolombia.com/queso-mozzarella-light-pasco-x-450-g/p",
    "https://www.jumbocolombia.com/queso-butirro-del-vecchio-x3-und-x210-grs/p",
    "https://www.tiendasjumbo.co/azucar-blanco-riopaila-x-1000g/p",
    "https://www.tiendasjumbo.co/azucar-manuelita-alta-pureza-x-1-kilo/p",
    "https://www.tiendasjumbo.co/azucar-incauca-blanco-especial-1-kg/p",
    "https://www.tiendasjumbo.co/azucar-blanco-mayaguez-x-2500-g/p",
    "https://www.tiendasjumbo.co/azucar-blanco-2-5kg-providencia/p"
]

def buscar_precio_jsonld(soup):
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and "offers" in data:
                offers = data["offers"]
                if isinstance(offers, dict):
                    price = offers.get("price")
                    if price:
                        return float(price)
                elif isinstance(offers, list):
                    price = offers[0].get("price")
                    if price:
                        return float(price)
        except Exception:
            continue
    return None

def buscar_precio_total_robusto(soup, precio_unidad=None):
    texto = soup.get_text()
    precios = []
    for match in re.finditer(r"\$[\s]*([\d\.]+)", texto):
        start = match.start()
        before = texto[max(0, start-10):start]
        after = texto[match.end():match.end()+10]
        if '(' in before or ')' in after or 'un a' in before.lower():
            continue
        try:
            valor = int(match.group(1).replace('.', '').replace(',', ''))
            precios.append(valor)
        except:
            continue
    # Filtra precios lógicamente posibles (en Colombia, productos de supermercado están entre 1.000 y 100.0000)
    precios_filtrados = [p for p in precios if 1000 < p < 1000000]
    if precios_filtrados:
        return min(precios_filtrados)
    # Si no encontró, retorna el menor de todos
    if precios:
        return min(precios)
    return None

def extraer_precio_unidad(soup):
    texto = soup.get_text()
    match = re.search(r"\(\s*un\s*a\s*\$\s*([\d\.,]+)", texto, re.IGNORECASE)
    if match:
        precio_unidad = match.group(1)
        precio_unidad = precio_unidad.replace('.', '').replace(',', '.')
        return float(precio_unidad)
    return None

def extraer_unidad(nombre, descripcion):
    patrones = [r'(\d+)\s*(und|kg|gr|g|ml|l|unidades?)', r'x\s*(\d+)\s*(und|kg|gr|g|ml|l|unidades?)']
    for texto in [nombre, descripcion]:
        if texto:
            for p in patrones:
                m = re.search(p, texto, re.IGNORECASE)
                if m:
                    return f"{m.group(1)} {m.group(2).lower()}"
    return None

def parse_jumbo_colombia(html):
    soup = BeautifulSoup(html, 'html.parser')
    nombre = soup.find('h1').get_text(strip=True) if soup.find('h1') else None
    precio_unidad_val = extraer_precio_unidad(soup)
    precio = buscar_precio_jsonld(soup)
    if precio is None:
        precio = buscar_precio_total_robusto(soup, precio_unidad=precio_unidad_val)
    descripcion_tag = soup.find('div', class_='vtex-store-components-3-x-productDescriptionText')
    descripcion = descripcion_tag.get_text(" ", strip=True) if descripcion_tag else None
    if not descripcion:
        meta = soup.find('meta', {'name': 'description'})
        descripcion = meta.get('content') if meta else ''
    unidad = extraer_unidad(nombre, descripcion)
    if precio is not None:
        precio = float(precio)
    if precio_unidad_val and unidad:
        try:
            precio_unidad_str = f"{precio_unidad_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            precio_unidad_val = f"{precio_unidad_str}/{unidad.split()[1]}"
        except:
            precio_unidad_val = f"{precio_unidad_val}/und"
    return nombre, precio, descripcion, unidad, precio_unidad_val

def corregir_precio_fantasma(precio):
    """
    Corrige precios tipo 49903.0 -> 4990, 229903.0 -> 22990, etc.
    Solo aplica a precios mayores a 9999.
    """
    try:
        if pd.notnull(precio) and precio != '' and float(precio) > 9999:
            precio_str = str(int(float(precio)))
            if precio_str.endswith('3'):
                precio_real = int(precio_str[:-1])  # Quita el último 3
                return precio_real
            elif precio_str.endswith('0'):
                return int(precio_str[:-1])
            else:
                return int(float(precio) / 10)
        else:
            return int(precio) if pd.notnull(precio) and precio != '' else ''
    except:
        return precio

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
    time.sleep(6)
    html = driver.page_source
    nombre, precio, descripcion, unidad, precio_unidad = parse_jumbo_colombia(html)
    resultados.append({
        "url": url,
        "nombre": nombre,
        "precio": precio,
        "descripcion": descripcion,
        "unidad": unidad,
        "precio_unidad": precio_unidad
    })

driver.quit()

df = pd.DataFrame(resultados)
# --- CORRIGE EL PRECIO FANTASMA ---
df['precio'] = df['precio'].apply(corregir_precio_fantasma)
df.to_csv("datos_estructurados_jumbo_colombia.csv", index=False, encoding='utf-8')
print("¡Datos guardados exitosamente!")
