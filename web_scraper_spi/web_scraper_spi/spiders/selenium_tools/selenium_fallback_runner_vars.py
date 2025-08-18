import sys
import os
import time
import json
from bs4 import BeautifulSoup
from seleniumbase import SB
from urllib.parse import urlparse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))
from captcha import captcha
import hashlib
from urllib.parse import urlparse, unquote

url = sys.argv[1]
captcha_tipo = sys.argv[2]
project_dir = sys.argv[3]


selectors = {
    "wise.com":[""],
    "tradingeconomics.com":["td.datatable-item"],
    "www.mataf.net":["select#convFrom"]
}


def _safe_filename_from_url(url: str, ext=".txt"):
        """Genera un nombre estable y único a partir de la URL."""
        u = urlparse(url)
        # basename del path (sin / final)
        base = os.path.basename(u.path.rstrip("/"))
        base = unquote(base) or "index"
        # agrega hash corto para distinguir querystrings
        h = hashlib.md5(url.encode("utf-8")).hexdigest()[:8]
        return f"{base}_{h}{ext}"


def guardar_html(contenido, url):
    soup = BeautifulSoup(contenido, 'html.parser')
    body = soup.body

    if body is None:
        return

    for tag in soup(["script", "style", "header", "footer", "nav"]):
        tag.decompose()

    body = soup.body

    for template in body.find_all('template'):
        template.decompose()

    for iframe in body.find_all('iframe'):
        iframe.decompose()

    styles_iconpack_div = body.find('div', id='styles_iconpack')
    if styles_iconpack_div:
        styles_iconpack_div.decompose()

    body = soup.body

    if body:
        raw_text = body.get_text(separator="\n", strip=True)
        # Normaliza espacios duros y colapsa líneas vacías
        lines = [line.replace("\xa0", " ").strip() for line in raw_text.splitlines()]
        texto_limpio = "\n".join([l for l in lines if l])
    else:
        texto_limpio = ""

    output_dir = os.path.join(project_dir, 'extraccion', 'dataset', 'paginas_descargadas_vars')
    os.makedirs(output_dir, exist_ok=True)
    nombre = _safe_filename_from_url(url, ext=".txt")
    filepath = os.path.join(output_dir, nombre)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(texto_limpio)

    print(f"✅ HTML guardado: {filepath} para {url}")



with SB(uc=True) as sb:
    print(f"🔍 Cargando variable: {url} con SB 🔍\n")
    sb.activate_cdp_mode(url)
    sb.uc_gui_click_captcha()
    sb.cdp.sleep(5)


    dominio = urlparse(url).netloc
    vars_selectors = selectors.get(dominio, [])

    status_element = False
    for selector in vars_selectors:
        if(status_element == False):
            try:
                sb.cdp.wait_for_element_visible(selector, timeout=200)
                print(f"✅ Variable detectada en {selector}")
                status_element = True
                break
            except Exception as e:
                print(f"⚠️ No encontrado: {selector} - Posiblemente la pagina cambio o la variable no existe | {e}")
                continue
        else:
            print(f"\n⚠️ Variable no detectada en {selector}, todos los selectores fueron recorridos\n")
            break


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
            resolved_html = captcha.recaptcha(url)
        guardar_html(resolved_html, url)
    else:
        guardar_html(page_source.lower(), url)

