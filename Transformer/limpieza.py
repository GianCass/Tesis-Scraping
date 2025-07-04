import os
import trafilatura

RAW_DIR = os.path.join("Transformer", "data", "raw")
PROCESSED_DIR = os.path.join("Transformer", "data", "processed")

def extract_text_trafilatura(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    # Extraer el texto visible más relevante
    result = trafilatura.extract(html, include_comments=False, include_tables=True, favor_recall=True)
    return result

def process_all_html_files(raw_root=RAW_DIR, processed_root=PROCESSED_DIR):
    for root, _, files in os.walk(raw_root):
        for file in files:
            if file.endswith(".html"):
                input_path = os.path.join(root, file)
                
                # Calcular ruta de salida manteniendo subcarpeta
                relative_path = os.path.relpath(input_path, raw_root)
                output_path = os.path.join(processed_root, os.path.splitext(relative_path)[0] + "_extracted.txt")
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                print(f"🔍 Procesando: {input_path}")
                extracted_text = extract_text_trafilatura(input_path)

                if extracted_text:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(extracted_text)
                    print(f"✅ Guardado: {output_path}")
                else:
                    print(f"⚠️ No se extrajo texto desde: {input_path}")

if __name__ == "__main__":
    process_all_html_files()
