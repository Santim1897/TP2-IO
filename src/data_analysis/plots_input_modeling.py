"""
Generador de Figuras de Input Modeling (Análisis de Datos) para TP2 Puerto Sur (Grupo 8)
Genera las 3 figuras requeridas por la cátedra en alta resolución (300 DPI):
1. fig_input_escalas_mensuales.png: Serie temporal mensual y detección de la brecha de 26.33 días (Abril 2024).
2. fig_input_estacionalidad_reefer.png: Estacionalidad de fruta en contenedores reefer (Octubre-Diciembre vs resto del año).
3. fig_input_arribos_por_turno.png: Distribución horaria por turno (Diurno, Vespertino, Nocturno) y comparación de preservación bajo mayor demanda.
"""

import sys
import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Rutas portables
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_CSV = BASE_DIR / "data" / "PuertoSur_escalas_G08.csv"
PLOTS_DIR = BASE_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# Estilo visual limpio y profesional
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 10.5
plt.rcParams['axes.labelsize'] = 11.5
plt.rcParams['axes.titlesize'] = 12.5
plt.rcParams['xtick.labelsize'] = 9.5
plt.rcParams['ytick.labelsize'] = 9.5
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 13.5

# Cargar dataset
df = pd.read_csv(DATA_CSV)
df['fecha_hora_arribo'] = pd.to_datetime(df['fecha_hora_arribo'])

# =========================================================================
# FIGURA 1: Escalas por Mes (2023-2026) y Brecha de Registro en Abril 2024
# =========================================================================
df['year_month'] = df['fecha_hora_arribo'].dt.to_period('M')
monthly_counts = df['year_month'].value_counts().sort_index()

months_str = [f"{str(m)[2:]}" for m in monthly_counts.index]
counts = monthly_counts.values

fig, ax = plt.subplots(figsize=(11, 5.2), dpi=300)

# Colores: resaltar Abril 2024
colors = ['#d9534f' if str(m) == '2024-04' else '#1F4E79' for m in monthly_counts.index]
bars = ax.bar(range(len(counts)), counts, color=colors, width=0.72, edgecolor='black', linewidth=0.5)

# Anotación en Abril 2024
idx_apr24 = [i for i, m in enumerate(monthly_counts.index) if str(m) == '2024-04'][0]
ax.annotate(
    'Brecha de registros:\n25/03/2024 – 21/04/2024\n(26,33 días sin escalas / 94 escalas)',
    xy=(idx_apr24, counts[idx_apr24]),
    xytext=(idx_apr24 - 4, counts[idx_apr24] + 95),
    arrowprops=dict(facecolor='#d9534f', shrink=0.08, width=1.5, headwidth=7),
    fontweight='bold', fontsize=9.5, color='#a94442',
    bbox=dict(boxstyle="round,pad=0.4", fc="#f2dede", ec="#ebccd1", lw=1)
)

# Línea de media histórica excluyendo la brecha
mean_regular = monthly_counts[monthly_counts.index != '2024-04'].mean()
ax.axhline(mean_regular, color='#f0ad4e', linestyle='--', linewidth=1.8, label=f'Promedio mensual regular (~{mean_regular:.0f} escalas/mes)')

ax.set_xticks(range(0, len(counts), 2))
ax.set_xticklabels([months_str[i] for i in range(0, len(counts), 2)], rotation=45, ha='right')
ax.set_xlabel('Mes de Operación (Año-Mes)', fontweight='bold')
ax.set_ylabel('Cantidad de Escalas Registradas', fontweight='bold')
ax.set_ylim(0, 350)
ax.set_title('Distribución Temporal de Escalas Registradas (2023–2026) — Grupo 08', fontweight='bold', pad=15)
ax.legend(loc='upper right', frameon=True, framealpha=0.95)

plt.tight_layout()
out_fig1 = PLOTS_DIR / 'fig_input_escalas_mensuales.png'
plt.savefig(out_fig1, dpi=300)
plt.close()
print(f"Guardado: {out_fig1}")

# =========================================================================
# FIGURA 2: Estacionalidad en Contenedores Reefer (Fruta: Octubre a Diciembre)
# =========================================================================
df['month'] = df['fecha_hora_arribo'].dt.month
reefer_by_month = df.groupby('month')['mov_reefer'].mean()
meses_nombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

fig, ax = plt.subplots(figsize=(9, 5), dpi=300)

