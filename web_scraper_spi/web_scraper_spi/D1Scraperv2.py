from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# URLs de productos Tiendas D1 (puedes agregar más)
urlsaScrapear = [
    "https://domicilios.tiendasd1.com/p/huevos-tipo-l-kikes-30-und-12006002",
    "https://domicilios.tiendasd1.com/p/huevo-tipo-aa-sol-naciente-12-und-12000291",
    "https://domicilios.tiendasd1.com/p/arroz-diana-500-g-12002073",
    "https://domicilios.tiendasd1.com/p/arroz-estandar-500-grs-12000051",
    "https://domicilios.tiendasd1.com/p/pan-tajado-multigranos-450-g-12005835",
    "https://domicilios.tiendasd1.com/p/pan-tajado-mantequilla-450g-12005834",
    "https://domicilios.tiendasd1.com/p/pan-vital-fruticereal-500-g-12004570",
    "https://domicilios.tiendasd1.com/p/leche-equilibrio-tetrapak-uhtlatti-900ml-12005778",
    "https://domicilios.tiendasd1.com/p/leche-saborizada-alpin-pack-x3-185ml-12006263",
    "https://domicilios.tiendasd1.com/p/tomate-chonto-x-1000-g-12005556",
    "https://domicilios.tiendasd1.com/p/tomates-secos-ainoa-180-g-12000941",
    "https://domicilios.tiendasd1.com/p/banano-unidad-12005468",
    "https://domicilios.tiendasd1.com/p/cebolla-cabezona-x-1000g-12005767",
    "https://domicilios.tiendasd1.com/p/papa-airfryer-mccain-x-500g-12006077",
    "https://domicilios.tiendasd1.com/p/papa-capira-x-2500-g-12006191",
    "https://domicilios.tiendasd1.com/p/queso-mozzarella-tajado-x-250g-latti-12006207",
    "https://domicilios.tiendasd1.com/p/quesito-alpina-185-g-12002456",
    "https://domicilios.tiendasd1.com/p/azucar-blanca-1000-grs-12000249",
    "https://domicilios.tiendasd1.com/p/azucar-morena-1000-grs-12000250",
    "https://domicilios.tiendasd1.com/p/endulzante-con-stevia-natri-180-g-12002470"
]


def buscar_nombre_d1(soup):
    # El nombre aparece en <h1> después de "Nombre del producto: ..."
    h1s = soup.find_all('h1')
    for h1 in h1s:
        txt = h1.get_text(strip=True)
        if "Nombre del producto" in txt or "Nombre del Producto" in txt or "Producto:" in txt:
            return txt
    # Alternativa: usa <title> si no encuentra nombre
    title = soup.find('title')
    if title:
        return title.get_text(strip=True)
    return None

def buscar_precio_d1(soup):
    # Busca el precio en <p class="DetailBasePrice__DetailBasePriceStyles...">
    price_tag = soup.find('p', class_=re.compile(r'base__price'))
    if price_tag:
        text = price_tag.get_text(strip=True)
        price = re.sub(r'[^\d,]', '', text).replace(',', '.')
        try:
            return float(price)
        except:
            pass
    return None

def buscar_descripcion_d1(soup):
    # Busca el contenedor de descripción según tu imagen
    desc_container = soup.find('div', class_=re.compile(r'product-detail__description'))
    if desc_container:
        # Busca los <p> con suficiente texto descriptivo
        p_tags = desc_container.find_all('p')
        for p in p_tags:
            txt = p.get_text(strip=True)
            # Puedes ajustar el largo mínimo aquí si necesitas
            if txt and len(txt) > 30:
                return txt
    # Alternativa: meta description
    meta_desc = soup.find('meta', {'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        return meta_desc['content']
    return None

def extraer_unidad(nombre, descripcion):
    patrones = [
        r'(\d+\.?\d*)\s*(und|kg|gr|g|ml|l|unidades?)',
        r'x\s*(\d+\.?\d*)\s*(und|kg|gr|g|ml|l|unidades?)'
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
    try:
        precio = float(str(precio).replace(',', '').replace(' ', ''))
    except Exception:
        return None
    match = re.search(r'(\d+\.?\d*)\s?(und|kg|gr|g|ml|l|unidades?)', str(unidad), re.IGNORECASE)
    if match:
        cantidad = float(match.group(1).replace(',', '.'))
        tipo = match.group(2).lower()
        if cantidad != 0:
            precio_unidad = precio / cantidad
            return f"{precio_unidad:.2f}/{tipo}"
    return None

def parse_d1(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    nombre = buscar_nombre_d1(soup)
    precio = buscar_precio_d1(soup)
    descripcion = buscar_descripcion_d1(soup)
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

# --- Configuración de Selenium ---
options = Options()
options.add_argument("--headless=new")
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(options=options)

resultados = []
for url in urlsaScrapear:
    print(f"Procesando: {url}")
    driver.get(url)
    time.sleep(6)  # Puedes ajustar el tiempo si la página carga lento
    html = driver.page_source
    data = parse_d1(html, url)
    resultados.append(data)

driver.quit()

df = pd.DataFrame(resultados)
df.to_csv("datos_estructurados_tiendasd1.csv", index=False, encoding='utf-8')
print("¡Datos guardados exitosamente en 'datos_estructurados_tiendasd1.csv'!")
