"""
Generador de Gráficos Analíticos de Alta Calidad (300 DPI) para TP2 Puerto Sur (Grupo 8)
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from src.paths import PLOTS_DIR

out_dir = str(PLOTS_DIR)

# Configurar estilo visual limpio y profesional
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 14

# -------------------------------------------------------------------------
# FIGURA 1: Capacidad Máxima y Nivel de Servicio vs Demanda Diaria (Consigna c)
# -------------------------------------------------------------------------
df_cap = pd.read_csv(f'{out_dir}/capacidad_demanda.csv')

fig, ax1 = plt.subplots(figsize=(9, 5.5), dpi=300)
ax2 = ax1.twinx()

# Líneas de estadía W
l1 = ax1.plot(df_cap['buques_dia'], df_cap['W_3gruas'], 'o-', color='#d9534f', linewidth=2.5, markersize=7, label='Estadía W: 3 Grúas (Actual)')
l2 = ax1.plot(df_cap['buques_dia'], df_cap['W_4gruas'], 's-', color='#0275d8', linewidth=2.5, markersize=7, label='Estadía W: 4 Grúas (Mejora)')
l_umbral = ax1.axhline(16.0, color='darkred', linestyle='--', linewidth=2, label='Umbral Crítico Contractual (16h)')

# Barras de % buques excedidos
width = 0.12
b1 = ax2.bar(df_cap['buques_dia'] - width/2, df_cap['pct16_3gruas'], width=width, color='#d9534f', alpha=0.25, label='% Excede 16h (3 Grúas)')
b2 = ax2.bar(df_cap['buques_dia'] + width/2, df_cap['pct16_4gruas'], width=width, color='#0275d8', alpha=0.25, label='% Excede 16h (4 Grúas)')

ax1.set_xlabel('Demanda Diaria de Buques (buques/día)', fontweight='bold')
ax1.set_ylabel('Estadía Promedio en Puerto (Horas)', fontweight='bold')
ax2.set_ylabel('% de Escalas con Estadía > 16 Horas', fontweight='bold')

ax1.set_ylim(0, 30)
ax2.set_ylim(0, 100)

# Unir leyendas
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, framealpha=0.9)

plt.title('Capacidad Portuaria y Nivel de Servicio vs. Demanda Diaria (Grupo 8)', fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(f'{out_dir}/fig1_capacidad_demanda.png', dpi=300)
plt.close()
print("Guardado: fig1_capacidad_demanda.png")

# -------------------------------------------------------------------------
# FIGURA 2: Desglose de Estadía: Ws vs Wq (Consigna b)
# -------------------------------------------------------------------------
df_base = pd.read_csv(f'{out_dir}/resumen_base_vs_4gruas.csv')

fig, ax = plt.subplots(figsize=(8, 5), dpi=300)

configs = ['3 Grúas (Actual)', '4 Grúas (Mejora)']
wq_vals = [df_base.loc[df_base['Config']=='Actual_3G_3B', 'Wq'].values[0], df_base.loc[df_base['Config']=='Mejora_4G_3B', 'Wq'].values[0]]
ws_vals = [df_base.loc[df_base['Config']=='Actual_3G_3B', 'Ws'].values[0], df_base.loc[df_base['Config']=='Mejora_4G_3B', 'Ws'].values[0]]

p1 = ax.bar(configs, ws_vals, width=0.45, label='Tiempo en Berma (Ws) [Atención + Maniobra]', color='#5cb85c')
p2 = ax.bar(configs, wq_vals, width=0.45, bottom=ws_vals, label='Tiempo de Espera en Rada (Wq) [Cola estéril]', color='#f0ad4e')
ax.axhline(16.0, color='darkred', linestyle='--', linewidth=2, label='Umbral Máximo Contractual (16h)')

# Etiquetas de valor
for i in range(2):
    tot = ws_vals[i] + wq_vals[i]
    ax.text(i, ws_vals[i]/2, f"{ws_vals[i]:.2f} h\n({(ws_vals[i]/tot)*100:.1f}%)", ha='center', va='center', color='white', fontweight='bold')
    ax.text(i, ws_vals[i] + wq_vals[i]/2, f"{wq_vals[i]:.2f} h\n({(wq_vals[i]/tot)*100:.1f}%)", ha='center', va='center', color='black', fontweight='bold')
    ax.text(i, tot + 0.6, f"Total: {tot:.2f} h", ha='center', va='bottom', color='black', fontweight='bold', fontsize=11)

ax.set_ylabel('Tiempo Promedio (Horas)', fontweight='bold')
ax.set_ylim(0, 30)
ax.set_title('Desglose del Tiempo de Estadía: Espera en Rada (Wq) vs. Servicio en Berma (Ws)', fontweight='bold', pad=15)
ax.legend(loc='upper right', frameon=True, framealpha=0.9)
plt.tight_layout()
plt.savefig(f'{out_dir}/fig2_desglose_estadia.png', dpi=300)
plt.close()
print("Guardado: fig2_desglose_estadia.png")

# -------------------------------------------------------------------------
# FIGURA 3: Período de Repago de la 4ª Berma vs Costo de Inmovilización (Consigna g)
# -------------------------------------------------------------------------
df_rep = pd.read_csv(f'{out_dir}/matriz_bermas_repago.csv')

fig, ax1 = plt.subplots(figsize=(8.5, 5), dpi=300)

costos = [15000, 20000, 22500, 25000, 30000]
paybacks_meses = [
    (12.0 / (2.53 * (c * 365 / 1e6))) * 12.0 for c in costos
]

l_pb = ax1.plot(costos, paybacks_meses, 'o-', color='#0275d8', linewidth=2.5, markersize=8, label='Período de Repago (Meses)')
ax1.axhline(12.0, color='gray', linestyle=':', label='1 Año (12 meses)')
ax1.axhline(6.0, color='green', linestyle='--', label='Meta Financiera (6 meses)')

ax1.set_xlabel('Costo de Inmovilización del Buque (USD / Día)', fontweight='bold')
ax1.set_ylabel('Plazo de Repago Simple (Meses)', fontweight='bold', color='#0275d8')
ax1.tick_params(axis='y', labelcolor='#0275d8')
ax1.set_ylim(0, 6)

for c, pb in zip(costos, paybacks_meses):
    ax1.annotate(f"{pb:.1f} meses", (c, pb), textcoords="offset points", xytext=(0, 10), ha='center', fontweight='bold', fontsize=9.5)

plt.title('Evaluación de Inversión 4ª Berma (USD 12M): Repago vs. Costo de Buque Detenido', fontweight='bold', pad=15)
ax1.legend(loc='upper right', frameon=True)
plt.tight_layout()
plt.savefig(f'{out_dir}/fig3_repago_berma.png', dpi=300)
plt.close()
print("Guardado: fig3_repago_berma.png")

# -------------------------------------------------------------------------
# FIGURA 4: Test de Tukey HSD (Intervalos de Confianza al 95%)
# -------------------------------------------------------------------------
df_tukey = pd.read_csv(f'{out_dir}/tukey_hsd_resultados.csv')

fig, ax = plt.subplots(figsize=(9, 4.8), dpi=300)

comparaciones = [f"{row['group1']} vs\n{row['group2']}" for _, row in df_tukey.iterrows()]
y_pos = np.arange(len(comparaciones))

ax.errorbar(
    df_tukey['meandiff'], y_pos, 
    xerr=[df_tukey['meandiff'] - df_tukey['lower'], df_tukey['upper'] - df_tukey['meandiff']],
    fmt='o', color='#0275d8', ecolor='#d9534f', elinewidth=2.5, capsize=5, markersize=6
)
ax.axvline(0, color='black', linestyle='--', linewidth=1.5)

ax.set_yticks(y_pos)
ax.set_yticklabels(comparaciones, fontsize=9)
ax.set_xlabel('Diferencia de Medias en Tiempo de Estadía (Horas, IC 95%)', fontweight='bold')
ax.set_title('Test de Tukey HSD (FWER = 0.05) entre Configuraciones Operativas', fontweight='bold', pad=15)

for i, (_, row) in enumerate(df_tukey.iterrows()):
    sig_text = "Significativo (p < 0.05)" if row['reject'] else "No Significativo"
    color_text = "#d9534f" if row['reject'] else "gray"
    ax.text(row['upper'] + 1.0, i, sig_text, va='center', fontsize=8.5, color=color_text, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{out_dir}/fig4_tukey_hsd.png', dpi=300)
plt.close()
print("Guardado: fig4_tukey_hsd.png")
