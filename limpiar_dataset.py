"""Limpia el CSV de Cielos Abiertos y lo guarda comprimido (.csv.gz).

Uso (desde la raíz del proyecto, con el entorno virtual activo):
    python limpiar_dataset.py

Lee:      data/Cielos_Abiertos_Colombia_20261002.csv   (el original, NO va a Git)
Escribe:  data/cielos_abiertos_limpio.csv.gz           (este sí va a Git)
"""
import unicodedata
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent
ENTRADA = BASE / "data" / "vuelos2.csv.gz"
SALIDA = BASE / "data" / "cielos_abiertvos_limpio.csv.gz"

# Pon True solo si el equipo decide eliminar filas idénticas (puede cambiar los totales).
QUITAR_DUPLICADOS = False

# Nombres distintos de una misma ciudad (claves SIN tildes).
ALIAS = {
    "CARTAGENA DE INDIAS": "CARTAGENA",
    "SANTIAGO DE CALI": "CALI",
    "ARAUCA MUNICIPIO": "ARAUCA",
    "CIUDAD DE MEXICO": "MEXICO",
}


def sin_tildes(texto):
    return "".join(c for c in unicodedata.normalize("NFD", str(texto))
                   if unicodedata.category(c) != "Mn")


def unificar(serie, usar_alias=False):
    """Une variantes con y sin tilde (queda la más frecuente) y aplica ALIAS."""
    mapa, canon = {}, {}
    for valor in serie.dropna().value_counts().index:   # de más a menos frecuente
        clave = sin_tildes(valor)
        if usar_alias and clave in ALIAS:
            mapa[valor] = ALIAS[clave]
        else:
            canon.setdefault(clave, valor)
            mapa[valor] = canon[clave]
    return serie.map(mapa)


def mb(ruta):
    return ruta.stat().st_size / 1_000_000


def main():
    if not ENTRADA.exists():
        raise SystemExit(f"No se encontró {ENTRADA}. Cópialo a la carpeta data/.")

    print(f"Leyendo {ENTRADA.name} ({mb(ENTRADA):.1f} MB)...")
    df = pd.read_csv(ENTRADA, dtype=str)
    filas_ini = len(df)
    print(f"  Filas: {filas_ini:,}   Columnas: {df.shape[1]}")

    # 1) Texto: quitar espacios y pasar a mayúsculas (menos fecha y números)
    numericas = ["anio", "mes", "pasajeros", "carga_kg"]
    texto = [c for c in df.columns if c not in numericas + ["fecha", "es_ruta_pei"]]
    for col in texto:
        df[col] = df[col].str.strip().str.upper()

    # 2) Unificar ciudades, países y aeropuertos (tildes y alias)
    for col in texto:
        if any(p in col for p in ("ciudad", "pais", "nombre_apto")):
            df[col] = unificar(df[col], usar_alias="ciudad" in col)

    # 3) Números
    # Año: acepta "2019", "2,019", "2.019", "2019.0" o "2019-01-01".
    # Si no se puede leer casi todo, se deja la columna original sin tocar.
    if "anio" in df.columns:
        limpio = (df["anio"].str.replace(r"[,\s.]", "", regex=True)
                  .str.extract(r"^((?:19|20)\d{2})", expand=False))
        anio = pd.to_numeric(limpio, errors="coerce")
        fallos = int(anio.isna().sum())
        if fallos / len(df) > 0.05:
            print(f"  AVISO anio: {fallos:,} valores ilegibles; se deja la columna original.")
        else:
            print(f"  anio: {fallos:,} valores vacíos tras la conversión")
            df["anio"] = anio.astype("Int64")
    if "mes" in df.columns:
        mes = pd.to_numeric(df["mes"], errors="coerce")
        if mes.isna().mean() > 0.05:
            print("  AVISO mes: valores ilegibles; se deja la columna original.")
        else:
            df["mes"] = mes.astype("Int64")
    for col in ("pasajeros", "carga_kg"):
        con_coma = int(df[col].str.contains(",", na=False).sum())
        print(f"  {col}: {con_coma:,} valores traen coma de miles (se quita)")
        num = pd.to_numeric(df[col].str.replace(",", "", regex=False), errors="coerce")
        print(f"  {col}: {int(num.isna().sum()):,} valores no numéricos se dejan en 0")
        num = num.fillna(0)
        df[col] = num.astype("int64") if (num % 1 == 0).all() else num

    # 4) Duplicados exactos
    dup = int(df.duplicated().sum())
    print(f"  Filas idénticas (duplicadas): {dup:,}")
    if QUITAR_DUPLICADOS and dup:
        df = df.drop_duplicates()
        print("  -> Eliminadas.")
    else:
        print("  -> Se conservan (QUITAR_DUPLICADOS = False).")

    # 5) Vacíos por columna (informativo)
    vacios = df.isna().sum()
    vacios = vacios[vacios > 0]
    if len(vacios):
        print("  Columnas con valores vacíos:")
        for col, n in vacios.items():
            print(f"    {col}: {int(n):,}")

    # 6) Guardar comprimido
    df.to_csv(SALIDA, index=False, encoding="utf-8", compression="gzip")
    print(f"\nListo: {SALIDA.name}")
    print(f"  Filas: {len(df):,} (antes {filas_ini:,})")
    print(f"  Tamaño: {mb(SALIDA):.1f} MB (antes {mb(ENTRADA):.1f} MB)")
    if mb(SALIDA) >= 100:
        print("  AVISO: sigue pesando 100 MB o más; GitHub no lo aceptará.")


if __name__ == "__main__":
    main()
