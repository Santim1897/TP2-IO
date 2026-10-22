"""
Suite Completa de Experimentación y Análisis para TP2 Puerto Sur (Grupo 8)
Ejecuta todos los experimentos para responder las consignas (b) a (g).
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from src.simulador import PuertoSurSim
from src.paths import DATA_G08_CSV, PLOTS_DIR
import time
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import scipy.stats as stats

def run_all_experiments():
    df = pd.read_csv(DATA_G08_CSV)
    df['fecha_hora_arribo'] = pd.to_datetime(df['fecha_hora_arribo'])
    
    print("================================================================")
    print("EJECUTANDO BATERÍA DE EXPERIMENTOS COMPLETA - PUERTO SUR (GRUPO 8)")
    print("================================================================")
    
    # -------------------------------------------------------------
    # EXPERIMENTO 1: Consigna (b) y (c) - Operación Actual vs 4ta Grúa
    # -------------------------------------------------------------
    print("\n--- EXPERIMENTO 1: OPERACIÓN ACTUAL VS 4TA GRÚA ---")
    sim_base = PuertoSurSim(df, num_bermas=3, num_gruas_base=3, seed=42)
    res_base = sim_base.run()
    
    sim_4gruas = PuertoSurSim(df, num_bermas=3, num_gruas_base=4, seed=42)
    res_4gruas = sim_4gruas.run()
    
    w_base = res_base['tiempo_estadia_total'].mean()
    wq_base = res_base['tiempo_espera_rada'].mean()
    ws_base = res_base['tiempo_en_berma'].mean()
    pct16_base = res_base['excede_16h'].mean() * 100.0
    
    w_4g = res_4gruas['tiempo_estadia_total'].mean()
    wq_4g = res_4gruas['tiempo_espera_rada'].mean()
    ws_4g = res_4gruas['tiempo_en_berma'].mean()
    pct16_4g = res_4gruas['excede_16h'].mean() * 100.0
    
    print(f"Base (3 Grúas): W = {w_base:.2f} h | Wq = {wq_base:.2f} h | Ws = {ws_base:.2f} h | % > 16h = {pct16_base:.2f}%")
    print(f"Con 4ta Grúa:   W = {w_4g:.2f} h | Wq = {wq_4g:.2f} h | Ws = {ws_4g:.2f} h | % > 16h = {pct16_4g:.2f}%")
    
    # Guardar resultados base
    df_res_base_summary = pd.DataFrame([
        {'Config': 'Actual_3G_3B', 'W': w_base, 'Wq': wq_base, 'Ws': ws_base, 'Pct_Excede_16h': pct16_base},
        {'Config': 'Mejora_4G_3B', 'W': w_4g, 'Wq': wq_4g, 'Ws': ws_4g, 'Pct_Excede_16h': pct16_4g}
    ])
    df_res_base_summary.to_csv(PLOTS_DIR / 'resumen_base_vs_4gruas.csv', index=False)

    # -------------------------------------------------------------
    # EXPERIMENTO 2: Consigna (c) - Barrido de Demanda Diaria Máxima
    # -------------------------------------------------------------
    print("\n--- EXPERIMENTO 2: BARRIDO DE CAPACIDAD MÁXIMA PARA W <= 16 HORAS ---")
    factores = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    demanda_base_diaria = 8.086 # buques / día
    
    capacidad_results = []
    df_sample = df.iloc[:3000].copy()
    
    for f in factores:
        buques_dia = demanda_base_diaria * f
        # Para factores menores a 1.0, submuestreamos proporcionalmente
        df_sub = df_sample.sample(frac=f, random_state=42).sort_values('fecha_hora_arribo').reset_index(drop=True) if f < 1.0 else df_sample
        
        s3 = PuertoSurSim(df_sub, num_bermas=3, num_gruas_base=3, seed=42)
        r3 = s3.run()
        
        s4 = PuertoSurSim(df_sub, num_bermas=3, num_gruas_base=4, seed=42)
        r4 = s4.run()
        
        capacidad_results.append({
            'factor': f,
            'buques_dia': buques_dia,
            'W_3gruas': r3['tiempo_estadia_total'].mean(),
            'pct16_3gruas': r3['excede_16h'].mean() * 100.0,
            'W_4gruas': r4['tiempo_estadia_total'].mean(),
            'pct16_4gruas': r4['excede_16h'].mean() * 100.0
        })
        print(f"Demanda: {buques_dia:.2f} b/d (Factor {f:.1f}) | 3 Grúas: W = {r3['tiempo_estadia_total'].mean():.2f} h (% >16h: {r3['excede_16h'].mean()*100:.1f}%) | 4 Grúas: W = {r4['tiempo_estadia_total'].mean():.2f} h (% >16h: {r4['excede_16h'].mean()*100:.1f}%)")
        
    df_capacidad = pd.DataFrame(capacidad_results)
    df_capacidad.to_csv(PLOTS_DIR / 'capacidad_demanda.csv', index=False)

    # -------------------------------------------------------------
    # EXPERIMENTO 3: Consigna (d) - Políticas de Patio y Camiones
    # -------------------------------------------------------------
    print("\n--- EXPERIMENTO 3: POLÍTICAS DE CAMIONES Y PATIO ---")
    s_cam_std = PuertoSurSim(df_sample, politica_camiones="estandar", seed=42)
    r_cam_std = s_cam_std.run()
    
    s_cam_pen = PuertoSurSim(df_sample, politica_camiones="penalidad", seed=42)
    r_cam_pen = s_cam_pen.run()
    
    s_cam_amp = PuertoSurSim(df_sample, politica_camiones="ventana_amplia", seed=42)
    r_cam_amp = s_cam_amp.run()
    
    print(f"Camiones Estándar (25% tarde):  W = {r_cam_std['tiempo_estadia_total'].mean():.2f} h | Ws = {r_cam_std['tiempo_en_berma'].mean():.2f} h")
    print(f"Camiones Penalizados (10% tarde): W = {r_cam_pen['tiempo_estadia_total'].mean():.2f} h | Ws = {r_cam_pen['tiempo_en_berma'].mean():.2f} h")
    print(f"Camiones Ventana Amplia (15% tarde): W = {r_cam_amp['tiempo_estadia_total'].mean():.2f} h | Ws = {r_cam_amp['tiempo_en_berma'].mean():.2f} h")

    # -------------------------------------------------------------
    # EXPERIMENTO 4: Consigna (e) - Impacto de Cruceros
    # -------------------------------------------------------------
    print("\n--- EXPERIMENTO 4: TEMPORADA DE CRUCEROS ---")
    s_no_cru = PuertoSurSim(df_sample, politica_crucero="sin_crucero", seed=42)
    r_no_cru = s_no_cru.run()
    
    s_cru_noexcl = PuertoSurSim(df_sample, politica_crucero="crucero_sin_exclusividad", seed=42)
    r_cru_noexcl = s_cru_noexcl.run()
    
    s_cru_excl = PuertoSurSim(df_sample, politica_crucero="crucero_exclusivo", seed=42)
    r_cru_excl = s_cru_excl.run()
    
    delta_w_excl = r_cru_excl['tiempo_estadia_total'].mean() - r_no_cru['tiempo_estadia_total'].mean()
    horas_demora_anual = delta_w_excl * (8852.0 / 3.0) # para 1 año (~2.950 buques)
    
    # 2 escalas/sem x 12 sem = 24 escalas de crucero
    n_escalas_crucero = 24
    ingreso_crucero_total = n_escalas_crucero * 60000.0 # USD 1.440.000
    
    # Costo buque detenido: USD 15.000 a 30.000 / día (USD 625 a 1.250 / h)
    costo_inmov_min = horas_demora_anual * (15000.0 / 24.0)
    costo_inmov_max = horas_demora_anual * (30000.0 / 24.0)
    
    canon_minimo_requerido = costo_inmov_min / n_escalas_crucero
    canon_maximo_requerido = costo_inmov_max / n_escalas_crucero
    
    print(f"Sin Cruceros:              W = {r_no_cru['tiempo_estadia_total'].mean():.2f} h")
    print(f"Cruceros Sin Exclusividad: W = {r_cru_noexcl['tiempo_estadia_total'].mean():.2f} h")
    print(f"Cruceros Con Exclusividad: W = {r_cru_excl['tiempo_estadia_total'].mean():.2f} h")
    print(f"Incremento medio estadía buques de carga: +{delta_w_excl:.2f} h/buque")
    print(f"Demora total generada a la flota de carga: {horas_demora_anual:,.1f} horas/año")
    print(f"Costo de inmovilización generado: USD {costo_inmov_min:,.0f} a USD {costo_inmov_max:,.0f} por temporada")
    print(f"Canon ofrecido por crucero: USD 60.000")
    print(f"Canon mínimo para no perder dinero: USD {canon_minimo_requerido:,.0f} a USD {canon_maximo_requerido:,.0f} por escala")

    # -------------------------------------------------------------
    # EXPERIMENTO 5: Consigna (f) y (g) - Proyecto Industrial y 4ta Berma
    # -------------------------------------------------------------
    print("\n--- EXPERIMENTO 5: PROYECTO INDUSTRIAL Y EVALUACIÓN DE 4TA BERMA ---")
    # Bajo demanda actual, la 4ta berma alivia colas
    s_b3_act = PuertoSurSim(df_sample, num_bermas=3, num_gruas_base=3, seed=42)
    r_b3_act = s_b3_act.run()
    
    s_b4_act = PuertoSurSim(df_sample, num_bermas=4, num_gruas_base=4, seed=42)
    r_b4_act = s_b4_act.run()
    
    delta_w_act = r_b3_act['tiempo_estadia_total'].mean() - r_b4_act['tiempo_estadia_total'].mean()
    buques_ano_act = 8852.0 / 3.0 # 2950.7 buques/año
    horas_ahorradas_act = delta_w_act * buques_ano_act
    dias_buque_act = horas_ahorradas_act / 24.0
    anos_buque_act = dias_buque_act / 365.0
    
    ahorro_act_min = dias_buque_act * 15000.0
    ahorro_act_max = dias_buque_act * 30000.0
    ahorro_act_med = dias_buque_act * 22500.0
    
    inversion_berma = 12000000.0 # USD 12M
    payback_act = inversion_berma / ahorro_act_med
    
    print(f"Actual (2.951 buques/año):")
    print(f"  3 Bermas: W = {r_b3_act['tiempo_estadia_total'].mean():.2f} h | 4 Bermas: W = {r_b4_act['tiempo_estadia_total'].mean():.2f} h")
    print(f"  Ahorro: {delta_w_act:.2f} h/buque ({anos_buque_act:.2f} años-buque evitados/año)")
    print(f"  Ahorro anual: USD {ahorro_act_med/1e6:.2f} M/año (Rango: {ahorro_act_min/1e6:.2f}M - {ahorro_act_max/1e6:.2f}M)")
    print(f"  Payback estimado: {payback_act:.2f} años (Rango: {inversion_berma/ahorro_act_max:.2f} a {inversion_berma/ahorro_act_min:.2f} años)")

    # -------------------------------------------------------------
    # TEST DE HIPÓTESIS Y TUKEY HSD
    # -------------------------------------------------------------
    print("\n--- TEST ESTADÍSTICO DE TUKEY HSD ---")
    data_tukey = []
    for w in res_base['tiempo_estadia_total'].iloc[:1500]:
        data_tukey.append({'Escenario': '1_Actual_3G_3B', 'Estadia': w})
    for w in res_4gruas['tiempo_estadia_total'].iloc[:1500]:
        data_tukey.append({'Escenario': '2_Mejora_4G_3B', 'Estadia': w})
    for w in r_cru_excl['tiempo_estadia_total'].iloc[:1500]:
        data_tukey.append({'Escenario': '3_Crucero_Excl', 'Estadia': w})
    for w in r_cam_pen['tiempo_estadia_total'].iloc[:1500]:
        data_tukey.append({'Escenario': '4_Camion_Penal', 'Estadia': w})
        
    df_tukey = pd.DataFrame(data_tukey)
    tukey = pairwise_tukeyhsd(df_tukey['Estadia'], df_tukey['Escenario'], alpha=0.05)
    print(tukey)
    
    # Guardar resumen de Tukey en CSV
    df_tukey_res = pd.DataFrame(data=tukey._results_table.data[1:], columns=tukey._results_table.data[0])
    df_tukey_res.to_csv(PLOTS_DIR / 'tukey_hsd_resultados.csv', index=False)
    
    print("\n=== EXPERIMENTOS CONCLUIDOS EXITOSAMENTE ===")

if __name__ == '__main__':
    run_all_experiments()
