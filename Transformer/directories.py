import csv
from pathlib import Path
import re
from urllib.parse import urlparse
import html
from unidecode import unidecode

def clean_string(text: str) -> str:
    """Limpia texto para nombres de directorio"""
    text = str(text)  # Asegura que sea string
    text = html.unescape(text)  # Decodifica HTML
    text = unidecode(text)  # Elimina acentos
    text = re.sub(r'[^\w\-_\. ]', '_', text.strip())  # Caracteres seguros
    return re.sub(r'\s+', ' ', text)[:50].strip()  # Limita longitud

def clean_url_dir(url: str) -> str:
    """Crea nombre legible de URL"""
    url = url.split('?')[0]  # Elimina parámetros
    name = urlparse(url).path.split('/')[-1] or urlparse(url).netloc
    return clean_string(name)

def create_structure(csv_path: Path, base_dir: Path):
    if not csv_path.exists():
        print(f"❌ Archivo no encontrado: {csv_path}")
        return

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')  # CSV con comas
        next(reader)  # Saltar encabezado (si existe)
        
        created = 0
        for row in reader:
            try:
                if len(row) < 5:  # Verifica mínimo de columnas
                    continue
                
                # Extrae columnas relevantes (ignora las últimas dos)
                country, retail, product, brand, url = row[0], row[1], row[2], row[3], row[4]
                
                # Crea ruta completa
                dir_path = (
                    base_dir / 
                    clean_string(country) / 
                    clean_string(retail) / 
                    clean_string(product) / 
                    clean_string(brand) / 
                    clean_url_dir(url)
                )
                
                dir_path.mkdir(parents=True, exist_ok=True)
                created += 1
                print(f"📂 {dir_path}")

            except Exception as e:
                print(f"⚠️ Error procesando fila: {row}\n   {type(e).__name__}: {e}")

    print(f"\n✅ Directorios creados: {created}")

if __name__ == "__main__":
    # Configuración
    CSV_FILE = Path("edaSisPricingInt(TablaActualizada) (2).csv")  # Asegúrate que esté en la misma carpeta
    OUTPUT_DIR = Path("data/raw")    # Ruta base de salida
    
    print("=== Iniciando creación de estructura ===")
    print(f"CSV: {CSV_FILE}")
    print(f"Salida: {OUTPUT_DIR}\n")
    
    create_structure(CSV_FILE, OUTPUT_DIR)