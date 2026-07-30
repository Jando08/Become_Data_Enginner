import json
import pandas as pd

print("Cargando datos raw...")

# 1. Leer el archivo JSON que guardamos anteriormente
with open("datos_procesados/tarea_extraida.json", "r", encoding="utf-8") as archivo:
    data = json.load(archivo)

# 2. Convertir el diccionario individual en un DataFrame de 1 sola fila
df = pd.DataFrame([data])

print("\n--- INFORMACIÓN DEL DATAFRAME ---")
print(df)

# 3. Transformación: Crear una columna nueva llamada 'estado_texto'
df['estado_texto'] = df['completed'].apply(lambda x: 'COMPLETADO' if x else 'PENDIENTE')

# 4. Seleccionar y renombrar columnas
df_final = df[['id', 'userId', 'title', 'estado_texto']].rename(columns={
    'userId': 'usuario_id',
    'title': 'titulo'
})

# 5. Exportar a un archivo CSV organizado
ruta_csv = "datos_procesados/tareas_limpias.csv"
df_final.to_csv(ruta_csv, index=False, encoding="utf-8")

print(f"\n🚀 Datos procesados y exportados a CSV con éxito en: {ruta_csv}")
