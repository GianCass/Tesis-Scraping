import torch
from pathlib import Path
from datetime import datetime as dt
import json
from tqdm import tqdm
import re
from extractor import process_file
from config import RAW_DIR, PROC_DIR

torch.set_num_threads(4)

def main():
    html_files = list(RAW_DIR.rglob("*.html"))
    if not html_files:
        print("No HTML files found.")
        return

    all_products = {}
    retail = "Jumbo"
    country = "Colombia"
    product = "Pan"
    url = "https://www.tiendasjumbo.co/"

    for html_path in tqdm(html_files, desc="Procesando"):
        res = process_file(html_path, retail, country)
        if not res:
            continue

        key = re.sub(r"[^\w\-]+", "_", res["nombre"].lower())[:100]
        all_products[key] = res

    if all_products:
        out_dir = PROC_DIR / product 
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = dt.now().strftime("%Y%m%d_%H%M%S")
        out_file = out_dir / f"{product}_{ts}.json"
        out_file.write_text(json.dumps(all_products, ensure_ascii=False, indent=2))
        print(f"\nGuardado: {out_file}  ({len(all_products)} productos)")

if __name__ == "__main__":
    main()