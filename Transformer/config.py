from pathlib import Path

RAW_DIR = Path("data/raw")
PROC_DIR = Path("data/processed")

MODEL_ID = "PlanTL-GOB-ES/roberta-base-bne-sqac"

QUESTIONS = {
    "precio": "¿Cuál es el precio del producto?",
    "nombre": "¿Cuál es el nombre del producto?",
    "marca": "¿Cuál es la marca del producto?",
    "unidad": "¿En qué unidad se vende el producto?",
    "precio_unidad_basica": "¿Cuál es el precio por unidad básica?",
    "url": "¿Cuál es la URL del producto?"
}

MAX_ATTEMPTS = 5
NEED_MATCHES = 2