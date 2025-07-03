import psycopg2
import json

# Cargar los datos desde el archivo JSON (línea por línea)
with open("C:/Users/Usuario/page_bodies.json", "r", encoding="utf-8") as f:
    lines = f.readlines()
    data = [json.loads(line) for line in lines]

# Conexión al Session Pooler de Supabase
conn = psycopg2.connect(
    host="aws-0-us-east-2.pooler.supabase.com",
    port="5432",
    dbname="postgres",
    user="postgres.kpypaqprheidjgnhcszy",
    password="holagianfranco15",
    sslmode="require"
)

cur = conn.cursor()

# Insertar los datos
inserted = 0
skipped = 0

for doc in data:
    try:
        cur.execute("""
            INSERT INTO productos (url, nombre, precio, descripcion, unidad, precio_unidad, fuente)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            doc.get("url"),
            doc.get("nombre"),
            doc.get("precio"),
            doc.get("descripcion"),
            doc.get("unidad"),
            doc.get("precio_unidad"),
            doc.get("fuente")
        ))
        inserted += 1
    except Exception as e:
        print(f"Error al insertar registro: {e}")
        skipped += 1

conn.commit()
cur.close()
conn.close()

print(f"✅ Insertados: {inserted}")
print(f"⏭️ Omitidos (duplicados o con error): {skipped}")
