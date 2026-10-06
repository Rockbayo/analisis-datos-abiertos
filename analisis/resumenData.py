"""Resumen base del dataset para las dimensiones de análisis (rol 3: temporal).

Este módulo centraliza la carga y limpieza mínima del CSV para que los
análisis por dimensión (p. ej. analisis/Temporal/analisisTemporal.py) no
repitan lógica y trabajen siempre sobre los mismos datos ya analizados.

Dataset: vuelos (Cielos Abiertos, datos.gov.co) en
data/cielos_abiertvos_limpio.csv.gz (CSV limpio: texto en mayúsculas,
`anio` ya numérico, sin comas de miles).
Periodo observado: 2017-01 a 2026-02 (granularidad mensual en `fecha`).

Variables temporales disponibles:
  - fecha: primer día del mes ("2017 Jan 01..."), granularidad mensual.
  - anio: año del registro (viene como "2,017", se limpia a int).
  - mes: mes calendario 1-12 (int).
Variables de medida:
  - pasajeros: número de pasajeros (numérica, se limpia a número).
  - carga_kg: carga en kilogramos (numérica, se limpia a número).
Variables categóricas de apoyo:
  - trafico: NACIONAL / INTERNACIONAL / E.
  - tipo_vuelo: R, T, PASAJEROS, TRONCAL, etc.

Uso:
    from analisis.resumenData import cargar_datos, VARIABLES
    df = cargar_datos()
"""

from functools import lru_cache
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "cielos_abiertvos_limpio.csv.gz"

# Columnas que necesita la dimensión temporal (nada más, para ir rápido).
COLUMNAS_TEMPORALES = ["fecha", "anio", "mes", "pasajeros", "carga_kg",
                       "trafico", "tipo_vuelo"]

# Descripción corta para mostrar en el tablero.
VARIABLES = {
    "fecha": "Periodo mensual del registro (primer día del mes).",
    "anio": "Año del registro (2017 a 2026).",
    "mes": "Mes calendario 1-12, sirve para ver estacionalidad.",
    "pasajeros": "Número de pasajeros (variable numérica principal).",
    "carga_kg": "Carga transportada en kilogramos (numérica de apoyo).",
    "trafico": "Tipo de tráfico: NACIONAL, INTERNACIONAL o E.",
    "tipo_vuelo": "Categoría del vuelo (R, T, PASAJEROS, TRONCAL, ...).",
}


@lru_cache(maxsize=1)
def cargar_datos():
    """Lee el CSV limpio una sola vez y devuelve el DataFrame ya listo.

    Conversiones aplicadas (robustas: funcionan aunque el CSV traiga
    comas de miles o texto sin normalizar):
    - `anio`: a entero (en el CSV limpio ya viene como 2017).
    - `pasajeros` y `carga_kg`: a número, lo no numérico queda en 0.
    - `periodo`: fecha mensual normalizada (Timestamp del día 1).
    """
    df = pd.read_csv(DATA_FILE, usecols=COLUMNAS_TEMPORALES)

    df["anio"] = (df["anio"].astype(str).str.replace(",", "", regex=False))
    df["anio"] = pd.to_numeric(df["anio"], errors="coerce").astype("Int64")

    df["mes"] = pd.to_numeric(df["mes"], errors="coerce").astype("Int64")

    for col in ("pasajeros", "carga_kg"):
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", "", regex=False),
            errors="coerce",
        ).fillna(0)

    # Periodo mensual normalizado a partir de anio+mes (más fiable que `fecha`).
    df["periodo"] = pd.to_datetime(
        dict(year=df["anio"].astype(int), month=df["mes"].astype(int), day=1)
    )
    df = df.dropna(subset=["anio", "mes"]).copy()
    df["anio"] = df["anio"].astype(int)
    df["mes"] = df["mes"].astype(int)
    return df


def describir_variables():
    """Devuelve la descripción de variables para el tablero."""
    return dict(VARIABLES)


if __name__ == "__main__":
    df = cargar_datos()
    print(f"Registros: {len(df):,}")
    print(f"Periodo: {df['periodo'].min().date()} a {df['periodo'].max().date()}")
    print(f"Variables: {list(df.columns)}")
