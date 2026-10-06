"""Dimensión temporal — lógica separada del template (rol 3).

Usa analisis/resumenData.py (datos ya limpios) y calcula lo que muestra
el tablero `temporal.html`:

- 3 indicadores: año pico, caída 2020 vs 2019, mes estacional pico.
- 3 visualizaciones: evolución anual, estacionalidad (mes 1-12),
  serie mensual completa.
- 2 filtros: tipo de tráfico y rango de años.

Las imágenes PNG se guardan en esta misma carpeta (Temporal/) y sirven
como respaldo/evidencia del reporte. El tablero web usa Chart.js con los
mismos datos (ver `obtener_datos_temporal`).

Uso:
    python -m analisis.Temporal.analisisTemporal   # regenera los 3 PNG
"""

from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg") 
import matplotlib.pyplot as plt 
from analisis.resumenData import cargar_datos

CARPETA = Path(__file__).resolve().parent
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
         "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
TRAFICOS = {"todos": "Todos", "NACIONAL": "Nacional", "INTERNACIONAL": "Internacional"}


def aplicar_filtros(df, trafico="todos", anio_ini=None, anio_fin=None):
    """Aplica los 2 filtros interactivos del tablero."""
    if trafico in ("NACIONAL", "INTERNACIONAL"):
        df = df[df["trafico"] == trafico]
    anios = sorted(df["anio"].unique().tolist())
    if anio_ini is not None:
        df = df[df["anio"] >= int(anio_ini)]
    if anio_fin is not None:
        df = df[df["anio"] <= int(anio_fin)]
    return df.copy(), anios


def obtener_datos_temporal(trafico="todos", anio_ini=None, anio_fin=None):
    """Calcula indicadores y series ya listas para el template."""
    base = cargar_datos()
    df, anios = aplicar_filtros(base, trafico, anio_ini, anio_fin)
    if df.empty:
        return {"vacio": True, "anios": anios, "traficos": TRAFICOS,
                "trafico": trafico, "anio_ini": anio_ini, "anio_fin": anio_fin}
    if anio_ini is None:
        anio_ini = int(df["anio"].min())
    if anio_fin is None:
        anio_fin = int(df["anio"].max())

   
    por_anio = (df.groupby("anio")
                  .agg(registros=("mes", "size"), pasajeros=("pasajeros", "sum"))
                  .reset_index().sort_values("anio"))
    por_anio["pasajeros"] = por_anio["pasajeros"].astype(int)


    por_mes = (df.groupby("mes")
                 .agg(registros=("mes", "size"), pasajeros=("pasajeros", "sum"))
                 .reindex(range(1, 13), fill_value=0))
    por_mes["pasajeros"] = por_mes["pasajeros"].astype(int)

    # 3) Serie mensual completa (periodo YYYY-MM).
    serie = (df.groupby("periodo")
               .agg(registros=("mes", "size"), pasajeros=("pasajeros", "sum"))
               .reset_index().sort_values("periodo"))
    serie["pasajeros"] = serie["pasajeros"].astype(int)
    serie["etiqueta"] = serie["periodo"].dt.strftime("%Y-%m")

    # --- 3 indicadores ---
    fila_pico = por_anio.loc[por_anio["pasajeros"].idxmax()]
    fila_valle = por_anio.loc[por_anio["pasajeros"].idxmin()]
    mes_pico = int(por_mes["pasajeros"].idxmax())
    mes_valle = int(por_mes["pasajeros"].idxmin())

    # Caída 2020 vs 2019 (si ambos años están en el filtro).
    pas_2019 = por_anio.loc[por_anio["anio"] == 2019, "pasajeros"]
    pas_2020 = por_anio.loc[por_anio["anio"] == 2020, "pasajeros"]
    if len(pas_2019) and len(pas_2020) and int(pas_2019.iloc[0]) > 0:
        caida_2020 = round((1 - float(pas_2020.iloc[0]) / float(pas_2019.iloc[0])) * 100, 1)
    else:
        caida_2020 = None

    # Variación del último año completo vs el anterior (usa años con 12 meses
    # sólo si el filtro los incluye; si no, compara los dos últimos del filtro).
    var_ultima = None
    if len(por_anio) >= 2:
        ult, prev = por_anio.iloc[-1], por_anio.iloc[-2]
        if int(prev["pasajeros"]) > 0:
            var_ultima = {
                "de": int(prev["anio"]), "a": int(ult["anio"]),
                "pct": round((float(ult["pasajeros"]) / float(prev["pasajeros"]) - 1) * 100, 1),
            }

    return {
        "vacio": False,
        "traficos": TRAFICOS, "trafico": trafico,
        "anios": anios, "anio_ini": int(anio_ini), "anio_fin": int(anio_fin),
        "kpis": {
            "anio_pico": int(fila_pico["anio"]),
            "pas_pico": int(fila_pico["pasajeros"]),
            "anio_valle": int(fila_valle["anio"]),
            "pas_valle": int(fila_valle["pasajeros"]),
            "caida_2020": caida_2020,
            "mes_pico": MESES[mes_pico - 1],
            "mes_pico_num": mes_pico,
            "mes_valle": MESES[mes_valle - 1],
            "var_ultima": var_ultima,
        },
        "anual": {
            "etiquetas": por_anio["anio"].astype(str).tolist(),
            "registros": por_anio["registros"].astype(int).tolist(),
            "pasajeros": por_anio["pasajeros"].astype(int).tolist(),
        },
        "estacional": {
            "etiquetas": MESES,
            "registros": por_mes["registros"].astype(int).tolist(),
            "pasajeros": por_mes["pasajeros"].astype(int).tolist(),
        },
        "serie": {
            "etiquetas": serie["etiqueta"].tolist(),
            "pasajeros": serie["pasajeros"].astype(int).tolist(),
        },
        "tabla_anual": por_anio.rename(columns={"anio": "año"}).to_dict("records"),
    }


