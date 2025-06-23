import torch, re, html, json, datetime as dt
from pathlib import Path
from typing import Optional, Dict, Any
from collections import deque
from tqdm import tqdm
from transformers import (
    AutoTokenizer, AutoModelForQuestionAnswering,
    BitsAndBytesConfig, pipeline
)

torch.set_num_threads(4)

# ─── Config ────────────────────────────────────────────────────────────────
RAW_DIR  = Path("data/raw")
PROC_DIR = Path("data/processed")

MODEL_ID = "PlanTL-GOB-ES/roberta-base-bne-sqac"   

QUESTIONS = {
    "precio":                "¿Cuál es el precio del producto?",
    "nombre":                "¿Cuál es el nombre del producto?",
    "marca":                 "¿Cuál es la marca del producto?",
    "unidad":                "¿En qué unidad se vende el producto?",
    "precio_unidad_basica":  "¿Cuál es el precio por unidad básica?",
    "url":                   "¿Cuál es la URL del producto?"
}

MAX_ATTEMPTS = 5
NEED_MATCHES = 2

# ─── Helpers de HTML ───────────────────────────────────────────────────────
TAG_RE    = re.compile(r"<[^>]+>")
SCRIPT_RE = re.compile(r"<(script|style).*?>.*?</\1>", re.I | re.S)
WS_RE     = re.compile(r"\s+")
BODY_RE   = re.compile(r"<body[^>]*>(.*?)</body>", re.I | re.S)

def extract_body_content(html_string: str) -> Optional[str]:
    """Devuelve el contenido entre <body>…</body> (sin tags)."""
    match = BODY_RE.search(html_string)
    return match.group(1).strip() if match else None

def strip_html(raw: str) -> str:
    raw = SCRIPT_RE.sub(" ", raw)
    raw = TAG_RE.sub(" ", raw)
    return WS_RE.sub(" ", html.unescape(raw)).strip()

# ─── Carga del modelo QA ───────────────────────────────────────────────────
def load_qa_model():
    # En CPU va bien; si dispones de GPU y 4-6 GB usa int8:
    # quant_cfg = BitsAndBytesConfig(load_in_8bit=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)
    model     = AutoModelForQuestionAnswering.from_pretrained(
        MODEL_ID,
        device_map="auto"           # GPU si existe, CPU si no
        # quantization_config=quant_cfg
    )
    return pipeline("question-answering", model=model, tokenizer=tokenizer)

qa_pipe = load_qa_model()

# ─── Preguntamos al modelo y devolvemos línea TSV ──────────────────────────
def ask_model(html_fragment: str) -> Optional[str]:
    context = strip_html(html_fragment)          # texto plano

    answers = []
    for key, question in QUESTIONS.items():
        out = qa_pipe(question=question, context=context)
        ans = out["answer"].strip()
        if ans == "" or ans.lower() in {"no", "ninguno"}:
            ans = "NA"
        answers.append(ans)

    # Aseguramos 6 campos
    if len(answers) != 6 or any(a == "NA" for a in answers):
        print("Respuesta incompleta:", answers)
        return None

    return "\t".join(answers)

# ─── Convierte TSV ➜ dict JSON (añade retail/country) ──────────────────────
def tsv_to_dict(tsv_line: str, retail: str, country: str) -> Dict[str, Any]:
    precio, nombre, marca, unidad, pub, url = tsv_line.split("\t")
    return {
        "precio": precio,
        "nombre": nombre,
        "marca": marca,
        "unidad": unidad,
        "precio_unidad_basica": pub,
        "url": url,
        "retailer": retail,
        "country": country
    }

# ─── Proceso por archivo ───────────────────────────────────────────────────
def process_file(html_path: Path, retail: str, country: str) -> Optional[Dict]:
    raw_html = html_path.read_text(errors="ignore")
    body     = extract_body_content(raw_html)
    text_for_model = body if body else raw_html

    answers = deque(maxlen=NEED_MATCHES)

    for attempt in range(1, MAX_ATTEMPTS + 1):
        tsv_line = ask_model(text_for_model)
        if not tsv_line:
            print(f"[{attempt}] TSV inválido.")
            continue

        result = tsv_to_dict(tsv_line, retail, country)
        answers.append(json.dumps(result, sort_keys=True))

        if len(answers) == NEED_MATCHES and len(set(answers)) == 1:
            print(f"✅ Respuesta estable en intento {attempt}")
            return json.loads(answers[-1])

    print("⛔ No se alcanzó estabilidad")
    return None

# ─── Main loop ─────────────────────────────────────────────────────────────
def main():
    html_files = list(RAW_DIR.rglob("*.html"))
    if not html_files:
        print("No HTML files found.")
        return

    all_products = {}
    retail  = "Jumbo"
    country = "Colombia"
    product = "Pan"

    for html_path in tqdm(html_files, desc="Procesando"):
        res = process_file(html_path, retail, country)
        if not res:
            continue

        key = re.sub(r"[^\w\-]+", "_", res["nombre"].lower())[:100]
        all_products[key] = res

    if all_products:
        out_dir = PROC_DIR / product 
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_file = out_dir / f"{product}_{ts}.json"
        out_file.write_text(json.dumps(all_products, ensure_ascii=False, indent=2))
        print(f"\nGuardado: {out_file}  ({len(all_products)} productos)")

if __name__ == "__main__":
    main()