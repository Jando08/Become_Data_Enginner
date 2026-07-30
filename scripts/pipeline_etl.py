import json
import pandas as pd
import requests

# 1. EXTRACT (Función de extracción)
def extraer_datos(url: str) -> dict:
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        return respuesta.json()
    raise Exception(f"Error al consumir API: {respuesta.status_code}")

# 2. TRANSFORM (Función de transformación)
def transformar_datos(datos_raw: dict) -> pd.DataFrame:
    df = pd.DataFrame([datos_raw])
    df['estado_texto'] = df['completed'].apply(lambda x: 'COMPLETADO' if x else 'PENDIENTE')
    df_limpio = df[['id', 'userId', 'title', 'estado_texto']].rename(columns={
        'userId': 'usuario_id',
        'title': 'titulo'
    })
    return df_limpio

# 3. LOAD (Función de carga)
def cargar_datos(df: pd.DataFrame, ruta_destino: str) -> None:
    df.to_csv(ruta_destino, index=False, encoding="utf-8")
    print(f"🚀 Datos guardados exitosamente en {ruta_destino}")

# 4. ORQUESTADOR PRINCIPAL
def main():
    URL_API = "https://jsonplaceholder.typicode.com/todos/1"
    RUTA_CSV = "datos_procesados/pipeline_etl_resultado.csv"
    
    print("Iniciando Pipeline ETL...")
    raw_data = extraer_datos(URL_API)
    df_procesado = transformar_datos(raw_data)
    cargar_datos(df_procesado, RUTA_CSV)

if __name__ == "__main__":
    main()
