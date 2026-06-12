# limpiar_analizar_epidemiologia.py (VERSIÓN CORREGIDA)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

print("=" * 70)
print("ANÁLISIS DE DATOS EPIDEMIOLÓGICOS - DEFUNCIONES POR SEMANA")
print("=" * 70)

# 1. Leer datos con separador correcto
print("\n📂 Leyendo archivo...")
df = pd.read_csv('def_semana_epidemiologica.csv', sep='|', encoding='utf-8')

print(f"✅ Datos cargados: {len(df):,} filas × {len(df.columns)} columnas")
print(f"\nColumnas: {df.columns.tolist()}")

# 2. Limpiar nombres de columnas (quitar espacios)
df.columns = df.columns.str.strip()

# 3. Ver tipos de datos originales
print("\n🔍 Tipos de datos originales:")
print(df.dtypes)

# 4. Limpiar caracteres extraños SOLO en columnas de texto
print("\n🧹 Limpiando caracteres extraños...")
columnas_texto = ['GRUPO_EDAD', 'REGION']  # 'SEXO' es numérico

for col in columnas_texto:
    if col in df.columns and df[col].dtype == 'object':
        # Convertir a string primero
        df[col] = df[col].astype(str)
        # Reemplazar caracteres comunes corruptos
        df[col] = df[col].str.replace('Ã¡', 'á', regex=False)
        df[col] = df[col].str.replace('Ã©', 'é', regex=False)
        df[col] = df[col].str.replace('Ã­', 'í', regex=False)
        df[col] = df[col].str.replace('Ã³', 'ó', regex=False)
        df[col] = df[col].str.replace('Ãº', 'ú', regex=False)
        df[col] = df[col].str.replace('Ã±', 'ñ', regex=False)
        df[col] = df[col].str.replace('Â', '', regex=False)
        print(f"   ✅ Limpiada columna: {col}")

# 5. Mapear valores de sexo (si son numéricos)
print("\n⚥ Procesando columna SEXO...")
if 'SEXO' in df.columns:
    if df['SEXO'].dtype in ['int64', 'float64'] or df['SEXO'].astype(str).str.isnumeric().all():
        # Mapear códigos a etiquetas
        sexo_map = {1: 'Hombre', 2: 'Mujer', 0: 'No especificado'}
        df['SEXO_LABEL'] = df['SEXO'].map(sexo_map).fillna('No especificado')
        print(f"   ✅ Valores únicos en SEXO: {df['SEXO'].unique()}")
        print(f"   ✅ Mapeados a: {df['SEXO_LABEL'].unique()}")

# 6. Convertir tipos de datos numéricos
print("\n📊 Convirtiendo tipos de datos...")
df['ANO_ESTADISTICO'] = pd.to_numeric(df['ANO_ESTADISTICO'], errors='coerce')
df['SEMANA_ESTADISTICA'] = pd.to_numeric(df['SEMANA_ESTADISTICA'], errors='coerce')
df['POBLACION'] = pd.to_numeric(df['POBLACION'], errors='coerce')
df['MUERTES_OBS'] = pd.to_numeric(df['MUERTES_OBS'], errors='coerce')

print(f"   Años: {df['ANO_ESTADISTICO'].min():.0f} a {df['ANO_ESTADISTICO'].max():.0f}")
print(f"   Semanas: {df['SEMANA_ESTADISTICA'].min():.0f} a {df['SEMANA_ESTADISTICA'].max():.0f}")

# 7. Estadísticas básicas
print("\n📈 Estadísticas generales:")
total_muertes = df['MUERTES_OBS'].sum()
total_poblacion = df['POBLACION'].sum()
print(f"   Total muertes registradas: {total_muertes:,.0f}")
print(f"   Población total (referencia): {total_poblacion:,.0f}")
print(f"   Tasa de mortalidad global: {total_muertes / total_poblacion * 100000:.2f} por 100,000 hab")

# 8. Análisis por grupo de edad
print("\n👥 Muertes por grupo de edad:")
muertes_edad = df.groupby('GRUPO_EDAD')['MUERTES_OBS'].sum().sort_values(ascending=False)
for edad, muertes in muertes_edad.head(10).items():
    print(f"   {edad}: {muertes:,.0f} muertes")

# 9. Análisis por sexo (usando la etiqueta)
print("\n⚥ Muertes por sexo:")
if 'SEXO_LABEL' in df.columns:
    muertes_sexo = df.groupby('SEXO_LABEL')['MUERTES_OBS'].sum()
else:
    muertes_sexo = df.groupby('SEXO')['MUERTES_OBS'].sum()
