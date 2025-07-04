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


import undetected_chromedriver as uc
from undetected_chromedriver import Chrome, ChromeOptions
import pickle


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from captcha import captcha


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

        status_captcha, tipo = self.detectar_captcha(body_text, response.url, captcha_tipo, response.status)

        if(status_captcha == True):
            print(f"⚠️⚠️ Captcha detectado ({tipo}) en Scrapy. Usando Selenium como fallback... ⚠️⚠️")

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


    def esperar_carga_completa(driver, timeout=45):
        print("Cargando completamente la página web...\n\n\n")
        try:
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )

            body_elem = driver.find_element(By.TAG_NAME, 'body')
            body_text = body_elem.text.strip()

            if len(body_text) < 100:
                print("Contenido insuficiente en <body>")
                return False

            currency_symbols = ['$', '€', '£', '₽', '¥', '₩', '฿']
            if not any(symbol in body_text for symbol in currency_symbols):
                print("\nNo se encontró ningún símbolo de moneda en el texto del body. (no se cargo completamente)\n")
                return False

            elementos = driver.find_elements(By.XPATH, '//*')
            tiene_price = False
            for el in elementos:
                clase = el.get_attribute('class') or ''
                texto = el.text or ''
                # tiene que haber por lo menos un elemento que diga precio en su clase o texto para confirmar que la pagina se cargo completamente
                if 'price' in clase.lower() or 'precio' in clase.lower() or 'preço' in clase.lower() or \
                'price' in texto.lower() or 'precio' in texto.lower() or 'preço' in texto.lower():
                    tiene_price = True
                    break

            if not tiene_price:
                print("\nNo se encontró ningún elemento con 'price' o 'precio' en clases o texto. (no se cargo completamente)\n")
                return False

            return True

        except Exception as e:
            print(f"Error durante la espera: {e}")
            return False


    def obtener_status_code(driver, target_url):
        try:
            logs = driver.get_log("performance")
            for entry in logs:
                log = json.loads(entry["message"])["message"]
                if log["method"] == "Network.responseReceived":
                    response = log["params"]["response"]
                    url = response["url"]
                    if target_url in url:
                        return response["status"]
        except Exception as e:
            print(f"Error al obtener status_code: {e}")
        return 200



    def detectar_captcha(page_source, url, captcha_tipo="no", status_code=200):
        soup = BeautifulSoup(page_source, 'html.parser')
        visible_text = soup.get_text(separator=' ', strip=True).lower()

        print("Detectando captcha para " + url)

        # 1. Cloudflare
        cloudflare_keywords = [
            "checking your browser", "checking your browser before accessing", "verificando tu navegador antes de acceder", "verificando tu navegador",
            "ddos protection", "ddos protection by cloudflare", "cloudflare ray id", "cloudflare security", "checking if the site connection is secure", "browser challenge", "security check", "please enable cookies and reload the page",
        ]

        cloudflare_selectors = [
            '#challenge-form',
            '#cf-content',
            '.challenge-form',
            '.cf-content'
            '.cf-browser-verification',
            '.cf-error-overview',
            '[data-ray]'
        ]

        # Señales Cloudflare
        is_cloudflare = (
            status_code in [503, 403, 429] or
            any(kw in visible_text for kw in cloudflare_keywords) or
            any(soup.select(selector) for selector in cloudflare_selectors) or
            'cloudflare' in visible_text and any(word in visible_text for word in ['challenge', 'verification', 'checking'])
        )



        # 2. reCAPTCHA
        recaptcha_indicators = {
            'selectors': [
                "div.g-recaptcha",
                "div.recaptcha",
                "iframe[src*='google.com/recaptcha']",
                "script[src*='google.com/recaptcha']",
                ".g-recaptcha-response",
                "[data-sitekey]"  # reCAPTCHA site key
            ],
            'text_patterns': [
                "i'm not a robot",
                "no soy un robot",
                "verify you are human",
                "verifica que eres humano",
                "recaptcha"
            ]
        }

        is_recaptcha = (
            any(soup.select(selector) for selector in recaptcha_indicators['selectors']) or
            any(pattern in visible_text for pattern in recaptcha_indicators['text_patterns'])
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
            # captcha.cloudflare(url)
            return True, "cloudflare"

        elif captcha_tipo == "recaptcha" and is_recaptcha:
            print("⚠️ Captcha reCAPTCHA detectado! ⚠️")
            # captcha.recaptcha(url)
            return True, "recaptcha"

        elif captcha_tipo == "no":
            if is_cloudflare:
                print("⚠️⚠️ Captcha Cloudflare detectado automáticamente! ⚠️⚠️")
                # captcha.cloudflare(url)
                return True, "cloudflare"
            elif is_recaptcha:
                print("⚠️⚠️ Captcha reCAPTCHA detectado automáticamente! ⚠️⚠️")
                # captcha.recaptcha(url)
                return True, "recaptcha"

        return False, "no"







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

        driver = None

        try:
            options = uc.ChromeOptions()
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

            options.add_argument('--disable-blink-features=AutomationControlled')

            # options.add_argument("--headless=new")
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-extensions")

            user_agent = random.choice(self.USER_AGENTS)
            options.add_argument(f'user-agent={user_agent}')

            caps = DesiredCapabilities.CHROME.copy()
            caps["goog:loggingPrefs"] = {"performance": "ALL"}

            options.add_experimental_option("prefs", {
                "profile.managed_default_content_settings.images": 2,
                "profile.managed_default_content_settings.stylesheets": 2,
                "profile.managed_default_content_settings.fonts": 2,
                "profile.managed_default_content_settings.plugins": 2
            })

            # Driver con Undetected Chromedriver
            driver = uc.Chrome(use_subprocess=False, options=options)



            print ("Inicio trabajo con Cookies")


            #uiiiauuuiiiiiaaaa
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            domain = parsed_url.netloc.replace("www.", "").replace(".", "_")
            cookies_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'captcha', 'cookies', f"cookies_{domain}.pkl")
            driver.get(base_url)
            time.sleep(2)


            driver.delete_all_cookies()

            if os.path.exists(cookies_path):
                print("🔐 Cargando cookies del archivo:", cookies_path)
                with open(cookies_path, "rb") as f:
                    cookies = pickle.load(f)
                    for cookie in cookies:
                        try:
                            if 'expiry' in cookie:
                                cookie['expiry'] = int(cookie['expiry'])
                            driver.add_cookie(cookie)
                        except Exception as e:
                            print(f"❌ Error al agregar cookie: {e}")



            print(f"Cargando con Selenium: {url}")



            driver.get(url)

            # carga completa de la pagina
            status = False
            for intento in range(3):
                status = self.esperar_carga_completa(driver)
                if status:
                    break
                print(f"Intento {intento + 1} fallido. Reintentando en 10 segundos...")
                time.sleep(10)

            if not status:
                print("La página no se cargó completamente después de 3 intentos.")


            time.sleep(random.uniform(2.0, 4.5))


            driver.execute_script("window.scrollBy(0, 150)")
            time.sleep(random.uniform(0.3, 1.5))

            action = ActionChains(driver)
            action.move_by_offset(random.randint(10, 200), random.randint(10, 200)).perform()
            time.sleep(random.uniform(0.5, 1.5))

            time.sleep(10)


            page_source = driver.page_source.lower()

            # obtener el status code para detectar cloudflare
            status_code = self.obtener_status_code(driver, url)

            # verificar si hay captcha y llamar funciones para solucionarlas
            status_captcha, captcha_tipo_detected = self.detectar_captcha(page_source, url, captcha_tipo, status_code)
            print("\nEl estado de captcha para " + url + "es: " + status_captcha)
            if(status_captcha):
                if (captcha_tipo_detected == "cloudfare"):
                    resolved_html = captcha.cloudflare(url)
                elif (captcha_tipo_detected == "recaptcha"):
                    resolved_html = captcha.recaptcha(url)
                self.guardar_html(resolved_html.encode("utf-8"))
                driver.quit()
                return



            # carga completa de la pagina
            # status = False
            # for intento in range(3):
            #     status = self.esperar_carga_completa(driver)
            #     if status:
            #         break
            #     print(f"Intento {intento + 1} fallido. Reintentando en 10 segundos...")
            #     time.sleep(10)

            # if not status:
            #     print("La página no se cargó completamente después de 3 intentos.")

            # time.sleep(random.uniform(2.0, 4.5))

            page_source = driver.page_source
            driver.quit()

            self.guardar_html(page_source.encode('utf-8'))

        except WebDriverException as e:
            self.logger.error(f"Selenium falló al descargar {url}: {e}")
        finally:
            if driver:
                driver.quit()


    def guardar_html(self, contenido):
        soup = BeautifulSoup(contenido, 'html.parser')
        body = soup.body

        if body is None:
            self.logger.warning("No se encontró <body> en el HTML.")
            return

        # Aqui se hace parte de la limpieza de bodies
        for script in body.find_all('script'):
            script.decompose()

        for style in body.find_all('style'):
            style.decompose()

        for iframe in body.find_all('iframe'):
            iframe.decompose()

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

        self.logger.info(f"\n\n\n\n\nGuardado solo <body> para {self.counter - 1}: {filepath}\n\n\n\n\n")
