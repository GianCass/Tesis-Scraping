from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# URLs a scrapear
urls_a_scrapear = [
    "https://www.alvi.cl/product/cafe-instantaneo-tradicion-lata-2",
    "https://www.alvi.cl/product/cafe-instantaneo-institucional",
    "https://www.alvi.cl/product/cafe-instantaneo-clasico-lata",
    "https://www.alvi.cl/product/cafe-liofilizado-frasco",
    "https://www.alvi.cl/product/papa-duquesa-cong-frutos-del-maipo-1-kg",
    "https://www.alvi.cl/product/pan-molde-blanco-amada-masa-500-gr",
    "https://www.alvi.cl/product/pan-molde-integral-xl-ideal-750gr",
    "https://www.alvi.cl/product/pan-molde-blanco-xl-cena-740-gr",
    "https://www.alvi.cl/product/pan-molde-sandw-blanco-guillermina-800-g",
    "https://www.alvi.cl/product/pan-integral-bauducco-390gr",
    "https://www.alvi.cl/product/bebida-original-desechable",
    "https://www.alvi.cl/product/bebida-desechable-9",
    "https://www.alvi.cl/product/bebida-desechable-29",
    "https://www.alvi.cl/product/bebida-desechable-6",
    "https://www.alvi.cl/product/bebida-desechable-4",
    "https://www.alvi.cl/product/arroz-g2-grano-largo-ancho-bolsa",
    "https://www.alvi.cl/product/arroz-g2-gran-seleccion-largo",
    "https://www.alvi.cl/product/arroz-largo-delgado-grado-2",
    "https://www.alvi.cl/product/arroz-g1-largo-ancho-bolsa",
    "https://www.alvi.cl/product/arroz-g2-largo-delgado-aruba-900-gr",
    "https://www.alvi.cl/product/huevos-blanco-grande",
    "https://www.alvi.cl/product/huevos-grande-blanco",
    "https://www.alvi.cl/product/huevo-primera-color-la-herradura-30-un",
    "https://www.alvi.cl/product/pechuga-deshuesada-pollo-iqf",
    "https://www.alvi.cl/product/pechuga-deshuesada-congelada",
    "https://www.alvi.cl/product/leche-entera-natural-sin-tapa",
    "https://www.alvi.cl/product/leche-entera-natural-2",
    "https://www.alvi.cl/product/leche-entera-tetra-los-peumos-1lt",
    "https://www.alvi.cl/product/leche-entera-natural-3",
    "https://www.alvi.cl/product/leche-entera-sin-lactosa-con-tapa",
    "https://www.alvi.cl/product/cerveza-extra-botella",
    "https://www.alvi.cl/product/cerveza-budweiser-473-cc-lata",
    "https://www.alvi.cl/product/cerveza-botella",
    "https://www.alvi.cl/product/cerveza-stella-artois-330-cc-bot-2",
    "https://www.alvi.cl/product/cerveza-royal-guard-470-cc-lata",
    "https://www.alvi.cl/product/pasta-spaghetti-n-5-3",
    "https://www.alvi.cl/product/pasta-spaghetti-n-5-2",
    "https://www.alvi.cl/product/pasta-spaghetti-n-5-al-huevo",
    "https://www.alvi.cl/product/pasta-spaghetti-n-5-4",
    "https://www.alvi.cl/product/pasta-spaghetti-integral"
]

def buscar_precio(soup):
    # Busca precio principal en <span> o <p> con símbolo $
    precio_tag = soup.find(lambda tag: tag.name in ['span', 'p'] and tag.get_text().strip().startswith('$'))
    if precio_tag:
        precio_text = precio_tag.get_text().replace('$', '').replace('.', '').replace(',', '.').strip()
        try:
            return float(precio_text)
        except:
            return None
    return None

def buscar_nombre(soup):
    tag = soup.find('title')
    if tag:
        return tag.get_text().replace("| Alvi", "").strip()
    tag = soup.find('h1')
    if tag:
        return tag.get_text().strip()
    return None

def buscar_descripcion(soup):
    # Busca todos los <p> con clases que suelen tener la descripción y filtra por texto útil
    for p in soup.find_all('p', class_=re.compile(r'Text_text')):
        class_str = ' '.join(p.get('class', []))
        if "regular__KSs6J" in class_str and "lg__GZWsa" in class_str:
            txt = p.get_text(strip=True)
            if txt and txt.lower() not in ['categorías', 'productos relacionados', ''] and len(txt) > 10:
                return txt
    # Si no encontró nada, intenta devolver el primer <p> "largo" que no sea genérico
    for p in soup.find_all('p'):
        txt = p.get_text(strip=True)
        if txt and txt.lower() not in ['categorías', 'productos relacionados', ''] and len(txt) > 10:
            return txt
    return ""

def buscar_unidad(soup):
    # --- NO CAMBIAR ESTA LÓGICA ---
    p_unidad = soup.find('p', class_=lambda c: c and "Text_text--sm_KnF3l" in c and "Text_text--gray__r4RdT" in c)
    if p_unidad:
        return p_unidad.get_text(strip=True)
    for p in soup.find_all('p'):
        texto = p.get_text(strip=True)
        if re.search(r"\d+\s?(g|kg|ml|l|gr)", texto.lower()):
            return texto
    return ""

def calcular_precio_por_unidad(precio, unidad):
    # --- NO CAMBIAR ESTA LÓGICA ---
    if not precio or not unidad:
        return ""
    match = re.search(r"(\d+(?:[\.,]\d+)?)\s?(kg|g|ml|l|gr)", unidad.lower())
    if match:
        cantidad = float(match.group(1).replace(",", "."))
        tipo = match.group(2)
        # Ajusta a gramos si está en kg
        if tipo == 'kg':
            cantidad *= 1000
            tipo = 'g'
        elif tipo == 'l':
            cantidad *= 1000
            tipo = 'ml'
        if cantidad > 0:
            precio_unidad = precio / cantidad
            return f"{precio_unidad:.2f}/{tipo}"
    return ""

# --- Configuración de Selenium ---
options = Options()
options.add_argument("--headless=new")
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(options=options)

resultados = []
for url in urls_a_scrapear:
    print(f"Procesando: {url}")
    driver.get(url)
    time.sleep(4)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    nombre = buscar_nombre(soup)
    precio = buscar_precio(soup)
    descripcion = buscar_descripcion(soup)
    unidad = buscar_unidad(soup)
    precio_unidad = calcular_precio_por_unidad(precio, unidad)

    print("Nombre:", nombre)
    print("Precio:", precio)
    print("Descripción:", descripcion)
    print("Unidad:", unidad)
    print("Precio por unidad:", precio_unidad)
    print("-" * 50)

    resultados.append({
        "url": url,
        "nombre": nombre if nombre else "",
        "precio": precio if precio else "",
        "descripcion": descripcion if descripcion else "",
        "unidad": unidad if unidad else "",
        "precio_unidad": precio_unidad if precio_unidad else ""
    })

driver.quit()

df = pd.DataFrame(resultados)
df.to_csv("datos_estructurados_alvi.csv", index=False, encoding='utf-8')
print("¡Datos guardados en 'datos_estructurados_alvi.csv'!")
