"""
Ajuste Estadístico Formal y Tests de Bondad de Ajuste (Input Modeling)
TP2 - Simulación "Puerto Sur" (ITBA IO 11.51 - Grupo 8)

Ajusta distribuciones teóricas de probabilidad a:
1. Tiempos entre arribos (Delta t) por servicio regular y global.
2. Carga por buque (mov_dry, mov_reefer, mov_oog) y su estacionalidad (meses 10 a 12).
3. Ejecuta tests formales de Kolmogorov-Smirnov (K-S) con estadístico D y p-valores.
4. Exporta parámetros validados a data/distribuciones_g08.json.
"""

import sys
import os
import json
from pathlib import Path

# Asegurar que la raíz del proyecto esté en sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
import scipy.stats as stats

# Importar rutas portables
from src.paths import DATA_G08_CSV, DISTRIBUTIONS_JSON, DATA_DIR

def fit_distribution_candidates(data, name="Variable"):
    """
    Ajusta distribuciones continuas candidatas y evalúa Kolmogorov-Smirnov.
    Retorna un diccionario ordenado por menor estadístico D (mejor ajuste K-S).
    """
    clean_data = data.dropna()
    clean_data = clean_data[clean_data > 0]
    n = len(clean_data)
    
    candidates = {
        'expon': stats.expon,
        'gamma': stats.gamma,
        'weibull_min': stats.weibull_min,
        'lognorm': stats.lognorm
    }
    
    results = []
    
    for dist_name, dist_obj in candidates.items():
        try:
            # Fit distribution
            params = dist_obj.fit(clean_data)
            
            # K-S Test
            d_stat, p_val = stats.kstest(clean_data, dist_name, args=params)
            
            # Log-Likelihood & AIC
            loglik = np.sum(dist_obj.logpdf(clean_data, *params))
            k_params = len(params)
            aic = 2 * k_params - 2 * loglik
            
            results.append({
                'dist': dist_name,
                'params': [float(p) for p in params],
                'D_stat': float(d_stat),
                'p_value': float(p_val),
                'aic': float(aic),
                'loglik': float(loglik)
            })
        except Exception as e:
            continue
            
    # Ordenar por menor estadístico D (mejor ajuste K-S)
    results = sorted(results, key=lambda x: x['D_stat'])
    return results