# Colores: resaltar temporada alta de fruta (Oct-Dic)
colors_reefer = ['#f0ad4e' if m in [10, 11, 12] else '#2F5597' for m in range(1, 13)]
bars_r = ax.bar(meses_nombres, reefer_by_month.values, color=colors_reefer, width=0.65, edgecolor='black', linewidth=0.5)

# Valores sobre barras
for bar in bars_r:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.8, f"{yval:.1f}", ha='center', va='bottom', fontsize=9.5, fontweight='bold')

mean_resto = df[~df['month'].isin([10, 11, 12])]['mov_reefer'].mean()
mean_fruta = df[df['month'].isin([10, 11, 12])]['mov_reefer'].mean()
ax.axhline(mean_resto, color='#2F5597', linestyle=':', linewidth=1.5, label=f'Promedio regular (Ene-Sep): {mean_resto:.1f} reefer/escala')
ax.axhline(mean_fruta, color='#d9534f', linestyle='--', linewidth=1.8, label=f'Temporada Frutícola (Oct-Dic): {mean_fruta:.1f} reefer/escala (+55%)')

ax.set_xlabel('Mes del Año', fontweight='bold')
ax.set_ylabel('Movimientos Reefer Promedio por Buque', fontweight='bold')
ax.set_ylim(0, 58)
ax.set_title('Estacionalidad de Carga Refrigerada (Cosecha de Fruta) — Grupo 08', fontweight='bold', pad=15)
ax.legend(loc='upper left', frameon=True, framealpha=0.95)

plt.tight_layout()
out_fig2 = PLOTS_DIR / 'fig_input_estacionalidad_reefer.png'
plt.savefig(out_fig2, dpi=300)
plt.close()
print(f"Guardado: {out_fig2}")

# =========================================================================
# FIGURA 3: Distribución de Arribos por Turno y Preservación de Patrón Horario
# =========================================================================
df['hour'] = df['fecha_hora_arribo'].dt.hour
def clasificar_turno(h):
    if 0 <= h < 8: return 'Nocturno (00-08)'
    elif 8 <= h < 16: return 'Diurno (08-16)'
    else: return 'Vespertino (16-24)'

df['turno'] = df['hour'].apply(clasificar_turno)
prop_hist = df['turno'].value_counts(normalize=True).loc[['Nocturno (00-08)', 'Diurno (08-16)', 'Vespertino (16-24)']] * 100.0

# Comparación con compresión errónea cruda (hallada por Santi: Noche pasa a 33.3% con x1.35 y a 34.0% con x2.0)
prop_comp_135 = [33.27, 34.17, 32.56]
prop_comp_200 = [34.00, 27.13, 38.88]

fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=300)
x = np.arange(3)
width = 0.25

rects1 = ax.bar(x - width, prop_hist.values, width, label='Histórico Real (Calibrado)', color='#1F4E79')
rects2 = ax.bar(x, prop_comp_135, width, label='Compresión Errónea (Factor 1.35x)', color='#0275d8', alpha=0.7)
rects3 = ax.bar(x + width, prop_comp_200, width, label='Compresión Errónea (Factor 2.00x)', color='#f0ad4e', alpha=0.85)

for rects in [rects1, rects2, rects3]:
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2.0, h + 0.6, f"{h:.1f}%", ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_xticks(x)
ax.set_xticklabels(['Nocturno\n(00:00 – 08:00)', 'Diurno\n(08:00 – 16:00)', 'Vespertino\n(16:00 – 24:00)'], fontweight='bold')
ax.set_ylabel('Proporción de Arribos (%)', fontweight='bold')
ax.set_ylim(0, 56)
ax.set_title('Efecto de la Compresión Temporal sobre la Distribución de Arribos por Turno', fontweight='bold', pad=15)
ax.legend(loc='upper right', frameon=True, framealpha=0.95)

# Cuadro explicativo
ax.text(0.5, 48, 'La compresión lineal simple distorsiona los turnos aumentando artificialmente\nlos arribos nocturnos (+10.5%). El generador corregido preserva el patrón empírico.',
        ha='center', va='center', fontsize=9, style='italic',
        bbox=dict(boxstyle="round,pad=0.5", fc="#eef5fb", ec="#b8d4ee", lw=1))

plt.tight_layout()
out_fig3 = PLOTS_DIR / 'fig_input_arribos_por_turno.png'
plt.savefig(out_fig3, dpi=300)
plt.close()
print(f"Guardado: {out_fig3}")
print("=== Figuras de Input Modeling generadas exitosamente ===")
