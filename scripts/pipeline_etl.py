import os
import json
import logging
import requests
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# 1. CONFIGURACIÓN DEL SISTEMA DE LOGS
logging.basicConfig(
    filename='pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)

load_dotenv()

def extraer_datos(url: str) -> dict:
    logging.info("Iniciando extracción de datos desde la API...")
    try:
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status() # Lanza excepción si el código de estado no es 200
        logging.info("Datos extraídos correctamente de la fuente.")
        return respuesta.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Fallo crítico en la extracción de datos: {e}")
        raise

def transformar_datos(datos_raw: dict) -> pd.DataFrame:
    logging.info("Iniciando transformación de datos con Pandas...")
    try:
        df = pd.DataFrame([datos_raw])
        df['estado_texto'] = df['completed'].apply(lambda x: 'COMPLETADO' if x else 'PENDIENTE')
        df_limpio = df[['id', 'userId', 'title', 'estado_texto']].rename(columns={
            'userId': 'usuario_id',
            'title': 'titulo'
        })
        logging.info("Transformación completada exitosamente.")
        return df_limpio
    except Exception as e:
        logging.error(f"Error durante la transformación de datos: {e}")
        raise

def cargar_datos_csv(df: pd.DataFrame, ruta_destino: str) -> None:
    try:
        df.to_csv(ruta_destino, index=False, encoding="utf-8")
        logging.info(f"Respaldo local guardado exitosamente en: {ruta_destino}")
    except Exception as e:
        logging.error(f"Error al guardar archivo CSV local: {e}")

def main():
    logging.info("=== INICIANDO EJECUCIÓN DEL PIPELINE ETL ===")
    URL_API = "https://jsonplaceholder.typicode.com/todos/1"
    RUTA_CSV = "datos_procesados/pipeline_final.csv"

    try:
        raw_data = extraer_datos(URL_API)
        df_procesado = transformar_datos(raw_data)
        cargar_datos_csv(df_procesado, RUTA_CSV)
        logging.info("=== PIPELINE ETL FINALIZADO CON ÉXITO ===")
    except Exception as e:
        logging.critical(f"El pipeline ETL falló y no pudo completar la ejecución: {e}")

if __name__ == "__main__":
    main()