for sexo, muertes in muertes_sexo.items():
    print(f"   {sexo}: {muertes:,.0f} muertes")

# 10. Análisis por región
print("\n📍 Top 10 regiones con más muertes:")
muertes_region = df.groupby('REGION')['MUERTES_OBS'].sum().sort_values(ascending=False)
for region, muertes in muertes_region.head(10).items():
    # Limpiar nombre de región si tiene caracteres extraños
    region_limpia = str(region).replace('Ã¡', 'á').replace('Ã³', 'ó').replace('Ã±', 'ñ').replace('Ã©', 'é')
    print(f"   {region_limpia}: {muertes:,.0f} muertes")

# 11. Series temporales (por año)
print("\n📅 Creando serie temporal...")
muertes_anual = df.groupby('ANO_ESTADISTICO')['MUERTES_OBS'].sum().reset_index()
muertes_anual = muertes_anual.dropna()

print("\n📊 Muertes por año (últimos 10):")
print(muertes_anual.tail(10).to_string(index=False))

# 12. Análisis de tendencia anual
print("\n📈 Tendencia anual:")
if len(muertes_anual) > 1:
    from scipy import stats
    slope, intercept, r_value, p_value, std_err = stats.linregress(muertes_anual['ANO_ESTADISTICO'], muertes_anual['MUERTES_OBS'])
    print(f"   Pendiente: {slope:.2f} muertes/año")
    print(f"   R²: {r_value**2:.3f}")
    print(f"   p-valor: {p_value:.4f}")
    if p_value < 0.05:
        print("   ✅ Tendencia estadísticamente significativa")
    else:
        print("   ⚠️ Tendencia NO significativa estadísticamente")

# 13. Guardar datos limpios
print("\n💾 Guardando datos limpios...")
df_limpio = df.dropna(subset=['ANO_ESTADISTICO', 'MUERTES_OBS'])
df_limpio.to_csv('datos_epidemiologia_limpios.csv', index=False)
print(f"✅ Datos limpios guardados: {len(df_limpio):,} filas")

# 14. Crear visualizaciones
print("\n📊 Generando visualizaciones...")
sns.set_style("whitegrid")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Gráfico 1: Muertes por año
ax = axes[0, 0]
if len(muertes_anual) > 1:
    ax.plot(muertes_anual['ANO_ESTADISTICO'], muertes_anual['MUERTES_OBS'], marker='o', linewidth=2)
    ax.set_title('Tendencia de Muertes por Año')
    ax.set_xlabel('Año')
    ax.set_ylabel('Número de muertes')
    ax.grid(True, alpha=0.3)

# Gráfico 2: Muertes por grupo de edad (Top 10)
ax = axes[0, 1]
top_edades = muertes_edad.head(10)
ax.barh(range(len(top_edades)), top_edades.values)
ax.set_yticks(range(len(top_edades)))
ax.set_yticklabels(top_edades.index)
ax.set_title('Muertes por Grupo de Edad (Top 10)')
ax.set_xlabel('Número de muertes')

# Gráfico 3: Muertes por sexo
ax = axes[1, 0]
if 'SEXO_LABEL' in df.columns:
    muertes_sexo.plot(kind='pie', autopct='%1.1f%%', ax=ax, startangle=90)
else:
    df['SEXO'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax, startangle=90)
ax.set_title('Distribución por Sexo')
ax.set_ylabel('')

# Gráfico 4: Top 10 regiones
ax = axes[1, 1]
top_regiones = muertes_region.head(10)
ax.barh(range(len(top_regiones)), top_regiones.values)
ax.set_yticks(range(len(top_regiones)))
# Limpiar nombres de regiones en las etiquetas
etiquetas = [str(r).replace('Ã¡', 'á').replace('Ã³', 'ó').replace('Ã±', 'ñ').replace('Ã©', 'é')[:30] for r in top_regiones.index]
ax.set_yticklabels(etiquetas)
ax.set_title('Top 10 Regiones con más Muertes')
ax.set_xlabel('Número de muertes')

plt.tight_layout()
plt.savefig('analisis_epidemiologico.png', dpi=150, bbox_inches='tight')
print(f"✅ Gráfico guardado: analisis_epidemiologico.png")

# Mostrar gráfico
plt.show()

print("\n" + "=" * 70)
print("🎉 ANÁLISIS COMPLETADO")
print("=" * 70)
print("\nArchivos generados:")
print("   - datos_epidemiologia_limpios.csv")
print("   - analisis_epidemiologico.png")