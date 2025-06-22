from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline
import json
import re
import html
import datetime as dt
from pathlib import Path
from typing import Optional, Dict, Any
from collections import deque
import torch
torch.set_num_threads(4)


# ─── Config ────────────────────────────────────────────────────────────────
RAW_DIR = Path("data/raw")
PROC_DIR = Path("data/processed")
PROMPT_TXT = Path("prompt_google.txt").read_text().strip()

MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
# SECONDARY_MODEL_ID =  "ale-bay/zephyr-2b-gemma-sft"
RETAIL_FALLBK = "Desconocido"
COUNTRY_FALLB = "Desconocido"

MAX_ATTEMPTS = 5
NEED_MATCHES = 2

GEN_KWARGS = dict(
    max_new_tokens=512,
    do_sample=False,
    temperature=0.0,
    # top_p = 0.9
)

# ─── Helpers ───────────────────────────────────────────────────────────────
TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_RE = re.compile(r"<(script|style).*?>.*?</\1>", re.I | re.S)
WS_RE = re.compile(r"\s+")
BODY_RE = re.compile(r"<body[^>]*>(.*?)</body>", re.IGNORECASE | re.DOTALL)

def extract_body_content(html_string: str) -> Optional[str]:
    """
    Extracts the content between the first <body> and </body> tags.
    Returns None if <body> tags are not found.
    """
    match = BODY_RE.search(html_string)
    if match:
        return match.group(1).strip()
    return None  # Or you could return the original html_string if no body is found


def strip_html(raw: str) -> str:
    raw = SCRIPT_RE.sub(" ", raw)
    raw = TAG_RE.sub(" ", raw)
    return WS_RE.sub(" ", html.unescape(raw)).strip()


def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        device_map="auto"  # Accelerate will handle device placement
    )

    return pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer
    ), tokenizer


generator, tokenizer = load_model()


def ask_model(context: str, retail: str, country: str, nombre_producto: str) -> Optional[Dict[str, Any]]:
    prompt = PROMPT_TXT.format(
        html_content=context,
        retail_name=retail,
        country_name=country,
        producto=nombre_producto
        
    )

    out = generator(prompt, **GEN_KWARGS)[0]["generated_text"]

    print("\n--- OUTPUT DEL MODELO ---")
    print(out)
    print("--- FIN DEL OUTPUT ---\n")

    out = re.sub(r"^```json\s*|```$", "", out, flags=re.I).strip()
    out = out.replace("None", "null").replace(
        "True", "true").replace("False", "false")
    try:
        return json.loads(out)
    except json.JSONDecodeError as e:
        print(f"Error al parsear JSON: {e}")
        return None

# ─── Main loop ─────────────────────────────────────────────────────────────


def process_file(html_path: Path, retail: str, country: str):

    raw_html_content = html_path.read_text(
        errors="ignore")  # 1. Leer el contenido HTML crudo
    body_content = extract_body_content(raw_html_content) # 2. Extraer el contenido del <body> si existe
    if body_content:
        text_for_model = body_content # 2.1 Si hay contenido en <body>, usarlo
        print("[Info]  Using <body> fragment for model input")
    else:
        text_for_model = raw_html_content # 2.2 Si no hay <body>, usar el HTML completo
        print("[Info]  <body> tag not found, using full HTML")

    answers = deque(maxlen=NEED_MATCHES)

    print("\n--- PROMPT INICIO ---")
    print(text_for_model)
    print("--- PROMPT FIN ---\n")

    for attempt in range(1, MAX_ATTEMPTS + 1):
        # 3. Pasar el texto plano al modelo
        result = ask_model(text_for_model, retail, country)
        if result is None:
            print(f"Attempt {attempt}: invalid JSON.")
            continue
        answers.append(result)
        if len(answers) == NEED_MATCHES and len({json.dumps(a, sort_keys=True) for a in answers}) == 1:
            print(f"Stable answer after {attempt} tries.")
            return result
    print(f"No stable answer within {MAX_ATTEMPTS} attempts.")
    return None


def main():
    html_files = list(RAW_DIR.rglob("*.html"))
    if not html_files:
        print("No HTML files found.")
        return

    for html_path in tqdm(html_files, desc="Procesando"):
        country = "Colombia"
        retail = "Jumbo"
        nombre_producto = "Pan"

        res = process_file(html_path, retail, country, nombre_producto)
        if res is None:
            continue

        out_dir = PROC_DIR / country / retail
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = dt.datetime.now().strftime("%Y%m%d")

        nombre_para_archivo = "producto_desconocido"
        if isinstance(res, dict):
            producto_extraido_data = res.get("producto_extraido")
            if isinstance(producto_extraido_data, dict):
                nombre_para_archivo = producto_extraido_data.get(
                    "nombre", "producto_sin_nombre_detalle")
            else:
                # Fallback if "producto_extraido" structure is not as expected
                nombre_para_archivo = res.get(
                    "nombre", "producto_estructura_incorrecta")
        else:
            nombre_para_archivo = "resultado_no_es_dict"

        nombre_clean = re.sub(
            r"[^\w\-]+", "_", str(nombre_para_archivo).strip().lower())[:40]

        out_file = out_dir / f"{nombre_clean}_{ts}.json"
        out_file.write_text(json.dumps(res, ensure_ascii=False, indent=2))
        print(f"Guardado {out_file}")


if __name__ == "__main__":
    main()
