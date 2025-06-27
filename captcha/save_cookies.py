import os
import pickle
from urllib.parse import urlparse
import undetected_chromedriver as uc

def save_cookies_for_multiple_urls(urls_with_captcha):
    cookies_dir = os.path.join(os.path.dirname(__file__), "cookies")
    os.makedirs(cookies_dir, exist_ok=True)

    seen_domains = set()

    for url, captcha_tipo in urls_with_captcha:
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "").strip()
        domain_key = domain.replace(".", "_")

        if domain in seen_domains:
            continue
        seen_domains.add(domain)

        filename = os.path.join(cookies_dir, f"cookies_{domain_key}.pkl")

        print(f"\n Abriendo Dominio Unico: {url} \n")

        try:
            driver = uc.Chrome(headless=False, use_subprocess=False)
            driver.get(f"{parsed.scheme}://{domain}")

            input(f"⚠️  Resuelve manualmente el CAPTCHA en {domain} de tipo {captcha_tipo} (si hay uno) y presiona Enter...")

            cookies = driver.get_cookies()
            with open(filename, "wb") as f:
                pickle.dump(cookies, f)

            print(f"✅ Cookies guardadas para {domain} en: {filename}")
            driver.quit()

        except Exception as e:
            print(f"❌ Error cargando {domain}: {e}")
            if driver:
                driver.quit()



def load_urls_from_txts():
    urls_with_captcha = []
    base_path = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'datos_extraidos')
    for file in ['dinamicas.txt', 'estaticas.txt']:
        full_path = os.path.join(base_path, file)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                for line in f:
                    partes = line.strip().split(', ', 1)
                    if len(partes) == 2:
                        url = partes[0].strip()
                        captcha_tipo = partes[1].strip().lower()
                        if url:
                            urls_with_captcha.append((url, captcha_tipo))
    return urls_with_captcha
