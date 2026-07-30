import json
import os
import requests

# 1. Endpoint de la API
URL = "https://jsonplaceholder.typicode.com/todos/1"

print("Iniciando extracción de datos...")

# 2. Consumir la API usando la librería requests
respuesta = requests.get(URL)

if respuesta.status_code == 200:
    datos = respuesta.json()
    print(f"Datos recibidos con éxito: {datos}")

    # 3. Guardar el JSON procesado
    ruta_destino = "datos_procesados/tarea_extraida.json"
    os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)

    with open(ruta_destino, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4)

    print(f"Archivo guardado exitosamente en: {ruta_destino}")
else:
    print(f"Error al consumir la API. Código de estado: {respuesta.status_code}")
