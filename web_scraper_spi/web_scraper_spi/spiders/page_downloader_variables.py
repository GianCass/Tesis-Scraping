import scrapy
from scrapy.http import Request
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
import random
import time
import json

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import hashlib
from urllib.parse import urlparse, unquote

import subprocess

import pickle



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


class PageDownloaderVariablesSpider(scrapy.Spider):
    name = 'page_downloader_variables'

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
    ]



    def __init__(self, *args, **kwargs):
        super(PageDownloaderVariablesSpider, self).__init__(*args, **kwargs)
        self.project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        self.urls_dinamicas_file = os.path.join(self.project_dir, 'dataset', 'datos_extraidos_variables', 'dinamicas.txt')
        self.urls_estaticas_file = os.path.join(self.project_dir, 'dataset', 'datos_extraidos_variables', 'estaticas.txt')


    def start_requests(self):
        try:
            if os.path.exists(self.urls_dinamicas_file):
                with open(self.urls_dinamicas_file, 'r') as f:
                    for linea in f:
                        url = linea.strip()
                        if not url:
                            continue
                        self.logger.info(f"⚡ Usando Selenium directo para dinámica: {url}")

                        # Llamada directa al fallback con un "failure" falso que contiene la URL
                        fake_failure = type('FakeFailure', (), {
                            'request': type('RequestMock', (), {'url': url})(),
                            'reason': 'forced-dynamic'
                        })()
                        self.fallback_with_selenium(fake_failure)

            # Procesar URLs estáticas
            if os.path.exists(self.urls_estaticas_file):
                    with open(self.urls_estaticas_file, 'r', encoding='utf-8') as f:
                        for linea in f:
                            url = linea.strip()
                            if not url:
                                continue
                            self.logger.info(f"🌐 Usando Scrapy para estática: {url}")

                            headers = {
                                'User-Agent': random.choice(self.USER_AGENTS),
                                'Accept-Language': 'en-US,en;q=0.9',
                                'Accept-Encoding': 'gzip, deflate, br',
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                'Connection': 'keep-alive',
                                'Upgrade-Insecure-Requests': '1',
                            }

                            yield Request(
                                url=url,
                                callback=self.save_page,              # tu callback para guardar/procesar
                                errback=self.fallback_with_selenium,  # en caso de fallo, intenta Selenium
                                headers=headers,
                                dont_filter=True,
                            )

        except Exception as e:
            self.logger.error(f"Error procesando URLs: {e}")


    def save_page(self, response):
        if response.status != 200:
            return self.fallback_with_selenium(response)

        body_text = response.text.lower()

        status_captcha, tipo = self.detectar_captcha(body_text, response.url, "no")

        if(status_captcha == True):
            print(f"⚠️⚠️ Captcha detectado ({tipo}) en Scrapy. Usando Selenium como fallback... ⚠️⚠️")

            fake_failure = type('FakeFailure', (), {
                'request': type('RequestMock', (), {'url': response.url})(),
            })()

            return self.fallback_with_selenium(fake_failure)

        self.guardar_html(response.body, response.url)





    def detectar_captcha(self, page_source, url, captcha_tipo="no"):
        soup = BeautifulSoup(page_source, 'html.parser')

        print("Detectando captcha para " + url)

        cloudflare_selectors = [
            "#challenge-form",
            "#cf-content",
            ".challenge-form",
            ".cf-browser-verification",
        ]

        # Señales Cloudflare
        # deteccion por texto - eliminada, por temas de falsos positivos. mismo con el status code
        # intentando crear una version correcta que funcione hasta si la pagina tiene Shadow-Root (para cloudflare no hay problema, solo recaptcha)
        # imposible detectar si shadowRoot: closed, continuando normal
        is_cloudflare = (
            any(soup.select(selector) for selector in cloudflare_selectors)
        )


        # 2. reCAPTCHA
        recaptcha_indicators = {
            'selectors': [
                "div.g-recaptcha",
                "div.recaptcha-checkbox",  # checkbox visible en v2
                ".grecaptcha-badge",  # visible en invisible v3
            ],
        }

        is_recaptcha = (
            any(soup.select(selector) for selector in recaptcha_indicators['selectors'])
        )


        def is_element_visible(element):
            if not element:
                return False

            style = element.get('style', '').lower()
            return not any(hidden in style for hidden in [
                'display:none', 'display: none',
                'visibility:hidden', 'visibility: hidden',
                'opacity:0', 'opacity: 0'
            ])


        if is_recaptcha:
            recaptcha_elements = soup.select("div.g-recaptcha, div.recaptcha, .g-recaptcha-response")
            is_recaptcha = any(is_element_visible(elem) for elem in recaptcha_elements) if recaptcha_elements else is_recaptcha


        if captcha_tipo == "cloudflare" and is_cloudflare:
            print("⚠️ Captcha Cloudflare detectado! ⚠️")
            return True, "cloudflare"

        elif captcha_tipo == "recaptcha" and is_recaptcha:
            print("⚠️ Captcha reCAPTCHA detectado! ⚠️")
            return True, "recaptcha"

        elif captcha_tipo == "no":
            if is_cloudflare:
                print("⚠️⚠️ Captcha Cloudflare detectado automáticamente! ⚠️⚠️")
                return True, "cloudflare"
            elif is_recaptcha:
                print("⚠️⚠️ Captcha reCAPTCHA detectado automáticamente! ⚠️⚠️")
                return True, "recaptcha"

        return False, "no"



    def fallback_with_selenium(self, failure):
        if hasattr(failure, 'request'):
            url = failure.request.url
        elif hasattr(failure, 'value') and hasattr(failure.value, 'response'):
            url = failure.value.response.url
        else:
            self.logger.error("Error desconocido en fallback.")
            return

        self.logger.warning(f"Selenium (SeleniumBase) usándose como fallback para variable: {url}")

        if sys.platform.startswith("win"):
            python_cmd = "python"
        else:
            python_cmd = "python3"

        subprocess.run([
            python_cmd, "web_scraper_spi/spiders/selenium_tools/selenium_fallback_runner_vars.py",
            url,
            "no",
            self.project_dir #directorio desde page_downloader.py
        ])

    def _safe_filename_from_url(self, url: str, ext=".txt"):
        """Genera un nombre estable y único a partir de la URL."""
        u = urlparse(url)
        # basename del path (sin / final)
        base = os.path.basename(u.path.rstrip("/"))
        base = unquote(base) or "index"
        # agrega hash corto para distinguir querystrings
        h = hashlib.md5(url.encode("utf-8")).hexdigest()[:8]
        return f"{base}_{h}{ext}"


    def guardar_html(self, contenido, url):
        soup = BeautifulSoup(contenido, 'html.parser')
        body = soup.body

        if body is None:
            self.logger.warning("No se encontró <body> en el HTML.")
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

        output_dir = os.path.join(self.project_dir, 'extraccion', 'dataset', 'paginas_descargadas_vars')
        os.makedirs(output_dir, exist_ok=True)
        nombre = self._safe_filename_from_url(url, ext=".txt")
        filepath = os.path.join(output_dir, nombre)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(texto_limpio)

        self.logger.info(f"\n\n\n\n\nGuardado solo <body> para {nombre}: {filepath}\n\n\n\n\n")
