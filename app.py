import unicodedata
from functools import lru_cache
from pathlib import Path

import pandas as pd
from flask import Flask, render_template, request
from analisis.Temporal.analisisTemporal import obtener_datos_temporal

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "cielos_abiertos_limpio.csv.gz"
PAIS_LOCAL = "COLOMBIA"   # cómo aparece Colombia en pais_origen / pais_destino

app = Flask(__name__)

DIMENSIONES = [
    {"endpoint": "poblacional", "nombre": "Dimensión poblacional"},
    {"endpoint": "territorial", "nombre": "Dimensión territorial"},
    {"endpoint": "temporal", "nombre": "Dimensión temporal"},
    {"endpoint": "relacional", "nombre": "Dimensión relacional y multivariada"},
]

NIVELES = {
    "ciudad_origen": "Ciudad de origen",
    "pais_origen": "País de origen",
    "ciudad_destino": "Ciudad de destino",
    "pais_destino": "País de destino",
    "nombre_apto_origen": "Aeropuerto de origen",
    "nombre_apto_destino": "Aeropuerto de destino",
}

AMBITOS = {"todos": "Todos", "colombia": "Solo Colombia", "exterior": "Solo exterior"}

# Nombres distintos de una misma ciudad (escribir las claves SIN tildes).
ALIAS = {
    "CARTAGENA DE INDIAS": "CARTAGENA",
    "SANTIAGO DE CALI": "CALI",
    "ARAUCA MUNICIPIO": "ARAUCA",
    "CIUDAD DE MEXICO": "MEXICO",
    "GUAINIA BARRANCO MINAS": "BARRANCOMINAS",
}


@app.context_processor
def menu():
    return {"dimensiones": DIMENSIONES, "endpoint_actual": request.endpoint}


def sin_tildes(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto)
                   if unicodedata.category(c) != "Mn")


def unificar(serie, usar_alias=False):
    """Une variantes con y sin tilde (queda la más frecuente) y aplica ALIAS."""
    mapa, canon = {}, {}
    for valor in serie.value_counts().index:      # de más a menos frecuente
        clave = sin_tildes(valor)
        if usar_alias and clave in ALIAS:
            mapa[valor] = ALIAS[clave]
        else:
            canon.setdefault(clave, valor)
            mapa[valor] = canon[clave]
    return serie.map(mapa)


@lru_cache(maxsize=1)
def cargar_datos():
    """Lee el CSV una sola vez y limpia nombres y números."""
    df = pd.read_csv(DATA_FILE, usecols=list(NIVELES) + ["pasajeros", "carga_kg"])
    for col in NIVELES:
        df[col] = df[col].str.strip().str.upper()
        df[col] = unificar(df[col], usar_alias=col.startswith("ciudad"))
    df["pasajeros"] = pd.to_numeric(df["pasajeros"], errors="coerce").fillna(0)
    df["carga_kg"] = pd.to_numeric(df["carga_kg"], errors="coerce").fillna(0)
    return df


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route('/analisis/poblacional')
def poblacional():
    # 1. Cargar el dataset
    df = pd.read_csv('data/vuelos2.csv.gz')
    
    # Limpieza de pasajeros para KPIs
    if 'pasajeros' in df.columns:
        df['pasajeros'] = df['pasajeros'].astype(str).str.replace(',', '')
        df['pasajeros'] = pd.to_numeric(df['pasajeros'], errors='coerce').fillna(0)
        promedio_pas = int(df['pasajeros'].mean())
    else:
        promedio_pas = 0
        
    total_operaciones = len(df)
    total_aerolineas = df['nombre_aerolinea'].nunique()
    
    # Top 5 Aerolíneas (%) y el resto en "Otras" para evidenciar oligopolio
    aero_counts = df['nombre_aerolinea'].value_counts(normalize=True) * 100
    top_aero = aero_counts.head(5)
    otras_pct = aero_counts.iloc[5:].sum()
    
    aero_labels = top_aero.index.tolist() + [f"Otras ({total_aerolineas - 5})"]
    aero_values = top_aero.values.round(1).tolist() + [round(otras_pct, 1)]

    # Top 3 Tipos de Vuelo (%)
    vuelos = df['tipo_vuelo'].value_counts(normalize=True).head(3) * 100
    
    # Top 5 Ciudades (%)
    ciudades = df['ciudad_origen'].value_counts(normalize=True).head(5) * 100

    datos_dinamicos = {
        "kpis": {
            "operaciones": f"{total_operaciones:,}",
            "aerolineas": total_aerolineas,
            "promedio_pasajeros": promedio_pas
        },
        "aerolineas": {
            "etiquetas": aero_labels,
            "valores": aero_values 
        },
        "vuelos": {
            "etiquetas": vuelos.index.tolist(),
            "valores": vuelos.values.round(1).tolist()
        },
        "ciudades": {
            "etiquetas": ciudades.index.tolist(),
            "valores": ciudades.values.round(1).tolist()
        }
    }

    return render_template('poblacional.html', datos=datos_dinamicos)