def run_input_modeling():
    print("=" * 80)
    print("  AJUSTE ESTADÍSTICO DE ENTRADA Y TESTS DE BONDAD DE AJUSTE (GRUPO 8)")
    print("=" * 80)
    
    df = pd.read_csv(DATA_G08_CSV)
    df['fecha_hora_arribo'] = pd.to_datetime(df['fecha_hora_arribo'])
    df = df.sort_values('fecha_hora_arribo').reset_index(drop=True)
    df['interarrival_hours'] = df['fecha_hora_arribo'].diff().dt.total_seconds() / 3600.0
    df['month'] = df['fecha_hora_arribo'].dt.month
    df['total_mov'] = df['mov_dry'] + df['mov_reefer'] + df['mov_oog']
    
    output_params = {
        "metadata": {
            "dataset": "PuertoSur_escalas_G08.csv",
            "grupo": "Grupo 08",
            "total_escalas": int(len(df)),
            "periodo_inicio": str(df['fecha_hora_arribo'].min()),
            "periodo_fin": str(df['fecha_hora_arribo'].max()),
            "lambda_global_buques_dia": float(len(df) / ((df['fecha_hora_arribo'].max() - df['fecha_hora_arribo'].min()).total_seconds() / (24*3600))),
            "lambda_global_buques_hora": float(len(df) / ((df['fecha_hora_arribo'].max() - df['fecha_hora_arribo'].min()).total_seconds() / 3600))
        },
        "servicios": {},
        "interarribos_global": {},
        "estacionalidad_fruta": {
            "meses_temporada_alta": [10, 11, 12],
            "meses_temporada_baja": [1, 2, 3, 4, 5, 6, 7, 8, 9]
        }
    }
    
    # -------------------------------------------------------------
    # 1. Ajuste de Tiempos Entre Arribos Global
    # -------------------------------------------------------------
    print("\n--- 1. AJUSTE DE INTER-ARRIBOS GLOBAL (Delta t) ---")
    delta_t_all = df['interarrival_hours'].dropna()
    mean_dt = float(delta_t_all.mean())
    std_dt = float(delta_t_all.std())
    cv_dt = float(std_dt / mean_dt)
    print(f"Global: Media = {mean_dt:.3f} h | Desv = {std_dt:.3f} h | CV = {cv_dt:.3f}")
    
    fit_global = fit_distribution_candidates(delta_t_all, "Global Delta t")
    output_params["interarribos_global"] = {
        "media_horas": mean_dt,
        "desv_horas": std_dt,
        "cv": cv_dt,
        "ajustes": fit_global,
        "mejor_ajuste": fit_global[0]
    }
    for r in fit_global:
        print(f"  {r['dist']:<12} | D = {r['D_stat']:.4f} | p-val = {r['p_value']:.4e} | AIC = {r['aic']:.1f}")

    # -------------------------------------------------------------
    # 2. Ajuste de Tiempos Entre Arribos por Servicio
    # -------------------------------------------------------------
    print("\n--- 2. AJUSTE DE INTER-ARRIBOS POR SERVICIO ---")
    servicios = df['servicio'].unique()
    
    for srv in servicios:
        df_srv = df[df['servicio'] == srv].sort_values('fecha_hora_arribo').reset_index(drop=True)
        dt_srv = df_srv['fecha_hora_arribo'].diff().dt.total_seconds() / 3600.0
        dt_srv_clean = dt_srv.dropna()
        
        m_srv = float(dt_srv_clean.mean())
        s_srv = float(dt_srv_clean.std())
        cv_srv = float(s_srv / m_srv)
        prop_srv = float(len(df_srv) / len(df))
        
        print(f"\n[Servicio: {srv}] (N = {len(df_srv)}, Proporción = {prop_srv*100:.1f}%)")
        print(f"  Delta t: Media = {m_srv:.3f} h | Desv = {s_srv:.3f} h | CV = {cv_srv:.3f}")
        
        fit_srv = fit_distribution_candidates(dt_srv_clean, f"Delta t {srv}")
        for r in fit_srv:
            print(f"    {r['dist']:<12} | D = {r['D_stat']:.4f} | p-val = {r['p_value']:.4e} | AIC = {r['aic']:.1f}")
            
        # -------------------------------------------------------------
        # 3. Ajuste de Carga por Servicio (Dry, Reefer, OOG)
        # -------------------------------------------------------------
        # Temporada baja vs alta de fruta para Reefer
        reefer_baja = df_srv[df_srv['month'].isin([1,2,3,4,5,6,7,8,9])]['mov_reefer']
        reefer_alta = df_srv[df_srv['month'].isin([10,11,12])]['mov_reefer']
        
        cargo_summary = {
            "mov_dry": {
                "media": float(df_srv['mov_dry'].mean()),
                "desv": float(df_srv['mov_dry'].std()),
                "min": int(df_srv['mov_dry'].min()),
                "max": int(df_srv['mov_dry'].max()),
                "p25": float(df_srv['mov_dry'].quantile(0.25)),
                "p50": float(df_srv['mov_dry'].quantile(0.50)),
                "p75": float(df_srv['mov_dry'].quantile(0.75))
            },
            "mov_reefer": {
                "general_media": float(df_srv['mov_reefer'].mean()),
                "general_desv": float(df_srv['mov_reefer'].std()),
                "temporada_baja_media": float(reefer_baja.mean()),
                "temporada_baja_desv": float(reefer_baja.std()),
                "temporada_alta_media": float(reefer_alta.mean()),
                "temporada_alta_desv": float(reefer_alta.std())
            },
            "mov_oog": {
                "media": float(df_srv['mov_oog'].mean()),
                "desv": float(df_srv['mov_oog'].std()),
                "min": int(df_srv['mov_oog'].min()),
                "max": int(df_srv['mov_oog'].max())
            },
            "total_mov": {
                "media": float(df_srv['total_mov'].mean()),
                "desv": float(df_srv['total_mov'].std())
            }
        }
        
        # Horas de grúa estimadas para 1 grúa individual
        h_single = (df_srv['mov_dry'] / 28.0) + (df_srv['mov_reefer'] / 21.0) + (df_srv['mov_oog'] / 12.0)
        h_dual = h_single / 1.7
        
        cargo_summary["horas_grua"] = {
            "single_media": float(h_single.mean()),
            "single_desv": float(h_single.std()),
            "dual_media": float(h_dual.mean()),
            "dual_desv": float(h_dual.std())
        }
        
        output_params["servicios"][srv] = {
            "escalas_historicas": int(len(df_srv)),
            "proporcion": prop_srv,
            "interarribos": {
                "media_horas": m_srv,
                "desv_horas": s_srv,
                "cv": cv_srv,
                "ajustes": fit_srv,
                "mejor_ajuste": fit_srv[0]
            },
            "carga": cargo_summary
        }
        
        print(f"  Carga media: Dry = {cargo_summary['mov_dry']['media']:.1f} | Reefer Baja = {cargo_summary['mov_reefer']['temporada_baja_media']:.1f} | Reefer Alta (Fruta) = {cargo_summary['mov_reefer']['temporada_alta_media']:.1f} | OOG = {cargo_summary['mov_oog']['media']:.1f}")
        print(f"  Horas grúa media: 1 Grúa = {cargo_summary['horas_grua']['single_media']:.2f} h | 2 Grúas = {cargo_summary['horas_grua']['dual_media']:.2f} h")

    # Guardar archivo JSON estructurado
    DISTRIBUTIONS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(DISTRIBUTIONS_JSON, 'w', encoding='utf-8') as f:
        json.dump(output_params, f, indent=2, ensure_ascii=False)
        
    print(f"\n[OK] Parámetros y distribuciones exportados exitosamente a:")
    print(f"     {DISTRIBUTIONS_JSON}")
    print("=" * 80)
    return output_params

if __name__ == '__main__':
    run_input_modeling()