def _estilo():
    plt.rcParams.update({"figure.dpi": 120, "axes.grid": True,
                         "grid.alpha": 0.3, "font.size": 9})


def generar_imagenes(trafico="todos", anio_ini=None, anio_fin=None):
    """Genera los 3 PNG de respaldo en esta carpeta. Devuelve las rutas."""
    datos = obtener_datos_temporal(trafico, anio_ini, anio_fin)
    if datos["vacio"]:
        return []
    _estilo()
    salidas = []

    # 1) Evolución anual de pasajeros.
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.bar(datos["anual"]["etiquetas"], datos["anual"]["pasajeros"], color="#16324F")
    ax.set_title("Evolución anual de pasajeros")
    ax.set_xlabel("Año")
    ax.set_ylabel("Pasajeros")
    fig.tight_layout()
    p1 = CARPETA / "evolucion_anual.png"
    fig.savefig(p1, bbox_inches="tight")
    plt.close(fig)
    salidas.append(str(p1))

    # 2) Estacionalidad por mes calendario.
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.plot(datos["estacional"]["etiquetas"], datos["estacional"]["pasajeros"],
            marker="o", color="#1F5F7A")
    ax.set_title("Estacionalidad: pasajeros por mes calendario")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Pasajeros (suma de todos los años)")
    fig.tight_layout()
    p2 = CARPETA / "estacionalidad_mensual.png"
    fig.savefig(p2, bbox_inches="tight")
    plt.close(fig)
    salidas.append(str(p2))

    # 3) Serie mensual completa.
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(datos["serie"]["etiquetas"], datos["serie"]["pasajeros"],
            linewidth=1.2, color="#E3A008")
    ax.set_title("Serie mensual de pasajeros (YYYY-MM)")
    ax.set_xlabel("Periodo")
    ax.set_ylabel("Pasajeros")
    paso = max(1, len(datos["serie"]["etiquetas"]) // 12)
    ax.set_xticks(range(0, len(datos["serie"]["etiquetas"]), paso))
    ax.set_xticklabels(datos["serie"]["etiquetas"][::paso], rotation=45, ha="right")
    fig.tight_layout()
    p3 = CARPETA / "serie_mensual.png"
    fig.savefig(p3, bbox_inches="tight")
    plt.close(fig)
    salidas.append(str(p3))

    return salidas


if __name__ == "__main__":
    rutas = generar_imagenes()
    for r in rutas:
        print(f"Generada: {r}")


