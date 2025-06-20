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
                        partes = linea.strip().split(', ', 1)
                        if not partes or len(partes) < 1:
                            continue
                        url = partes[0].strip()
                        captcha_tipo = partes[1].strip()
                        if url:
                            print(f"⚡ Usando Selenium directo para dinámica: {url}")

                            fake_failure = type('FakeFailure', (), {
                                'request': type('RequestMock', (), {'url': url})(),
                                'captcha_tipo': captcha_tipo
                            })()
                            self.fallback_with_selenium(fake_failure)

            # Procesar URLs estáticas
            if os.path.exists(self.urls_estaticas_file):
                with open(self.urls_estaticas_file, 'r') as f:
                    for linea in f:
                        partes = linea.strip().split(', ', 1)
                        if not partes or len(partes) < 1:
                            continue
                        url = partes[0].strip()
                        captcha_tipo = partes[1].strip()
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
                                dont_filter=True,
                                meta={'captcha_tipo': captcha_tipo}
                            )

        except Exception as e:
            self.logger.error(f"Error procesando URLs: {e}")


    def save_page(self, response):
        if response.status != 200:
            return self.fallback_with_selenium(response)

        body_text = response.text.lower()
        captcha_tipo = response.meta.get('captcha_tipo', 'no')

        if (
            (captcha_tipo == "cloudflare" and ("Verify you are human by completing the action below." or "checking your browser before accessing" or "verify you are human by completing the action below." or "Verify you are human" or "verify you are human" or "verifica que eres humano" or "confirma que eres humano" or "Verificando tu navegador antes de") in body_text)
            or (captcha_tipo == "recaptcha" and ("recaptcha" or "I'm not a robot" or "i'm not a robot" or "No soy un robot" or "no soy un robot") in body_text)
            or "mantén presionado el botón" in body_text
            or "verifica tu identidad" in body_text
        ):
            print(f"⚠️⚠️ Captcha detectado ({captcha_tipo}) en Scrapy. Usando Selenium como fallback... ⚠️⚠️")

            fake_failure = type('FakeFailure', (), {
                'request': type('RequestMock', (), {'url': response.url})(),
                'captcha_tipo': captcha_tipo
            })()

            return self.fallback_with_selenium(fake_failure)

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
            captcha_tipo = getattr(failure, 'captcha_tipo', 'no')
        elif hasattr(failure, 'value') and hasattr(failure.value, 'response'):
            url = failure.value.response.url
            captcha_tipo = 'no' #default
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

            time.sleep(random.uniform(2.0, 4.5))

            actions = ActionChains(driver)
            actions.move_by_offset(random.randint(100, 400), random.randint(100, 400)).perform()
            time.sleep(random.uniform(0.5, 1.2))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.25);")
            time.sleep(random.uniform(0.8, 1.5))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5);")
            time.sleep(random.uniform(0.5, 1.2))
            driver.execute_script("window.scrollTo(0, 0);")

            page_source = driver.page_source.lower()

            if captcha_tipo == "cloudflare" and ("Verify you are human by completing the action below." or "checking your browser before accessing" or "verify you are human by completing the action below." or "Verify you are human" or "verify you are human" or "verifica que eres humano" or "confirma que eres humano" or "Verificando tu navegador antes de") in page_source:
                print("⚠️⚠️ Captcha Cloudflare detectado! ⚠️⚠️")
                # aquí podrías intentar resolver o esperar más

            elif captcha_tipo == "recaptcha" and ("recaptcha" or "I'm not a robot" or "i'm not a robot" or "No soy un robot" or "no soy un robot") in page_source:
                print("⚠️⚠️ Captcha reCAPTCHA detectado! ⚠️⚠️")
                # aquí podrías integrar resolución si es necesario

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception as e:
                print("Timeout esperando el <body>")

            time.sleep(random.uniform(2.0, 4.5))

            # captcha_indicators = [
            #     "mantén presionado el botón",
            #     "captcha",
            #     "verifica tu identidad",
            #     "verifica",
            #     "mantén"
            # ]

            # if any(word in driver.page_source.lower() for word in captcha_indicators):
            #     print("⚠️ Captcha detectado. Intentando resolver", self.counter, "con Selenium...", url)
            #     self.captcha_identification(driver, url)


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

        for script in body.find_all('script'):
            script.decompose()

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
