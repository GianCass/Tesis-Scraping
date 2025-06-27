import subprocess
import os
import shutil
import sys
import platform
import requests
from time import sleep

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
    distro = ""
    if system == "linux":
        try:
            with open("/etc/os-release", "r") as f:
                distro = f.read().lower()
        except:
            pass

    if system == "darwin":
        print("macOS detectado.")
        print("➡️ Ejecuta en terminal:\n   brew install node")

    elif system == "windows":
        print("🪟 Windows detectado.")
        print("➡️ Descarga e instala Node.js desde:\n   https://nodejs.org")

    else:
        print("❌ Sistema operativo no reconocido. Instala Node.js manualmente desde https://nodejs.org")

    sys.exit(1)

def install_requirements():
    print("📦 Instalando dependencias de FlareSolverr...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        cwd=FLARESOLVERR_DIR,
        check=True
    )

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
        raise Exception(f"Error FlareSolverr: {data}")


def recaptcha(url):
    print("⚠️  Resolver reCAPTCHA manualmente por ahora.")
    return
