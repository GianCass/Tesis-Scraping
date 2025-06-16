import json
import os
import re
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

# Rutas a los archivos
SCRAPED_DATA_PATH = "scraper/scraper/supermaxi_data.json"
PROMPT_FILE_PATH = "hugging-face/prompt.txt"  # Archivo en el mismo directorio de hugging_face

# Verificar existencia de archivos
if not os.path.exists(SCRAPED_DATA_PATH):
    raise FileNotFoundError(f"Archivo no encontrado: {os.path.abspath(SCRAPED_DATA_PATH)}")

if not os.path.exists(PROMPT_FILE_PATH):
    raise FileNotFoundError(f"Archivo de prompt no encontrado: {os.path.abspath(PROMPT_FILE_PATH)}")

# Cargar prompt desde archivo
with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as f:
    PROMPT_TEMPLATE = f.read()

# Cargar datos scrapeados
with open(SCRAPED_DATA_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)

# Inicializar modelo y tokenizer
model_name = "numind/ReaderLM-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0  # GPU (o MPS en Mac). Cambiar a device="cpu" si no hay GPU/MPS
)

def clean_json_output(raw_text: str) -> dict:
    """Extrae y valida JSON de la salida del modelo."""
    json_match = re.search(r"\{[\s\S]*\}", raw_text)
    if not json_match:
        return {"error": "No se encontró JSON válido"}
    try:
        return json.loads(json_match.group(0))
    except json.JSONDecodeError:
        return {"error": "JSON malformado"}

# Procesamiento de productos
for idx, product in enumerate(data, start=1):
    # Concatenar el contexto con título, descripción, precio y atributos (si los hay)
    context = (
        f"Título: {product.get('title', '')}\n"
        f"Descripción: {' '.join(product.get('description', []))}\n"
        f"Precio: {product.get('price', '')}\n"
        f"Atributos: {json.dumps(product.get('attributes', {}), ensure_ascii=False)}"
    )

    # Generar prompt final usando el template
    prompt = PROMPT_TEMPLATE.format(context=context)

    # Ejecutar el pipeline de generación de texto
    response = pipe(
        prompt,
        max_new_tokens=200,
        temperature=0.1,
        do_sample=False,
        pad_token_id=tokenizer.eos_token_id,
        return_full_text=False
    )

    # Limpiar la salida para extraer solo el JSON
    generated_text = response[0]["generated_text"]
    result = clean_json_output(generated_text)

    # Mostrar resultados
    print(f"\n{'='*30} Producto #{idx} {'='*30}")
    print(f"ID: {product.get('id', 'N/A')}")
    print("Datos extraídos:")
    print(json.dumps(result, indent=2, ensure_ascii=False))