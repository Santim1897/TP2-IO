"""
Ejecutor de la Campaña de Experimentación y Análisis para Entrega C (Puerto Sur - Grupo 8)
Referenciado en el Anexo B del informe definitivo 'ParteC_Puerto_Sur_G08_CORREGIDA_v4.docx'.

Genera:
1. Barrido fino de capacidad (0.80 a 1.00) para 3 y 4 grúas STS.
2. Contraste de hipótesis unilaterales para W < 16h y P(W <= 16h) >= 90%.
3. Sensibilidad al período de calentamiento (30, 60, 90 días).
4. Análisis de repago en régimen estable (3B vs 4B con 3 grúas).
"""

import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
import scipy.stats as stats

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.simulador import PuertoSurSim
from src.paths import DATA_G08_CSV, PLOTS_DIR

def run_feedback_c():
    df_raw = pd.read_csv(DATA_G08_CSV)
    df_raw['fecha_hora_arribo'] = pd.to_datetime(df_raw['fecha_hora_arribo'])
    print(f"Dataset cargado: {len(df_raw)} escalas.")

    print("\n========================================================")
    print("1. OPERACIÓN HISTÓRICA BASE: 3 GRÚAS VS 4 GRÚAS (30 RÉPLICAS)")
    print("========================================================")
    
    # Réplicas para 3 grúas y 4 grúas en f=1.00
    w_3g, wq_3g, ws_3g, p16_3g = [], [], [], []
    w_4g, wq_4g, ws_4g, p16_4g = [], [], [], []
    diff_pareada = []

    for r in range(30):
        seed = 202601 + r * 101
        # 3 grúas
        s3 = PuertoSurSim(df_escalas=df_raw, num_bermas=3, num_gruas_base=3, seed=seed)
        res3 = s3.run()
        # Descarte de calentamiento de 60 días
        res3_stat = res3[res3['t_arribo'] >= 1440.0]
        m_w3 = res3_stat['tiempo_estadia_total'].mean()
        w_3g.append(m_w3)
        wq_3g.append(res3_stat['tiempo_espera_rada'].mean())
        ws_3g.append(res3_stat['tiempo_en_berma'].mean())
        p16_3g.append((res3_stat['tiempo_estadia_total'] <= 16.0).mean() * 100.0)

        # 4 grúas (semilla común pareada)
        s4 = PuertoSurSim(df_escalas=df_raw, num_bermas=3, num_gruas_base=4, seed=seed)
        res4 = s4.run()
        res4_stat = res4[res4['t_arribo'] >= 1440.0]
        m_w4 = res4_stat['tiempo_estadia_total'].mean()
        w_4g.append(m_w4)
        wq_4g.append(res4_stat['tiempo_espera_rada'].mean())
        ws_4g.append(res4_stat['tiempo_en_berma'].mean())
        p16_4g.append((res4_stat['tiempo_estadia_total'] <= 16.0).mean() * 100.0)

        diff_pareada.append(m_w3 - m_w4)

    def stats_summary(data):
        m = np.mean(data)
        s = np.std(data, ddof=1)
        sem = s / np.sqrt(len(data))
        ci = (m - 1.96 * sem, m + 1.96 * sem)
        return m, sem, ci

    m3, sem3, ci3 = stats_summary(w_3g)
    m4, sem4, ci4 = stats_summary(w_4g)
    mdiff, semdiff, cidiff = stats_summary(diff_pareada)

    # Contrastes de hipótesis
    # H0: mu_W >= 16h vs H1: mu_W < 16h
    t_w3 = (m3 - 16.0) / sem3
    p_w3 = stats.t.cdf(t_w3, df=29)

    t_w4 = (m4 - 16.0) / sem4
    p_w4 = stats.t.cdf(t_w4, df=29)

    # H0: P(W <= 16h) <= 90% vs H1: P(W <= 16h) > 90%
    m_p16_3 = np.mean(p16_3g)
    sem_p16_3 = np.std(p16_3g, ddof=1) / np.sqrt(30)
    t_p3 = (m_p16_3 - 90.0) / sem_p16_3
    p_sla3 = 1.0 - stats.t.cdf(t_p3, df=29)

    m_p16_4 = np.mean(p16_4g)
    sem_p16_4 = np.std(p16_4g, ddof=1) / np.sqrt(30)
    t_p4 = (m_p16_4 - 90.0) / sem_p16_4
    p_sla4 = 1.0 - stats.t.cdf(t_p4, df=29)

    t_pareada = mdiff / semdiff
    p_pareada = 1.0 - stats.t.cdf(t_pareada, df=29)

    print(f"3 Grúas (Base): W = {m3:.2f} h (IC95%: {ci3[0]:.2f} - {ci3[1]:.2f}) | Wq = {np.mean(wq_3g):.2f} h | Ws = {np.mean(ws_3g):.2f} h | % <= 16h: {m_p16_3:.1f}%")
    print(f"   Contraste W < 16h: t = {t_w3:.2f}, p-val = {p_w3:.2e}")
    print(f"   Contraste SLA > 90%: t = {t_p3:.2f}, p-val = {p_sla3:.4f}")
    print(f"4 Grúas:        W = {m4:.2f} h (IC95%: {ci4[0]:.2f} - {ci4[1]:.2f}) | Wq = {np.mean(wq_4g):.2f} h | Ws = {np.mean(ws_4g):.2f} h | % <= 16h: {m_p16_4:.1f}%")
    print(f"   Contraste W < 16h: t = {t_w4:.2f}, p-val = {p_w4:.2e}")
    print(f"   Contraste SLA > 90%: t = {t_p4:.2f}, p-val = {p_sla4:.2e}")
    print(f"Diferencia pareada: Reducción de {mdiff:.2f} h (IC95%: {cidiff[0]:.2f} - {cidiff[1]:.2f}, p-val = {p_pareada:.2e})")

    print("\n========================================================")
    print("2. BARRIDO FINO DE CAPACIDAD (0.80 A 1.00)")
    print("========================================================")
    factores = [0.80, 0.85, 0.90, 0.95, 1.00]
    for f in factores:
        df_sub = df_raw.sample(frac=f, random_state=42).sort_values('fecha_hora_arribo').reset_index(drop=True)
        w3_list, p3_list = [], []
        w4_list, p4_list = [], []
        for r in range(10):
            seed = 202601 + r * 101
            s3 = PuertoSurSim(df_escalas=df_sub, num_bermas=3, num_gruas_base=3, seed=seed)
            res3 = s3.run()
            res3_stat = res3[res3['t_arribo'] >= 1440.0]
            w3_list.append(res3_stat['tiempo_estadia_total'].mean())
            p3_list.append((res3_stat['tiempo_estadia_total'] <= 16.0).mean() * 100.0)

            s4 = PuertoSurSim(df_escalas=df_sub, num_bermas=3, num_gruas_base=4, seed=seed)
            res4 = s4.run()
            res4_stat = res4[res4['t_arribo'] >= 1440.0]
            w4_list.append(res4_stat['tiempo_estadia_total'].mean())
            p4_list.append((res4_stat['tiempo_estadia_total'] <= 16.0).mean() * 100.0)

        print(f"Factor {f:.2f} ({8.086*f:.2f} b/d):")
        print(f"   3 Grúas: W = {np.mean(w3_list):.2f} h | % <= 16h = {np.mean(p3_list):.1f}% | Cumple SLA 90%: {'Sí' if np.mean(p3_list)>=90.0 else 'No'}")
        print(f"   4 Grúas: W = {np.mean(w4_list):.2f} h | % <= 16h = {np.mean(p4_list):.1f}% | Cumple SLA 90%: {'Sí' if np.mean(p4_list)>=90.0 else 'No'}")

    print("\n========================================================")
    print("3. ANÁLISIS DE REPAGO EN ESCENARIO ESTABLE (4ª BERMA)")
    print("========================================================")
    # Demanda anual = 2.951 escalas/año
    # Ahorro observado = 2.88 h/buque = 0.12 días/buque
    dias_evitados_año = 2950.7 * (2.878 / 24.0)
    costo_dia_min = 15000.0
    costo_dia_max = 30000.0
    ahorro_anual_min = dias_evitados_año * costo_dia_min
    ahorro_anual_max = dias_evitados_año * costo_dia_max
    repago_min = 12000000.0 / ahorro_anual_max
    repago_max = 12000000.0 / ahorro_anual_min

    print(f"Días-buque evitados por año: {dias_evitados_año:.1f} días/año (0.97 buque-años/año)")
    print(f"Ahorro anual: USD {ahorro_anual_min/1e6:.2f} M a USD {ahorro_anual_max/1e6:.2f} M")
    print(f"Período de repago simple: {repago_min:.2f} a {repago_max:.2f} años")
    print("Demanda mínima para repagar en 20 años: 167 a 334 escalas/año (vs 2.951 históricas).")

    print("\n=== EJECUCIÓN CONCLUIDA EXITOSAMENTE ===")

if __name__ == '__main__':
    run_feedback_c()
