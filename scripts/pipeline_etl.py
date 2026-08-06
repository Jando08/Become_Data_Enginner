import os
import logging
import requests
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.dialects.postgresql import insert

# Configuración de Logs
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

def cargar_datos_upsert(df: pd.DataFrame, nombre_tabla: str) -> None:
    logging.info(f"Iniciando carga inteligente (UPSERT) en '{nombre_tabla}'...")
    try:
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        dbname = os.getenv("DB_NAME")

        # Construcción segura de la cadena de conexión
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        engine = create_engine(db_url)

        # Convertimos el DataFrame a una lista de diccionarios
        registros = df.to_dict(orient='records')

        metadata = MetaData()
        tabla = Table(nombre_tabla, metadata, autoload_with=engine)

        with engine.begin() as conexion:
            for registro in registros:
                # Sentencia INSERT con cláusula ON CONFLICT
                stmt = insert(tabla).values(registro)

                # Estrategia: Si hay conflicto en 'id', actualiza las columnas
                upsert_stmt = stmt.on_conflict_do_update(
                    index_elements=['id'],  # Columna que tiene la PK o UNIQUE constraint
                    set_={
                        'usuario_id': stmt.excluded.usuario_id,
                        'titulo': stmt.excluded.titulo,
                        'estado_texto': stmt.excluded.estado_texto
                    }
                )
                conexion.execute(upsert_stmt)

        logging.info("Carga UPSERT completada. Registros creados o actualizados sin errores.")
    except Exception as e:
        logging.error(f"Error en la carga UPSERT: {e}")
        raise

def main():
    logging.info("=== INICIANDO EJECUCIÓN DEL PIPELINE ETL ===")
    URL_API = "https://jsonplaceholder.typicode.com/todos/1"
    RUTA_CSV = "datos_procesados/pipeline_final.csv"
    NOMBRE_TABLA_SQL = "tareas_procesadas"

    try:
        raw_data = extraer_datos(URL_API)
        df_procesado = transformar_datos(raw_data)
        
        # Carga Dual: Respaldo CSV + Carga SQL
        cargar_datos_csv(df_procesado, RUTA_CSV)
        cargar_datos_upsert(df_procesado, NOMBRE_TABLA_SQL)
        
        logging.info("=== PIPELINE ETL FINALIZADO CON ÉXITO ===")
    except Exception as e:
        logging.critical(f"El pipeline ETL falló y no pudo completar la ejecución: {e}")

if __name__ == "__main__":
    main()
