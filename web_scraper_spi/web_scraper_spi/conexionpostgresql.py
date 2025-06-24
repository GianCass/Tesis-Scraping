import json
import psycopg2

def limpiar(valor):
    """Evita insertar diccionarios u objetos no compatibles"""
    return valor if not isinstance(valor, dict) else None

# Conexión a PostgreSQL
conn = psycopg2.connect(
    dbname="extraccionprecioproducto",
    user="postgres",
    password="",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Leer JSON por líneas
ruta_json = "C:\\Users\\Usuario\\page_bodies.json"
with open(ruta_json, encoding='utf-8') as f:
    data = [json.loads(line) for line in f]

insertados = 0
omitidos = 0

for doc in data:
    url = limpiar(doc.get("url"))
    
    # Verificar si ya existe esa URL
    cur.execute("SELECT 1 FROM productos WHERE url = %s", (url,))
    if cur.fetchone():
        omitidos += 1
        continue

    cur.execute("""
        INSERT INTO productos (url, nombre, precio, descripcion, unidad, precio_unidad, fuente)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        url,
        limpiar(doc.get("nombre")),
        limpiar(doc.get("precio")),
        limpiar(doc.get("descripcion")),
        limpiar(doc.get("unidad")),
        limpiar(doc.get("precio_unidad")),
        limpiar(doc.get("fuente"))
    ))
    insertados += 1

conn.commit()
cur.close()
conn.close()

print(f"✅ Insertados: {insertados}")
print(f"⏭️ Omitidos (duplicados): {omitidos}")
