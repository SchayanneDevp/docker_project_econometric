
from pathlib import Path
import pandas as pd

# Rutas del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

ARCHIVO_ENTRADA = (
    BASE_DIR / "01_datos" / "raw" / "datal_2017_2026.csv"
)

ARCHIVO_SALIDA = (
    BASE_DIR / "01_datos" / "processed"
    / "serie_limpia_2017_2026.csv"
)


def main():
    print("Iniciando preparación de datos...")

    if not ARCHIVO_ENTRADA.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {ARCHIVO_ENTRADA}"
        )

    df = pd.read_csv(ARCHIVO_ENTRADA)

    # Validar columnas necesarias
    columnas_requeridas = {"fecha", "despachos", "pasajeros"}
    faltantes = columnas_requeridas - set(df.columns)

    if faltantes:
        raise ValueError(
            f"Faltan columnas en el CSV: {sorted(faltantes)}"
        )

    # Convertir tipos de datos
    df["fecha"] = pd.to_datetime(df["fecha"], errors="raise")

    for columna in ["despachos", "pasajeros"]:
        df[columna] = pd.to_numeric(
            df[columna], errors="raise"
        )

    # Ordenar cronológicamente
    df = df.sort_values("fecha").reset_index(drop=True)

    # Validaciones básicas
    if df.empty:
        raise ValueError("El archivo no contiene registros.")

    if df["fecha"].duplicated().any():
        raise ValueError("Hay fechas duplicadas en el archivo.")

    if df[["fecha", "despachos", "pasajeros"]].isna().any().any():
        raise ValueError("Hay valores vacíos en las columnas requeridas.")

    # Guardar datos procesados
    ARCHIVO_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ARCHIVO_SALIDA, index=False)

    print(f"Registros validados: {len(df)}")
    print(f"Archivo generado: {ARCHIVO_SALIDA}")
    print("Preparación finalizada correctamente.")


if __name__ == "__main__":
    main()
