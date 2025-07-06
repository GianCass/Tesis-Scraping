import re
import html
import json
from collections import deque
from pathlib import Path
from typing import Optional, Dict, Any
from transformers import (
    AutoTokenizer, AutoModelForQuestionAnswering,
    pipeline
)

def load_qa_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)
    model = AutoModelForQuestionAnswering.from_pretrained(
        MODEL_ID,
        device_map="auto"          
    )
    return pipeline("question-answering", model=model, tokenizer=tokenizer)

qa_pipe = load_qa_model()

# Helpers de HTML
TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_RE = re.compile(r"<(script|style).*?>.*?</\1>", re.I | re.S)
WS_RE = re.compile(r"\s+")
BODY_RE = re.compile(r"<body[^>]*>(.*?)</body>", re.I | re.S)

def extract_body_content(html_string: str) -> Optional[str]:
    match = BODY_RE.search(html_string)
    return match.group(1).strip() if match else None

def strip_html(raw: str) -> str:
    raw = SCRIPT_RE.sub(" ", raw)
    raw = TAG_RE.sub(" ", raw)
    return WS_RE.sub(" ", html.unescape(raw)).strip()

def ask_model(html_fragment: str) -> Optional[str]:
    context = strip_html(html_fragment)

    answers = []
    for key, question in QUESTIONS.items():
        out = qa_pipe(question=question, context=context)
        ans = out["answer"].strip()
        if ans == "" or ans.lower() in {"no", "ninguno"}:
            ans = "NA"
        answers.append(ans)

    if len(answers) != 6 or any(a == "NA" for a in answers):
        print("Respuesta incompleta:", answers)
        return None

    return "\t".join(answers)

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

def process_file(html_path: Path, retail: str, country: str) -> Optional[Dict]:
    raw_html = html_path.read_text(errors="ignore")
    body = extract_body_content(raw_html)
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

    print("No se alcanzó quorum de respuestas.")
    return None