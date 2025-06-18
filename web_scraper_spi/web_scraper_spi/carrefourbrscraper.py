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
    "https://mercado.carrefour.com.br/arroz-branco-longofino-tipo-1-camil-todo-dia-5kg-115789/p",
    "https://mercado.carrefour.com.br/arroz-solito-tipo-1-5kg-962740/p",
    "https://mercado.carrefour.com.br/arroz-branco-longofino-tipo-1-tio-joao-2kg-115657/p",
    "https://mercado.carrefour.com.br/arroz-bom-no-prato-5-kg-branco-tipo-1-6574050/p",
    "https://mercado.carrefour.com.br/arroz-branco-longofino-tipo-1-graos-selecionados-carrefour-5kg-239887/p",
    "https://mercado.carrefour.com.br/cafe-soluvel-lor-intense-40g-3102343/p",
    "https://mercado.carrefour.com.br/cafe-starbucks-pike-place-roast-torrado-e-moido-250g-5688450/p",
    "https://mercado.carrefour.com.br/cafe-melitta-soluvel-extra-forte-sache-com-40g-5370280/p",
    "https://mercado.carrefour.com.br/cafe-torrado-e-moido-do-ponto-tradicional-vacuo-500-g-4416066/p",
    "https://mercado.carrefour.com.br/cafe-soluvel-tradicional-carrefour-sc-50g-6459153/p",
    "https://mercado.carrefour.com.br/pao-de-forma-panco-premium-500g-241970/p",
    "https://mercado.carrefour.com.br/pao-de-forma-wickbold-5-zeros-viva-integralmente-400g-3148211/p",
    "https://mercado.carrefour.com.br/pao-de-forma-sem-casca-pullman-450g-9767312/p",
    "https://mercado.carrefour.com.br/pao-integral-nutrella-450g-9498370/p",
    "https://mercado.carrefour.com.br/pao-de-forma-seven-boys-450g-1109740/p",
    "https://mercado.carrefour.com.br/refrigerante-cocacola-garrafa-2-l-5761719/p",
    "https://mercado.carrefour.com.br/refrigerante-guarana-antarctica-sem-acucar-garrafa-2l-156205/p",
    "https://mercado.carrefour.com.br/refrigerante-pepsi-black-garrafa-2l-9767339/p",
    "https://mercado.carrefour.com.br/refrigerante-kuat-guarana-2l-673846/p",
    "https://mercado.carrefour.com.br/refrigerante-fanta-laranja-2l-157201/p",
    "https://mercado.carrefour.com.br/macarrao-talharim-camp-oro-grano-duro-500g-9930876/p",
    "https://mercado.carrefour.com.br/macarrao-espaguete-n8-com-ovos-barilla-500g-9289240/p",
    "https://mercado.carrefour.com.br/macarrao-de-semola-com-ovos-fidelinho-10-adria-500g-4235606/p",
    "https://mercado.carrefour.com.br/macarrao-talharim-massa-fresca-leve-500g-366366/p",
    "https://mercado.carrefour.com.br/massa-de-milho-fusilli-sem-gluten-quinoa-6282571/p",
    "https://mercado.carrefour.com.br/leite-integral-uht-italac-1-litro-8819505/p",
    "https://mercado.carrefour.com.br/leite-zero-lactose-semidesnatado-parmalat-zymil-1l-5633672/p",
    "https://mercado.carrefour.com.br/leite-integral-lider-1-l-8150516/p",
    "https://mercado.carrefour.com.br/leite-uht-integral-itambe-caixa-com-tampa-1-l-115517/p",
    "https://mercado.carrefour.com.br/leite-integral-uht-ninho-fortificado-1l-6289258/p",
    "https://mercado.carrefour.com.br/cerveja-heineken-garrafa-600ml-7941234/p",
    "https://mercado.carrefour.com.br/cerveja-lager-premium-puro-malte-stella-artois-330ml-6242740/p",
    "https://mercado.carrefour.com.br/cerveja-brahma-duplo-malte-puro-malte-350ml-lata-6643426/p",
    "https://mercado.carrefour.com.br/cerveja-munich-helles-puro-malte-spaten-garrafa-330ml-3486176/p",
    "https://mercado.carrefour.com.br/cerveja-budweiser-american-lager-330ml-long-neck-5513286/p",
    "https://mercado.carrefour.com.br/frango-inteiro-congelado-temperado-seara-frango-de-padaria-aproximadamente-14-kg-275689/p",
    "https://mercado.carrefour.com.br/file-de-peito-de-frango-congelado-sem-osso-perdigao-1kg-sassami-655007/p",
    "https://mercado.carrefour.com.br/file-de-frango-peito-congelado-sem-osso-sadia-1kg-7087942/p",
    "https://mercado.carrefour.com.br/file-de-peito-de-frango-congelado-korin-boa-pedida-700g-3170586/p",
    "https://mercado.carrefour.com.br/coxinha-da-asa-de-frango-iqf-lar-700g-3438902/p",
    "https://mercado.carrefour.com.br/acucar-cristal-organico-native-1kg-2176556/p",
    "https://mercado.carrefour.com.br/acucar-cristal-caravelas-2kg/p",
    "https://mercado.carrefour.com.br/acucar-refinado-carrefour-1kg-5699614/p",
    "https://mercado.carrefour.com.br/acucar-cristal-organico-itaja-500g-8623848/p",
    "https://mercado.carrefour.com.br/feijao-preto-tipo-1-camil-todo-dia-1-kg-875716/p",
    "https://mercado.carrefour.com.br/feijao-preto-tipo-1-kicaldo-1kg-8160708/p",
    "https://mercado.carrefour.com.br/feijao-preto-carrefour-1-kg-5668255/p",
    "https://mercado.carrefour.com.br/feijao-solito-preto-tipo-1kg-9772561/p",
    "https://mercado.carrefour.com.br/feijao-preto-tipo-1-fantastico-1-kg-4790146/p"
]

def buscar_precio_carrefour(soup):
    # Busca el span con clase "text-pdp-price font-bold text-default"
    precio_tag = soup.find('span', class_=re.compile(r'text-pdp-price'))
    if precio_tag:
        text = precio_tag.get_text(strip=True)
        match = re.search(r'R\$?\s*([\d.,]+)', text)
        if match:
            return float(match.group(1).replace('.', '').replace(',', '.'))
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

def parse_carrefour(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    nombre = buscar_nombre(soup)
    precio = buscar_precio_carrefour(soup)
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
# Puedes usar headless o no-headless según prefieras
# options.add_argument("--headless=new")
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--window-size=1920,1080')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

driver = webdriver.Chrome(options=options)

resultados = []
for url in urlsaScrapear:
    driver.get(url)
    try:
        # Espera a que aparezca el precio en pantalla
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "text-pdp-price"))
        )
    except:
        print(f"No se encontró el precio a tiempo en: {url}")

    time.sleep(3)
    html = driver.page_source
    data = parse_carrefour(html, url)
    resultados.append(data)

driver.quit()

df = pd.DataFrame(resultados)
df.to_csv("datos_estructurados_carrefour_br.csv", index=False, encoding='utf-8')
print("¡Datos guardados exitosamente!")
