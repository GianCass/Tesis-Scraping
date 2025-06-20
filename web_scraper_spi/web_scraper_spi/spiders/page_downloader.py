import scrapy
from scrapy.http import Request
import os
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

from selenium.webdriver.common.action_chains import ActionChains


class PageDownloaderSpider(scrapy.Spider):
    name = 'page_downloader'

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
    ]

    def estructura_incompleta(response):
        esperado = ['div#main-content', "div.render-container", 'div.product-list', 'script[type="application/ld+json"]']
        for selector in esperado:
            if not response.css(selector):
                return True
        return False

    def contenido_muy_corto(response):
        return len(response.text) < 10000

    def pagina_con_render_dinamico(response):
        texto = response.text.lower()
        patrones = [
            "enable javascript",
            "please wait",
            "verifying browser",
            "cloudflare",
            "press and hold",
            "checking your browser before accessing"
        ]
        return any(p in texto for p in patrones)






    def captcha_identification(self, driver, url):
        domain = urlparse(url).netloc.lower()

        if "super.walmart.com.mx" in domain or "walmart.com.mx" in domain:
            self.resolver_captcha_wallmartmx(driver)
        elif "amazon" in domain:
            print("else")
        else:
            print("⚠️ No hay función específica para resolver captcha de:", domain)




    def __init__(self, *args, **kwargs):
        super(PageDownloaderSpider, self).__init__(*args, **kwargs)
        self.counter = 1
        self.project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        self.urls_dinamicas_file = os.path.join(self.project_dir, 'dataset', 'datos_extraidos', 'dinamicas.txt')
        self.urls_estaticas_file = os.path.join(self.project_dir, 'dataset', 'datos_extraidos', 'estaticas.txt')


    def start_requests(self):
        try:
            if os.path.exists(self.urls_dinamicas_file):
                with open(self.urls_dinamicas_file, 'r') as f:
                    for linea in f:
                        partes = linea.strip().split(',')
                        if not partes or len(partes) < 1:
                            continue
                        url = partes[0].strip()
                        if url:
                            print(f"⚡ Usando Selenium directo para dinámica: {url}")

                            # Simulamos un objeto de tipo `failure` como el que recibiría `errback`
                            fake_failure = type('FakeFailure', (), {
                                'request': type('RequestMock', (), {'url': url})()
                            })()
                            self.fallback_with_selenium(fake_failure)

            # Procesar URLs estáticas
            if os.path.exists(self.urls_estaticas_file):
                with open(self.urls_estaticas_file, 'r') as f:
                    for linea in f:
                        partes = linea.strip().split(',')
                        if not partes or len(partes) < 1:
                            continue
                        url = partes[0].strip()
                        if url:
                            print(f"🌐 Usando Scrapy para estática: {url}")
                            headers = {
                                'User-Agent': random.choice(self.USER_AGENTS),
                                'Accept-Language': 'en-US,en;q=0.9',
                                'Accept-Encoding': 'gzip, deflate, br',
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                'Connection': 'keep-alive',
                                'Upgrade-Insecure-Requests': '1'
                            }

                            yield Request(
                                url=url,
                                callback=self.save_page,
                                errback=self.fallback_with_selenium,
                                headers=headers,
                                dont_filter=True
                            )

        except Exception as e:
            self.logger.error(f"Error procesando URLs: {e}")


    def save_page(self, response):
        if response.status != 200:
            return self.fallback_with_selenium(response)

        body_text = response.text.lower()

        if "mantén presionado el botón" in body_text or "verifica tu identidad" in body_text:
            print("⚠️ Captcha detectado en Scrapy. Usando Selenium como fallback...")
            return self.fallback_with_selenium(response)

        self._guardar_html(response.body)



    def necesita_selenium(self, response):
        return (
            self.estructura_incompleta(response) or
            self.contenido_muy_corto(response) or
            self.pagina_con_render_dinamico(response)
        )



    def fallback_with_selenium(self, failure):
        if hasattr(failure, 'request'):
            url = failure.request.url
        elif hasattr(failure, 'value') and hasattr(failure.value, 'response'):
            url = failure.value.response.url
        else:
            self.logger.error("Error desconocido en fallback.")
            return

        self.logger.warning(f"Selenium usándose como fallback para: {url}")

        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            user_agent = random.choice(self.USER_AGENTS)
            options.add_argument(f'user-agent={user_agent}')

            driver = webdriver.Chrome(options=options)

            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                """
            })

            print(f"Cargando con Selenium: {url}")
            driver.get(url)

            actions = ActionChains(driver)
            actions.move_by_offset(random.randint(100, 400), random.randint(100, 400)).perform()
            time.sleep(random.uniform(0.5, 1.2))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.25);")
            time.sleep(random.uniform(0.8, 1.5))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5);")
            time.sleep(random.uniform(0.5, 1.2))
            driver.execute_script("window.scrollTo(0, 0);")

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception as e:
                print("Timeout esperando el <body>")

            time.sleep(random.uniform(2.0, 4.5))

            captcha_indicators = [
                "mantén presionado el botón",
                "captcha",
                "verifica tu identidad",
                "verifica",
                "mantén"
            ]

            if any(word in driver.page_source.lower() for word in captcha_indicators):
                print("⚠️ Captcha detectado. Intentando resolver", self.counter, "con Selenium...", url)
                self.captcha_identification(driver, url)


            page_source = driver.page_source
            driver.quit()

            self._guardar_html(page_source.encode('utf-8'))

        except WebDriverException as e:
            self.logger.error(f"Selenium falló al descargar {url}: {e}")


    def _guardar_html(self, contenido):
        soup = BeautifulSoup(contenido, 'html.parser')
        body = soup.body

        if body is None:
            self.logger.warning("No se encontró <body> en el HTML.")
            return

        # Eliminar todos los <script> del <body>
        for script in body.find_all('script'):
            script.decompose()

        # Eliminar el div con id="styles_iconpack" si existe
        styles_iconpack_div = body.find('div', id='styles_iconpack')
        if styles_iconpack_div:
            styles_iconpack_div.decompose()

        output_dir = os.path.join(self.project_dir, 'extraccion', 'dataset', 'paginas_descargadas')
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{self.counter}.html"
        self.counter += 1
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(body))

        self.logger.info(f"Guardado solo <body> para {self.counter}: {filepath}\n\n\n\n\n")
