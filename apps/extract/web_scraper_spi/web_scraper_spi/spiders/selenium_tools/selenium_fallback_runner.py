import sys
import os
import time
import json
from bs4 import BeautifulSoup
from seleniumbase import SB
from urllib.parse import urlparse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))
from captcha import captcha

url = sys.argv[1]
captcha_tipo = sys.argv[2]
counter = sys.argv[3]
project_dir = sys.argv[4]


selectors = {
    "www.heb.com.mx": ["div.price"],
    "www.lacomer.com.mx": ["span.txt-whitout-line.ng-binding"],
    "www.carrefour.com.ar": ["span.valtech-carrefourar-product-price-0-x-sellingPriceValue"],
    "www.cotodigital.com.ar": ["var.price.h3.ng-star-inserted"],
    "domicilios.tiendasd1.com": ["p.base__price"],
    "www.jumbo.cl": ["div.sticky-product-prices"],
    "www.alvi.cl": ["body:contains('Sku:')"],  # texto especial
    "www.wong.pe": ["span.vtex-product-price-1-x-currencyContainer"],
    "www.obahortifruti.com.br": ["section.section-breadcrumb"], # EN VEZ DE SUPERMUFFATO
    "www.extramercado.com.br": ["body:contains('Preço')"], # EN VEZ DE BRETA - texto especial
    "www.realonline.com.py": ["p.base__price"], # EN VEZ DE SALEMMAONLINE
    "www.hiperlibertad.com.ar": ["span.vtex-product-price-1-x-sellingPriceValue"],
    "www.vivanda.com.pe": ["span.vivanda-product-price-1-x-currencyContainer"],
    "www.peridomicilio.com": ["div.cart__actions__price"],
    "www.megasuper.com": ["div.cart__actions__price"],
    "automercado.cr": ["h1.product-detail__data--title"],
    "www.smrey.com": ["div.cart__actions__price"],
    "www.pricesmart.com": ["span.sf-price__regular"],
    "biggie.com.py": ["p.priceArticle"],
    "www.chedraui.com.mx": ["span.chedrauimx-add-to-cart-button-0-x-currencyContainer"],
    "www.alsuper.com": ["div.as-price-container"],
    "mercado.carrefour.com.br": ["span.text-pdp-price"],
    "www.paodeacucar.com": [".ComparativePrice-sc-"],  # fragmento de clase
    "www.zaffari.com.br": ["span.zaffarilab-zaffari-produto-1-x-ProductPriceSellingPriceValue"],
    "www.jumbo.com.ar": ["div.vtex-price-format-gallery"],
    "diaonline.supermercadosdia.com.ar": ["span.diaio-store-5-x-sellingPriceValue"],
    "www.exito.com": ["body:contains('Otros')"],  # texto
    "www.jumbocolombia.com": ["div.tiendasjumboqaio-jumbo-minicart-2-x-price"],
    "www.olimpica.com": ["span.olimpica-dinamic-flags-0-x-currencyContainer"],
    "www.carulla.com": ["body:contains('Und')"],  # texto especial
    "www.unimarc.cl": ["body:contains('Sku:')"],
    "www.tottus.cl": ["div.prices"],
    "www.plazavea.com.pe": ["div.ProductCard__content__price"],
    "www.metro.pe": ["span.metroio-metroiocompo1app-0-x-currencyContainer"],
    "www.makro.plazavea.com.pe": ["div.MakroPriceTable"],
    "www.supermaxi.com": ["h5.cf_api_regular_price"],
    "www.frecuento.com": ["h4.ps-product__price"],
    "coralhipermercados.com": ["span.price"],
    "www.tia.com.ec": ["span.price"],
    "www.supermercadosantamaria.com": ["div.wrapp-detalle-precio"],
    "www.masxmenos.cr": ["span.vtex-store-components-3-x-currencyContainer"],
    "www.super99.com": ["span.price"],
    "www.superxtra.com": ["div.superxtrapanama-home-categories-0-x-custom-product-selling-price"],
    "www.ribasmith.com": ["span.price"],
    "www.casarica.com.py": ["span#producto-precio"],
    "www.stock.com.py": ["span.productPrice"],
    "www.superseis.com.py": ["span.productPrice"],
    "www.maxipali.co.cr": ["span.vtex-store-components-3-x-currencyContainer"], # PERSONALIZAR - DONE
    "despensa.bodegaaurrera.com.mx": ["h1#main-title"], # PERSONALIZAR - DONE
    "www.lider.cl": ["span.pdp-mobile-sales-price"],
}




