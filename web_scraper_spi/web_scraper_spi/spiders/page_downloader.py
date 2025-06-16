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



    # def resolver_captcha_wallmartmx(self, driver):
    #     try:
    #         print("🔐 Resolviendo captcha de Walmart MX (versión dinámica)...")

    #         # 1. Esperar a que aparezca el contenedor principal del captcha
    #         WebDriverWait(driver, 15).until(
    #             EC.presence_of_element_located((By.XPATH,
    #                 "//div[@role='button' and .//*[contains(text(), 'Mantén presionado')]]"))
    #         )

    #         # 2. Localizar el botón mediante la combinación de atributos y texto
    #         button = WebDriverWait(driver, 15).until(
    #             EC.element_to_be_clickable((By.XPATH,
    #                 "//div[@role='button' and .//*[contains(text(), 'Mantén presionado')]]//p")))

    #         # 3. Scroll suave al elemento
    #         driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
    #         time.sleep(0.5)

    #         # 4. Acción de mantener presionado con verificación de cambios
    #         action = ActionChains(driver)
    #         action.move_to_element(button).click_and_hold().perform()
    #         print("⏳ Manteniendo presionado el botón...")

    #         # 5. Espera adaptativa con detección de cambios
    #         start_time = time.time()
    #         pressed_successfully = False

    #         while time.time() - start_time < 25:  # Margen de 25 segundos
    #             try:
    #                 # Verificar cambios visuales en el botón
    #                 current_style = button.value_of_css_property("color")
    #                 if "rgb(255, 255, 255)" in current_style:  # Ejemplo de cambio de color
    #                     pressed_successfully = True
    #                     print("✅ Cambio de estilo detectado")
    #                     break

    #                 # Verificar si aparece el checkmark
    #                 checkmark = driver.find_elements(By.XPATH, "//*[local-name()='svg' and .//*[local-name()='path' and contains(@d, 'M9')]]")
    #                 if checkmark:
    #                     pressed_successfully = True
    #                     print("✅ Checkmark detectado")
    #                     break

    #                 time.sleep(0.5)
    #             except:
    #                 time.sleep(0.5)
    #                 continue

    #         # 6. Liberar el botón
    #         action.release().perform()
    #         print("🔄 Botón liberado")

    #         # 7. Verificación final
    #         if not pressed_successfully:
    #             print("⚠️ No se detectaron cambios visuales, pero se completó el tiempo")

    #         # Esperar posible redirección o confirmación
    #         time.sleep(3)
    #         print("✅ Proceso de captcha completado")

    #     except Exception as e:
    #         print(f"❌ Error crítico resolviendo captcha: {str(e)}")
    #         raise

    def resolver_captcha_wallmartmx(self, driver):
        try:
            print("🔐 Resolviendo captcha de Walmart MX (solución mejorada)...")

            # 1. Esperar a que el desafío esté completamente cargado
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH,
                    "//*[@role='button' and contains(., 'Mantén presionado')]"))
            )

            # 2. Localizar el botón principal usando la estructura jerárquica
            button_container = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH,
                    "//div[contains(@class, 'button') and .//p[contains(text(), 'Mantén presionado')]]"))
            )

            # 3. Localizar el elemento de texto específico
            button_text = button_container.find_element(By.XPATH,
                ".//p[contains(@class, 'text') and contains(text(), 'Mantén presionado')]")

            # 4. Scroll y posicionamiento preciso
            driver.execute_script("""
                arguments[0].scrollIntoView({
                    behavior: 'auto',
                    block: 'center',
                    inline: 'center'
                });
            """, button_container)

            # 5. Simulación de acción humana con eventos precisos
            action = ActionChains(driver)

            # Movimiento inicial al contenedor
            action.move_to_element(button_container)
            action.pause(random.uniform(0.3, 0.7))

            # Movimiento preciso al texto
            action.move_to_element(button_text)
            action.pause(random.uniform(0.2, 0.5))

            # Presionar y mantener
            action.click_and_hold()
            action.pause(0.1)
            action.perform()

            print("⏳ Manteniendo presionado el botón (simulación mejorada)...")

            # 6. Monitoreo avanzado con detección de cambios
            start_time = time.time()
            progress_detected = False
            hold_time = random.uniform(18.0, 22.0)  # Tiempo variable entre 18-22 segundos

            while time.time() - start_time < hold_time:
                try:
                    # Verificar cambios en el contenedor principal
                    current_bg = button_container.value_of_css_property("background-color")
                    if "rgba(0, 0, 0, 0)" not in current_bg:  # Cambio de fondo detectado
                        progress_detected = True
                        print("✅ Cambio de fondo detectado")
                        break

                    # Verificar animación de progreso
                    progress_bar = button_container.find_elements(By.XPATH,
                        ".//div[contains(@style, 'width:') and contains(@style, 'background')]")
                    if progress_bar and progress_bar[0].value_of_css_property("width") != "0px":
                        progress_detected = True
                        print("✅ Barra de progreso detectada")
                        break

                    # Pequeños movimientos aleatorios para parecer humano
                    if random.random() > 0.7:
                        action.move_by_offset(
                            random.randint(-3, 3),
                            random.randint(-2, 2)
                        ).pause(0.1).perform()

                    time.sleep(0.3)
                except:
                    time.sleep(0.3)
                    continue

            # 7. Liberación con eventos completos
            action.release()
            action.move_by_offset(1, 1)  # Pequeño movimiento al soltar
            action.pause(0.2)
            action.perform()

            # 8. Esperar confirmación final
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH,
                        "//*[contains(@class, 'success') or contains(@class, 'checkmark')]")))
                print("✅ Verificación de captcha exitosa")
            except:
                if progress_detected:
                    print("⚠️ No se encontró confirmación visual pero se detectó progreso")
                else:
                    print("⚠️ No se detectó confirmación visual del captcha")

            # Espera final aleatoria antes de continuar
            time.sleep(random.uniform(1.5, 3.0))

        except Exception as e:
            print(f"❌ Error en solución mejorada: {str(e)}")

            # Intentar solución de emergencia basada en el issue de GitHub
            try:
                print("🔄 Intentando método de emergencia basado en eventos directos...")
                driver.execute_script("""
                    const buttons = document.querySelectorAll('[role="button"]');
                    for (const btn of buttons) {
                        if (btn.textContent.includes('Mantén presionado')) {
                            const mouseDown = new MouseEvent('mousedown', { bubbles: true });
                            btn.dispatchEvent(mouseDown);
                            setTimeout(() => {
                                const mouseUp = new MouseEvent('mouseup', { bubbles: true });
                                btn.dispatchEvent(mouseUp);
                            }, 20000);
                            break;
                        }
                    }
                """)
                time.sleep(22)
                print("✅ Método de emergencia ejecutado")
            except Exception as fallback_error:
                print(f"⚠️ Método de emergencia también falló: {str(fallback_error)}")
                raise







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
        self.urls_file = os.path.join(self.project_dir, 'extraccion', 'dataset', 'datos_extraidos', 'urls.txt')

    def start_requests(self):
        try:
            with open(self.urls_file, 'r') as f:
                urls = f.readlines()

            for url in urls:
                url = url.strip()
                if url:
                    print("Request: " + url)
                    headers = {
                        'User-Agent': (
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                            '(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
                        ),
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'
                    }

                    yield Request(
                        url,
                        callback=self.save_page,
                        errback=self.fallback_with_selenium,
                        headers=headers,
                        dont_filter=True
                    )
        except FileNotFoundError:
            self.logger.error(f"¡Archivo no encontrado! Verifica la ruta: {self.urls_file}")


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
            # options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            user_agent = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            )
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
