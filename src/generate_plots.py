"""
Generador de Gráficos Analíticos de Alta Calidad (300 DPI) para TP2 Puerto Sur (Grupo 8)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

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

out_dir = 'C:/Users/ASUS/.gemini/antigravity/scratch/TP2-IO/plots'

# -------------------------------------------------------------------------
# FIGURA 1: Capacidad Máxima y Nivel de Servicio vs Demanda Diaria (Consigna c)
# -------------------------------------------------------------------------
df_cap = pd.read_csv(f'{out_dir}/capacidad_demanda.csv')

fig, ax1 = plt.subplots(figsize=(9, 5.5), dpi=300)
ax2 = ax1.twinx()

# Líneas de estadía W
l1 = ax1.plot(df_cap['buques_dia'], df_cap['W_3gruas'], 'o-', color='#d9534f', linewidth=2.5, markersize=7, label='Estadía W: 3 Grúas (Actual)')
l2 = ax1.plot(df_cap['buques_dia'], df_cap['W_4gruas'], 's-', color='#0275d8', linewidth=2.5, markersize=7, label='Estadía W: 4 Grúas (Mejora)')
ax1.axhline(16.0, color='#d9534f', linestyle='--', linewidth=1.8, label='Umbral Límite Navieras (16 h)')

# Barras de % buques excedidos
b1 = ax2.plot(df_cap['buques_dia'], df_cap['pct16_3gruas'], '^--', color='#f0ad4e', alpha=0.7, label='% Excede 16h (3 Grúas)')
b2 = ax2.plot(df_cap['buques_dia'], df_cap['pct16_4gruas'], 'v--', color='#5cb85c', alpha=0.7, label='% Excede 16h (4 Grúas)')

ax1.set_xlabel('Demanda Diaria de Buques (buques/día)', fontweight='bold')
ax1.set_ylabel('Estadía Promedio Total W (horas)', fontweight='bold', color='#333333')
ax2.set_ylabel('% Buques con Estadía > 16 horas', fontweight='bold', color='#f0ad4e')
ax1.set_title('Capacidad Operativa y Cumplimiento del Umbral de 16h vs. Demanda Diaria', fontweight='bold', pad=15)

# Puntos de corte para 16h
ax1.axvline(7.45, color='gray', linestyle=':', alpha=0.8)
ax1.text(7.50, 4.0, 'Cap. Máx 3 Grúas\n(~7.45 b/d)', color='#d9534f', fontsize=9, fontweight='bold')

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True)

plt.tight_layout()
plt.savefig(f'{out_dir}/fig1_capacidad_demanda.png', dpi=300)
plt.close()
print("Guardado: fig1_capacidad_demanda.png")

# -------------------------------------------------------------------------
# FIGURA 2: Desglose del Tiempo de Estadía: Espera vs Atención (Consigna b)
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5), dpi=300)

escenarios = ['Operación Actual (3G)', 'Con 4ta Grúa (4G)', 'Crucero Exclusivo', '4 Bermas + 4 Grúas']
wq_vals = [16.32, 9.06, 24.16, 2.74]
ws_vals = [7.92, 7.40, 7.93, 7.40]

bar_width = 0.55
bars_ws = ax.bar(escenarios, ws_vals, width=bar_width, label='Atención en Berma (Ws)', color='#5bc0de', edgecolor='black')
bars_wq = ax.bar(escenarios, wq_vals, width=bar_width, bottom=ws_vals, label='Espera en Rada (Wq)', color='#f0ad4e', edgecolor='black')

# Umbral 16h
ax.axhline(16.0, color='#d9534f', linestyle='--', linewidth=2, label='Umbral Navieras (16 h)')

# Etiquetas de valores
for i in range(len(escenarios)):
    total = ws_vals[i] + wq_vals[i]
    pct_esp = (wq_vals[i] / total) * 100
    ax.text(i, total + 0.6, f"{total:.1f} h\n({pct_esp:.0f}% esp)", ha='center', fontsize=9, fontweight='bold')

ax.set_ylabel('Tiempo Promedio (horas)', fontweight='bold')
ax.set_title('Desglose de Estadía Portuaria: Tiempo en Berma (Ws) vs. Espera en Rada (Wq)', fontweight='bold', pad=15)
ax.set_ylim(0, 38)
ax.legend(loc='upper right', frameon=True)

plt.tight_layout()
plt.savefig(f'{out_dir}/fig2_desglose_estadia.png', dpi=300)
plt.close()
print("Guardado: fig2_desglose_estadia.png")

# -------------------------------------------------------------------------
# FIGURA 3: Análisis de Repago de la 4ta Berma (Consigna g)
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.5, 5), dpi=300)

costos_inmov = np.linspace(15000, 30000, 50)
dias_ahorrados_ano = 5.97 * 365 # ~2.180 días-buque/año
inversion = 12000000.0

ahorros_anuales_M = (dias_ahorrados_ano * costos_inmov) / 1e6
paybacks_meses = (inversion / (ahorros_anuales_M * 1e6)) * 12

ax.plot(costos_inmov / 1000, paybacks_meses, color='#0275d8', linewidth=3)
ax.set_xlabel('Costo de Inmovilización de Buque (miles USD / día)', fontweight='bold')
ax.set_ylabel('Período de Repago (Meses)', fontweight='bold', color='#0275d8')
ax.set_title('Período de Repago de la Inversión en 4ª Berma (USD 12M)', fontweight='bold', pad=15)
ax.grid(True, linestyle='--', alpha=0.6)

# Marcadores de extremos
ax.scatter([15, 30], [paybacks_meses[0], paybacks_meses[-1]], color='#d9534f', zorder=5, s=60)
ax.annotate(f'Repago: {paybacks_meses[0]:.1f} meses\n(USD 15k/día)', (15, paybacks_meses[0]), textcoords="offset points", xytext=(15, 10), fontweight='bold')
ax.annotate(f'Repago: {paybacks_meses[-1]:.1f} meses\n(USD 30k/día)', (30, paybacks_meses[-1]), textcoords="offset points", xytext=(-80, 10), fontweight='bold')

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