# def obtener_status_code(sb, target_url):
#     try:
#         logs = sb.driver.get_log("performance")
#         for entry in logs:
#             log = json.loads(entry["message"])["message"]
#             if log["method"] == "Network.responseReceived":
#                 response = log["params"]["response"]
#                 if target_url in response["url"]:
#                     return response["status"]
#     except Exception as e:
#         print(f"Error obteniendo status code: {e}")
#     return 200


def guardar_html(contenido):
    soup = BeautifulSoup(contenido, 'html.parser')
    body = soup.body
    if body is None:
        print("No se encontró <body>.")
        return
    for script in body.find_all('script'):
            script.decompose()

    for template in body.find_all('template'):
            template.decompose()

    for style in body.find_all('style'):
        style.decompose()

    for iframe in body.find_all('iframe'):
        iframe.decompose()

    styles_iconpack_div = body.find('div', id='styles_iconpack')
    if styles_iconpack_div:
        styles_iconpack_div.decompose()

    output_dir = os.path.join(project_dir, 'extraccion', 'dataset', 'paginas_descargadas')
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{counter}.html"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(body))

    print(f"✅ HTML guardado: {filepath} para {url}")



with SB(uc=True) as sb:
    print(f"🔍 Cargando: {url} con SB 🔍\n")
    sb.activate_cdp_mode(url)
    sb.uc_gui_click_captcha()
    sb.cdp.sleep(5)


    dominio = urlparse(url).netloc
    price_selectors = selectors.get(dominio, [])

    if (dominio == "www.maxipali.co.cr"):
         print("Contenido visible detras el banner, si es que aparecio")
    elif (dominio == "despensa.bodegaaurrera.com.mx"):
         print("Contenido visible detras el banner, si es que aparecio")


    # Espera por precio dinámico => Pagina cargada completamente - DONE
    for selector in price_selectors:
        try:
            sb.cdp.wait_for_element_visible(selector, timeout=200)
            print(f"✅ Precio detectado en {selector}")
            break
        except Exception as e:
            print(f"⚠️ No encontrado: {selector} - Posiblemente la pagina cambio o el producto no existe | {e}")
            continue


    # HTML de la pagina - DONE
    page_source = sb.cdp.get_page_source()


    status_captcha = False
    tipo_captcha_detectado = "no"



    # 1) Cloudflare
    cloudflare_selectors = [
        "#challenge-form",
        "#cf-content",
        "#cf-turnstile",
        ".challenge-form",
        ".cf-browser-verification",
    ]


    # 2) reCAPTCHA v2 / v3 / invisible
    recaptcha_selectors = [
        "div.g-recaptcha",
        "div.recaptcha-checkbox",  # checkbox visible en v2
        ".grecaptcha-badge",  # visible en invisible v3
    ]

    # use SB instead of simple search - DONE
    if captcha_tipo == "recaptcha" or captcha_tipo == "no":
        for selector in recaptcha_selectors:
            if sb.cdp.is_element_visible(selector):
                print("⚠️ reCAPTCHA visible ⚠️")
                status_captcha = True
                tipo_captcha_detectado = "recaptcha"
                break

    if captcha_tipo == "cloudflare" or captcha_tipo == "no":
        for selector in cloudflare_selectors:
            if sb.cdp.is_element_visible(selector):
                print("⚠️ Cloudflare visible ⚠️")
                status_captcha = True
                tipo_captcha_detectado = "cloudflare"
                break



    print("\nEl estado de captcha para " + url + "es: " + str(status_captcha))


    # resolver captchas al detectar con solve capthca de SB, sino con metodos creados previamente - DONE
    if(status_captcha):
        if (tipo_captcha_detectado == "cloudflare"):
            try:
                sb.uc_gui_click_captcha()
                resolved_html = sb.cdp.get_page_source()
            except Exception as e:
                print("UC_GUI_CLICK_CAPTCHA de SB no pudo pasar el captcha Cloudflare. Intentando con Captcha Solver\n")
                resolved_html = captcha.cloudflare(url)
        elif (tipo_captcha_detectado == "recaptcha"):
            try:
                sb.uc_gui_click_captcha()
                resolved_html = sb.cdp.get_page_source()
            except Exception as e:
                print("UC_GUI_CLICK_CAPTCHA de SB no pudo pasar el captcha reCAPTCHA. Intentando con Captcha Solver\n")
                resolved_html = captcha.recaptcha(url)
        guardar_html(resolved_html)
    else:
        guardar_html(page_source.lower())

