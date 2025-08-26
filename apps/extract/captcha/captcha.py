import subprocess
import os
import shutil
import sys
import platform
import requests
from time import sleep
from selenium_recaptcha import Recaptcha_Solver
from selenium import webdriver
from seleniumbase import SB

FLARESOLVERR_DIR = os.path.join(os.getcwd(), 'FlareSolverr')
FLARESOLVERR_URL = "http://localhost:8191"

def is_node_installed():
    return shutil.which("node") is not None

def is_flaresolverr_running():
    try:
        response = requests.get(f"{FLARESOLVERR_URL}/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def install_node_instruction():
    print("\n❌ NodeJS no está instalado. ❌\n")
    system = platform.system().lower()

    if system == "darwin":
        print("macOS detectado.")
        print("➡️ Ejecuta en terminal:\n   brew install node")

    elif system == "windows":
        print("🪟 Windows detectado.")
        print("➡️ Descarga e instala Node.js desde:\n   https://nodejs.org")

    else:
        print("❌ Sistema operativo no reconocido. Instala Node.js manualmente desde https://nodejs.org")

    sys.exit(1)

# def install_requirements():
#     print("📦 Instalando dependencias de FlareSolverr...")
#     subprocess.run(
#         [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
#         cwd=FLARESOLVERR_DIR,
#         check=True
#     )

def start_flaresolverr():
    if not is_node_installed():
        install_node_instruction()

    if not os.path.exists(FLARESOLVERR_DIR):
        print("📦 Clonando FlareSolverr...")
        subprocess.run(["git", "clone", "https://github.com/FlareSolverr/FlareSolverr.git", FLARESOLVERR_DIR], check=True)
        install_requirements()

    elif not os.path.exists(os.path.join(FLARESOLVERR_DIR, "src", "flaresolverr.py")):
        print("❌ No se encontró el archivo principal de FlareSolverr.")
        sys.exit(1)

    print("🚀 Iniciando FlareSolverr desde Python...")
    subprocess.Popen(
        [sys.executable, "src/flaresolverr.py"],
        cwd=FLARESOLVERR_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    print("⏳ Esperando a que FlareSolverr esté disponible...")
    for _ in range(10):
        if is_flaresolverr_running():
            print("✅ FlareSolverr está corriendo.")
            return
        sleep(1)

    print("❌ No se pudo iniciar FlareSolverr.")
    print("\nVerificar estas condiciones ademas: Install Chrome (all OS) or Chromium (just Linux, it doesn't work in Windows) web browser.\n(Only in Linux) Install Xvfb package.\n(Only in macOS) Install XQuartz package.\n")
    sys.exit(1)



def cloudfare(url):
    if not is_flaresolverr_running():
        start_flaresolverr()

    headers = {"Content-Type": "application/json"}

    print("FlareSolverr listo para resolver Cloudflare de url: " + url)

    payload = {
        "cmd": "request.get",
        "url": url,
        "maxTimeout": 60000
    }

    response = requests.post(f"{FLARESOLVERR_URL}/v1", headers=headers, json=payload)

    print (response.text)
    data = response.json()

    if data.get("status") == "ok":
        return data["solution"]["response"]
    else:
        return resolve_cloudflare_with_seleniumbase(url)


def resolve_cloudflare_with_seleniumbase(url):
    print("Inicializando resolucion de Cloudflare con SeleniumBase")
    try:
        with SB(uc=True, headless=False, locale="en") as sb:
            sb.activate_cdp_mode(url)
            sb.uc_gui_click_captcha()
            sb.sleep(5)
            page_source = sb.driver.page_source
            return page_source

    except Exception as e:
        print(f"❌ Error cargando {url}: {e}")


def recaptcha(url):
    print("⚠️ Se detectó un reCAPTCHA, intentando resolverlo automáticamente...")

    options = webdriver.ChromeOptions()
    # Abrimos sin headless para fallback manual
    options.add_argument("--headless")
    options.add_argument("--window-size=1200,800")
    options.add_argument('--disable-blink-features=AutomationControlled')

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        sleep(40)

        solver = Recaptcha_Solver(
            driver=driver,
            ffmpeg_path='',  # descarga automático si no existe
            log=1  # Mostrar progreso
        )

        status = solver.solve_recaptcha()
        # if status and "recaptcha-success" in driver.page_source:
        if status:
            print("✅ reCAPTCHA resuelto automáticamente.")
            sleep(2)
        else:
            raise Exception("No se pudo resolver automáticamente")

    except Exception as e:
        print(f"\n⚠️ No se pudo resolver automáticamente: {e}")
        print("Esperando que el usuario resuelva el reCAPTCHA manualmente...")
        print("👉 Una vez resuelto, presiona ENTER para continuar.\n")
        # input()  # Usuario confirma resolucion del Recaptcha
        sleep(20)

    finally:
        html = driver.page_source
        driver.quit()
        print("🚪 Cerrando navegador tras resolución de reCAPTCHA.")
        return html