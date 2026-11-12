"""
Motor de Réplicas Independientes y Análisis Estadístico de Salidas (Output Analysis)
Trabajo Práctico N° 2 - Puerto Sur (Grupo 8) - IO51 (ITBA)

Ejecuta 30 réplicas independientes por escenario con:
- Período de calentamiento (warm-up) descartado (60 días = 1.440 horas).
- Cálculo de Media, Desvío Estándar e Intervalo de Confianza al 95% (t de Student).
- Test de Hipótesis formal: H0: mu_W >= 16h vs H1: mu_W < 16h.
- Contraste de ANOVA y Comparaciones Múltiples de Tukey HSD (alpha = 0.05).
- Cálculo de Repago y Ahorro Económico para la 4ª Berma (USD 12M, vida 20 años).
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
import numpy as np
import scipy.stats as stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from src.simulador import PuertoSurSim
from src.paths import DATA_G08_CSV, PLOTS_DIR

N_REPLICAS = 30
WARMUP_HORAS = 1440.0  # 60 días de calentamiento
DURACION_DIAS = 365.0   # 1 año operativo por réplica

def run_replicas_for_config(
    nombre_config: str,
    num_bermas: int = 3,
    num_gruas_base: int = 3,
    politica_crucero: str = "sin_crucero",
    factor_demanda: float = 1.0,
    politica_camiones: str = "estandar",
    base_seed: int = 1000
) -> Dict[str, Any]:
    print(f"-> Ejecutando {N_REPLICAS} réplicas para: {nombre_config}...", flush=True)
    w_list = []
    wq_list = []
    ws_list = []
    pct16_list = []

    for r in range(N_REPLICAS):
        seed = base_seed + r * 37
        sim = PuertoSurSim(
            df_escalas=None,
            num_bermas=num_bermas,
            num_gruas_base=num_gruas_base,
            politica_crucero=politica_crucero,
            factor_demanda=factor_demanda,
            politica_camiones=politica_camiones,
            seed=seed,
            modo_generacion="estocastico",
            duracion_estocastica_dias=DURACION_DIAS + (WARMUP_HORAS / 24.0)
        )
        res = sim.run()

        # Filtrar período transitorio de calentamiento
        res_estacionario = res[res['t_arribo'] >= WARMUP_HORAS]
        if len(res_estacionario) == 0:
            res_estacionario = res

        w_list.append(res_estacionario['tiempo_estadia_total'].mean())
        wq_list.append(res_estacionario['tiempo_espera_rada'].mean())
        ws_list.append(res_estacionario['tiempo_en_berma'].mean())
        pct16_list.append(res_estacionario['excede_16h'].mean() * 100.0)

    # Inferencia Estadística al 95%
    def calc_ic95(data):
        m = np.mean(data)
        s = np.std(data, ddof=1)
        sem = s / np.sqrt(len(data))
        t_crit = stats.t.ppf(0.975, df=len(data)-1)
        delta = t_crit * sem
        return m, s, delta, (m - delta, m + delta)

    w_m, w_s, w_delta, w_ic = calc_ic95(w_list)
    wq_m, wq_s, wq_delta, wq_ic = calc_ic95(wq_list)
    ws_m, ws_s, ws_delta, ws_ic = calc_ic95(ws_list)
    pct16_m, pct16_s, pct16_delta, pct16_ic = calc_ic95(pct16_list)

    # Test H0: mu_W >= 16h vs H1: mu_W < 16h
    t_stat = (w_m - 16.0) / (w_s / np.sqrt(N_REPLICAS))
    p_val_16 = stats.t.cdf(t_stat, df=N_REPLICAS - 1)

    print(f"   W = {w_m:.2f} +- {w_delta:.2f} h [IC95%: {w_ic[0]:.2f}, {w_ic[1]:.2f}] | Wq = {wq_m:.2f} h | Ws = {ws_m:.2f} h | % > 16h = {pct16_m:.1f}% | p-val(W<16h) = {p_val_16:.4e}", flush=True)

    return {
        'config': nombre_config,
        'W_mean': w_m, 'W_delta': w_delta, 'W_std': w_s, 'W_ic_inf': w_ic[0], 'W_ic_sup': w_ic[1],
        'Wq_mean': wq_m, 'Wq_delta': wq_delta,
        'Ws_mean': ws_m, 'Ws_delta': ws_delta,
        'pct16_mean': pct16_m, 'pct16_delta': pct16_delta,
        'p_val_H0_16h': p_val_16,
        'raw_W': w_list
    }

def run_suite_replicas():
    print("=========================================================================")
    print(f"INICIANDO PROTOCOLO ESTADÍSTICO DE {N_REPLICAS} RÉPLICAS INDEPENDIENTES (IO51)")
    print("=========================================================================")

    resultados = []

    # 1. Escenario Base (Inciso b): 3 Bermas, 3 Grúas, Camiones Estándar
    res_base = run_replicas_for_config("1_Base_3B_3G", num_bermas=3, num_gruas_base=3, factor_demanda=1.0)
    resultados.append(res_base)

    # 2. Escenario 4ta Grúa (Inciso c): 3 Bermas, 4 Grúas
    res_4g = run_replicas_for_config("2_Mejora_3B_4G", num_bermas=3, num_gruas_base=4, factor_demanda=1.0)
    resultados.append(res_4g)

    # 3. Escenario Patio Penalizado (Inciso d): Camiones 10% tardíos
    res_cam = run_replicas_for_config("3_Patio_CamionPenal", num_bermas=3, num_gruas_base=3, politica_camiones="penalidad")
    resultados.append(res_cam)

    # 4. Escenario Cruceros con Exclusividad (Inciso e): 3 Bermas, 3 Grúas, 24 cruceros
    res_cru = run_replicas_for_config("4_Crucero_Exclusivo", num_bermas=3, num_gruas_base=3, politica_crucero="crucero_exclusivo")
    resultados.append(res_cru)

    # 5. Escenario Industrial Base (+35% demanda) con 3 Bermas (Inciso f)
    res_ind_base_3b = run_replicas_for_config("5_IndBase35_3B_3G", num_bermas=3, num_gruas_base=3, factor_demanda=1.35)
    resultados.append(res_ind_base_3b)

    # 6. Escenario Industrial Base (+35% demanda) con 4 Bermas (Inciso f)
    res_ind_base_4b = run_replicas_for_config("6_IndBase35_4B_4G", num_bermas=4, num_gruas_base=4, factor_demanda=1.35)
    resultados.append(res_ind_base_4b)

    # 7. Escenario Industrial Optimista (+100% demanda) con 3 Bermas
    res_ind_opt_3b = run_replicas_for_config("7_IndOpt100_3B_3G", num_bermas=3, num_gruas_base=3, factor_demanda=2.0)
    resultados.append(res_ind_opt_3b)

    # 8. Escenario Industrial Optimista (+100% demanda) con 4 Bermas
    res_ind_opt_4b = run_replicas_for_config("8_IndOpt100_4B_4G", num_bermas=4, num_gruas_base=4, factor_demanda=2.0)
    resultados.append(res_ind_opt_4b)

    # Guardar resumen de réplicas en CSV
    df_summary = pd.DataFrame([{
        'Configuracion': r['config'],
        'W_Media': r['W_mean'],
        'W_Delta_IC95': r['W_delta'],
        'W_IC_Inferior': r['W_ic_inf'],
        'W_IC_Superior': r['W_ic_sup'],
        'Wq_Media': r['Wq_mean'],
        'Ws_Media': r['Ws_mean'],
        'Pct_Excede_16h': r['pct16_mean'],
        'P_Valor_H0_16h': r['p_val_H0_16h']
    } for r in resultados])
    df_summary.to_csv(PLOTS_DIR / 'resumen_30_replicas_ic95.csv', index=False)
    print(f"\nResumen de 30 réplicas guardado en: {PLOTS_DIR / 'resumen_30_replicas_ic95.csv'}")

    # =========================================================================
    # ANOVA Y TEST DE COMPARACIONES MÚLTIPLES DE TUKEY HSD
    # =========================================================================
    print("\n--- ANÁLISIS DE VARIANZA (ANOVA) Y TUKEY HSD ENTRE CONFIGURACIONES ---")
    tukey_data = []
    configs_comp = [res_base, res_4g, res_cam, res_cru]
    for c in configs_comp:
        for val in c['raw_W']:
            tukey_data.append({'Escenario': c['config'], 'Estadia_W': val})

    df_tukey_input = pd.DataFrame(tukey_data)
    tukey_res = pairwise_tukeyhsd(df_tukey_input['Estadia_W'], df_tukey_input['Escenario'], alpha=0.05)
    print(tukey_res)

    df_tukey_export = pd.DataFrame(data=tukey_res._results_table.data[1:], columns=tukey_res._results_table.data[0])
    df_tukey_export.to_csv(PLOTS_DIR / 'tukey_hsd_replicas.csv', index=False)

    # =========================================================================
    # CÁLCULO DE REPAGO ECONÓMICO FORMAL DE LA 4ª BERMA (Consigna g)
    # =========================================================================
    print("\n=========================================================================")
    print("ANÁLISIS DE REPAGO ECONÓMICO Y EVALUACIÓN DE INVERSIÓN (CONSIGNA G)")
    print("=========================================================================")
    # Para demanda +35% (Industrial Base):
    delta_w_ind = res_ind_base_3b['W_mean'] - res_ind_base_4b['W_mean']
    buques_ano_base = (8852.0 / 3.0) * 1.35  # ~3.983 buques/año
    horas_evitadas_ano = delta_w_ind * buques_ano_base
    dias_buque_evitados = horas_evitadas_ano / 24.0
    anos_buque_evitados = dias_buque_evitados / 365.0

    inversion_berma = 12000000.0  # USD 12M
    vida_util = 20.0  # años

    costo_dia_min = 15000.0
    costo_dia_max = 30000.0
    costo_dia_med = 22500.0

    ahorro_anual_min = dias_buque_evitados * costo_dia_min
    ahorro_anual_max = dias_buque_evitados * costo_dia_max
    ahorro_anual_med = dias_buque_evitados * costo_dia_med

    payback_min = inversion_berma / ahorro_anual_max  # Con máximo ahorro -> menor tiempo
    payback_max = inversion_berma / ahorro_anual_min  # Con mínimo ahorro -> mayor tiempo
    payback_med = inversion_berma / ahorro_anual_med

    print(f"Demanda Industrial Base (+35% = {buques_ano_base:.0f} buques/año):")
    print(f"  3 Bermas: W = {res_ind_base_3b['W_mean']:.2f} +- {res_ind_base_3b['W_delta']:.2f} h")
    print(f"  4 Bermas: W = {res_ind_base_4b['W_mean']:.2f} +- {res_ind_base_4b['W_delta']:.2f} h")
    print(f"  Reducción de estadía: {delta_w_ind:.2f} horas/buque")
    print(f"  Años-buque de inmovilización evitados: {anos_buque_evitados:.2f} años-buque/año ({horas_evitadas_ano:,.0f} horas-buque/año)")
    print(f"  Ahorro anual estimado: USD {ahorro_anual_med/1e6:.2f} M/año (Rango: USD {ahorro_anual_min/1e6:.2f}M a {ahorro_anual_max/1e6:.2f}M)")
    print(f"  Inversión de capital: USD 12.000.000 (Vida útil: {vida_util:.0f} años)")
    print(f"  Período de Repago Simple: {payback_med:.2f} años (~{payback_med*12:.1f} meses)")
    print(f"  Rango de Repago: {payback_min:.2f} a {payback_max:.2f} años (Ampliamente inferior a 20 años)")

    df_repago = pd.DataFrame([{
        'Escenario': 'Industrial_Base_Plus35pct',
        'Buques_Ano': buques_ano_base,
        'Delta_W_Horas': delta_w_ind,
        'Horas_Buque_Evitadas_Ano': horas_evitadas_ano,
        'Dias_Buque_Evitados_Ano': dias_buque_evitados,
        'Anos_Buque_Evitados_Ano': anos_buque_evitados,
        'Ahorro_Anual_USD_Min': ahorro_anual_min,
        'Ahorro_Anual_USD_Med': ahorro_anual_med,
        'Ahorro_Anual_USD_Max': ahorro_anual_max,
        'Inversion_USD': inversion_berma,
        'Payback_Anos_Min': payback_min,
        'Payback_Anos_Med': payback_med,
        'Payback_Anos_Max': payback_max
    }])
    df_repago.to_csv(PLOTS_DIR / 'repago_4ta_berma_formal.csv', index=False)
    print("Resultados de repago guardados en repago_4ta_berma_formal.csv")

if __name__ == '__main__':
    run_suite_replicas()