@app.route("/analisis/territorial")
def territorial():
    nivel = request.args.get("nivel", "ciudad_origen")
    if nivel not in NIVELES:
        nivel = "ciudad_origen"
    ambito = request.args.get("ambito", "todos")
    if ambito not in AMBITOS:
        ambito = "todos"
    ctx = dict(niveles=NIVELES, nivel=nivel, ambitos=AMBITOS, ambito=ambito,
               r=None, error=None)

    if not DATA_FILE.exists():
        ctx["error"] = f"No se encontró {DATA_FILE.name} en la carpeta data."
        return render_template("territorial.html", **ctx)

    df = cargar_datos()
    col_pais = "pais_origen" if "origen" in nivel else "pais_destino"
    if ambito == "colombia":
        df = df[df[col_pais] == PAIS_LOCAL]
    elif ambito == "exterior":
        df = df[df[col_pais].notna() & (df[col_pais] != PAIS_LOCAL)]
    if df.empty:
        ctx["error"] = "No hay datos con ese filtro. Revisa el valor de PAIS_LOCAL en app.py."
        return render_template("territorial.html", **ctx)

    g = (df.groupby(nivel)
           .agg(registros=("pasajeros", "size"),
                pasajeros=("pasajeros", "sum"),
                carga=("carga_kg", "sum"))
           .sort_values("pasajeros", ascending=False)
           .reset_index()
           .rename(columns={nivel: "territorio"}))
    g["pasajeros"] = g["pasajeros"].astype("int64")
    g["carga"] = g["carga"].astype("int64")

    total_pas = int(g["pasajeros"].sum())
    total_reg = int(g["registros"].sum())
    g["pct"] = (g["pasajeros"] / total_pas * 100).round(2)
    g["pct_reg"] = (g["registros"] / total_reg * 100).round(2)
    g["acum"] = g["pct"].cumsum().round(2)
    g["pas_por_reg"] = (g["pasajeros"] / g["registros"]).round(1)
    g["kg_por_pas"] = (g["carga"] / g["pasajeros"].where(g["pasajeros"] > 0)).round(1).fillna(0)

    con_pas = g[g["pasajeros"] > 0]
    solo_carga = g[(g["pasajeros"] == 0) & (g["carga"] > 0)]
    por_reg = g.sort_values("registros", ascending=False)
    grandes = con_pas[con_pas["registros"] >= 100]

    # El "menor" se calcula entre territorios con actividad real (100+ registros)
    base_menor = grandes if len(grandes) else con_pas
    menor = base_menor.iloc[-1]

    ctx["r"] = {
        "n_territorios": len(g),
        "n_sin_pasajeros": int((g["pasajeros"] == 0).sum()),
        "n_solo_carga": len(solo_carga),
        "n_pequenos": int((g["registros"] < 100).sum()),
        "total_registros": total_reg,
        "total_pasajeros": total_pas,
        "mayor": g.iloc[0].to_dict(),
        "menor": menor.to_dict(),
        "mayor_reg": por_reg.iloc[0].to_dict(),
        "menor_reg": por_reg.iloc[-1].to_dict(),
        "top5": round(float(g["pct"].head(5).sum()), 1),
        "hhi": round(float(((g["pasajeros"] / total_pas) ** 2).sum()), 3),
        "veces": round(float(g.iloc[0]["pasajeros"] / max(menor["pasajeros"], 1)), 1),
        "grafica": g.head(15)[["territorio", "pasajeros"]].to_dict("records"),
        "tabla": g.to_dict("records"),
        "mas_carga": grandes.nlargest(5, "kg_por_pas").to_dict("records"),
        "mas_llenos": grandes.nlargest(5, "pas_por_reg").to_dict("records"),
        "top_carga": g.nlargest(5, "carga").to_dict("records"),
    }
    return render_template("territorial.html", **ctx)


@app.route("/analisis/temporal")
def temporal():
    trafico = request.args.get("trafico", "todos")
    anio_ini = request.args.get("anio_ini", type=int)
    anio_fin = request.args.get("anio_fin", type=int)
    datos = obtener_datos_temporal(trafico=trafico, anio_ini=anio_ini, anio_fin=anio_fin)
    return render_template("temporal.html", datos=datos)


@app.route("/analisis/relacional")
def relacional():
    return render_template("relacional.html")


if __name__ == "__main__":
    app.run(debug=True)