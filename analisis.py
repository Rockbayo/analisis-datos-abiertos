import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('data/vuelos2.csv')

# Informacion principal del dataset
Cantidad_registros = df.shape[0]
Cantidad_variables = df.shape[1]

print("Cantidad de registros: ", Cantidad_registros)
print("Cantidad de Variables: ", Cantidad_variables)

# Informacion de las variables del dataset
df.info()

# ==========================================
# ANÁLISIS NUMÉRICO Y DE CONSOLA
# ==========================================

# Conocimiento Evidente 1
print("\n¿Cuál es la concentración del mercado aéreo colombiano según la participación de las aerolíneas y el tipo de operación?")
# Analisis de variables categoricas
aerolinea = df['nombre_aerolinea'].value_counts(normalize=True) * 100
print(aerolinea)

tipo_vuelo = df['tipo_vuelo'].value_counts(normalize=True) * 100
print(tipo_vuelo)

# Conocimiento evidente 2
print("\n¿Cuál es el comportamiento del volumen de pasajeros en las operaciones registradas en el dataset?")
# Analisis de variables numericas
df['pasajeros'] = df['pasajeros'].str.replace(',','') # Eliminacion de las comas para poder convertir a numero
df['pasajeros'] = pd.to_numeric(df['pasajeros'], errors='coerce') # Conversion a numero remplazando errores por Nan

# Analisis estadistico de personas
print("Estadisticas pasajeros:\n", df['pasajeros'].describe()) 

# Conocimiento evidente 3
print("\n¿Desde qué ciudades se origina la mayor cantidad de operaciones aéreas en Colombia?")
# Analisis de la variable ciudad_origen
origen = df['ciudad_origen'].value_counts(normalize=True) * 100
print(origen)

# Conocimiento evidente 4 (Barreras de Mercado)
print("\n¿Existe pluralidad y participación equitativa de las distintas aerolíneas dentro del total de operaciones?")
participacion_aerolineas = df['nombre_aerolinea'].value_counts(normalize=True) * 100
top_3_suma = participacion_aerolineas.head(3).sum()
otras_suma = participacion_aerolineas.iloc[3:].sum()
cantidad_otras = len(participacion_aerolineas) - 3

print(f"Participación acumulada del Top 3: {top_3_suma:.2f}%")
print(f"Participación acumulada de las otras {cantidad_otras} aerolíneas: {otras_suma:.2f}%")

# ==========================================
# PREPARACION DE LOS DATOS PARA GRAFICAR
# ==========================================

# Gráfico 1.0: Top 5 de las aerolineas con mayor cantidad de operaciones
top_aerolineas = df['nombre_aerolinea'].value_counts().head(5)

plt.figure(figsize=(10, 6))
sns.barplot(
    x=top_aerolineas.values,
    y=top_aerolineas.index,
    hue=top_aerolineas.index,
    palette='viridis',
    legend=False
)
sns.set_style('whitegrid')

plt.title('Top 5 de aerolineas con mayor cantidad de operaciones', fontsize=14, pad=15)
plt.xlabel('Cantidad de operaciones', fontsize=12, labelpad=10)
plt.ylabel('Aerolineas', fontsize=12, labelpad=10)
plt.savefig('graficos/Top_5_Aerolineas.png', dpi=300, bbox_inches='tight')
plt.tight_layout()
plt.show()

# Gráfico 1.1: Principales tipos de vuelo top 3
tipos_principales = df['tipo_vuelo'].value_counts().head(3)

plt.figure(figsize=(8, 8))
plt.pie(
    tipos_principales.values,
    labels=tipos_principales.index,
    autopct='%1.1f%%',
    startangle=140,
    colors=sns.color_palette('pastel')
)
plt.title('Principales tipos de vuelo (Top 3)', fontsize=14, pad=15)
plt.savefig('graficos/Principales_tipos_de_vuelo.png', dpi=300, bbox_inches='tight')
plt.tight_layout()
plt.show()

# Gráfico 2: Top 5 de ciudades de origen con mayor cantidad de operaciones
top_ciudades_origen = df['ciudad_origen'].value_counts().head(5)

plt.figure(figsize=(10, 6))
sns.barplot(
    x=top_ciudades_origen.index,
    y=top_ciudades_origen.values,
    palette='magma',
    hue=top_ciudades_origen.index,
    legend=False
)
plt.title('Top 5 de Ciudades de origen con mayor cantidad de operaciones', fontsize=14, pad=15)
plt.xlabel('Ciudades de origen', fontsize=12)
plt.ylabel('Cantidad de operaciones', fontsize=12)
plt.xticks(rotation=45) 
plt.tight_layout()
plt.savefig('graficos/Top_5_Ciudades_origen.png', dpi=300, bbox_inches='tight')
plt.show()

# Gráfico 3: Distribucion del volumen de pasajeros por operacion mensual
plt.figure(figsize=(10, 6))
sns.histplot(
    df['pasajeros'].dropna(),
    bins=40,
    log_scale=True,
    color='teal'
)
plt.title('Distribucion de Volumen de pasajeros por operacion mensual', fontsize=14, pad=15)
plt.xlabel('Cantidad de Pasajeros (Escala Logarítmica)', fontsize=12)
plt.ylabel('Frecuencia (Cantidad de registros)', fontsize=12)
plt.tight_layout()
plt.savefig('graficos/graf_vol_pasajeros.png', dpi=300, bbox_inches='tight')
plt.show()

# Gráfico 4: Concentración del Mercado: Oligopolio vs Minorías
plt.figure(figsize=(8, 8))
etiquetas = ['Top 3 Aerolíneas Predominantes', f'Otras {cantidad_otras} Aerolíneas Minoritarias']
valores = [top_3_suma, otras_suma]

plt.pie(
    valores,
    labels=etiquetas,
    autopct='%1.1f%%',
    startangle=90,
    colors=['#ff9999','#66b3ff'],
    explode=(0.05, 0)
)
plt.title('Concentración del Mercado: Oligopolio vs Minorías', fontsize=14, pad=15)
plt.savefig('graficos/Concentracion_Mercado_Minorias.png', dpi=300, bbox_inches='tight')
plt.tight_layout()
plt.show()