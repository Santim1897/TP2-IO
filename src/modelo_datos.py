"""Cuantifica los datos G08 y calcula referencias a priori de teoría de colas.

Uso desde la raíz del repositorio:
    python -m src.modelo_datos

Las salidas son descriptivas y analíticas. Las estimaciones de colas no
reemplazan al simulador físico: sus hipótesis se explicitan en el JSON.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd

from src.paths import DATA_G08_CSV, DATA_DIR, DISTRIBUTIONS_JSON, PLOTS_DIR


REQUIRED_COLUMNS = {
    "id_escala",
    "fecha_hora_arribo",
    "servicio",
    "mov_dry",
    "mov_reefer",
    "mov_oog",
}
SERVICE_ORDER = ["Austral Feeder", "Andes Container Line", "TransPatagonia Line"]
CRANE_RATES = {"dry": 28.0, "reefer": 21.0, "oog": 12.0}
BERTHS = 3
MANEUVER_REFERENCE_H = 1.5


def erlang_c(lambd: float, mean_service_h: float, servers: int) -> dict[str, float | str]:
    """Calcula M/M/c con Erlang C en estado estable."""
    if lambd <= 0 or mean_service_h <= 0 or servers < 1:
        raise ValueError("lambda, tiempo de servicio y cantidad de servidores deben ser positivos")

    mu = 1.0 / mean_service_h
    rho = lambd / (servers * mu)
    if rho >= 1.0:
        return {"status": "unstable", "rho": rho}

    offered_load = lambd / mu
    base_sum = sum(offered_load**k / math.factorial(k) for k in range(servers))
    tail = (offered_load**servers) / (math.factorial(servers) * (1.0 - rho))
    p0 = 1.0 / (base_sum + tail)
    p_wait = tail * p0
    lq = p_wait * rho / (1.0 - rho)
    wq = lq / lambd
    w = wq + mean_service_h
    return {
        "status": "stable",
        "servers": servers,
        "lambda_per_h": lambd,
        "mu_per_h": mu,
        "rho": rho,
        "p_wait": p_wait,
        "mean_service_h": mean_service_h,
        "wq_h": wq,
        "w_h": w,
        "lq_vessels": lq,
        "l_vessels": lambd * w,
    }


def allen_cunneen(
    mmc: dict[str, float | str], cv_arrival: float, cv_service: float
) -> dict[str, float]:
    """Aproximación G/G/c de Allen-Cunneen usando M/M/c como referencia."""
    if mmc.get("status") != "stable":
        raise ValueError("Allen-Cunneen requiere una referencia M/M/c estable")
    ca2 = cv_arrival**2
    cs2 = cv_service**2
    wq = float(mmc["wq_h"]) * (ca2 + cs2) / 2.0
    mean_service_h = float(mmc["mean_service_h"])
    lambd = float(mmc["lambda_per_h"])
    return {
        "cv_arrival": cv_arrival,
        "cv_service": cv_service,
        "wq_h": wq,
        "w_h": wq + mean_service_h,
        "lq_vessels": lambd * wq,
        "l_vessels": lambd * (wq + mean_service_h),
    }


def _fit_diagnostics() -> dict[str, Any]:
    """Lee los ajustes existentes solo como diagnóstico exploratorio."""
    if not DISTRIBUTIONS_JSON.exists():
        return {"available": False, "note": "No existe distribuciones_g08.json."}
    with DISTRIBUTIONS_JSON.open(encoding="utf-8") as file:
        fits = json.load(file)

    summary: dict[str, Any] = {"available": True, "global": {}, "by_service": {}}
    global_fit = fits.get("interarribos_global", {}).get("mejor_ajuste", {})
    if global_fit:
        summary["global"] = {
            "distribution_ranked_first": global_fit.get("dist"),
            "ks_d": global_fit.get("D_stat"),
            "ks_p_nominal": global_fit.get("p_value"),
        }
    for service, values in fits.get("servicios", {}).items():
        fit = values.get("interarribos", {}).get("mejor_ajuste", {})
        if fit:
            summary["by_service"][service] = {
                "distribution_ranked_first": fit.get("dist"),
                "ks_d": fit.get("D_stat"),
                "ks_p_nominal": fit.get("p_value"),
            }
    summary["caution"] = (
        "Los p-valores K-S convencionales no se interpretan como aceptación formal: "
        "los parámetros se estimaron con la misma muestra; se requiere calibración "
        "por bootstrap y análisis temporal/estacional."
    )
    return summary


def build_summary(csv_path: Path = DATA_G08_CSV) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    df = pd.read_csv(csv_path)
    missing_columns = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing_columns:
        raise ValueError(f"Faltan columnas requeridas: {missing_columns}")
    if df.empty:
        raise ValueError("El archivo de escalas no contiene registros.")

    df["fecha_hora_arribo"] = pd.to_datetime(df["fecha_hora_arribo"], errors="coerce")
    numeric_columns = ["mov_dry", "mov_reefer", "mov_oog"]
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce")
    if df["fecha_hora_arribo"].isna().any() or df[numeric_columns].isna().any().any():
        raise ValueError("Hay fechas o movimientos ausentes/no numéricos.")
    if df["id_escala"].duplicated().any():
        raise ValueError("id_escala debe ser único.")
    if (df[numeric_columns] < 0).any().any():
        raise ValueError("Los movimientos no pueden ser negativos.")

    df = df.sort_values("fecha_hora_arribo").reset_index(drop=True)
    interarrival_h = df["fecha_hora_arribo"].diff().dt.total_seconds().dropna() / 3600.0
    if (interarrival_h < 0).any():
        raise ValueError("Los arribos no pueden retroceder en el tiempo tras ordenar.")

    start = df["fecha_hora_arribo"].min()
    end = df["fecha_hora_arribo"].max()
    span_h = (end - start).total_seconds() / 3600.0
    if span_h <= 0:
        raise ValueError("El período observado debe ser positivo.")
    lambd = len(df) / span_h

    df["total_mov"] = df[numeric_columns].sum(axis=1)
    df["mes"] = df["fecha_hora_arribo"].dt.month
    df["horas_grua_1"] = (
        df["mov_dry"] / CRANE_RATES["dry"]
        + df["mov_reefer"] / CRANE_RATES["reefer"]
        + df["mov_oog"] / CRANE_RATES["oog"]
    )
    df["servicio_berma_1grua"] = df["horas_grua_1"] + MANEUVER_REFERENCE_H

    service_summary: dict[str, Any] = {}
    for service in SERVICE_ORDER:
        group = df[df["servicio"] == service].copy()
        if group.empty:
            continue
        service_interarrival_h = (
            group["fecha_hora_arribo"].diff().dt.total_seconds().dropna() / 3600.0
        )
        service_work_h = group["horas_grua_1"]
        service_summary[service] = {
            "arrivals": int(len(group)),
            "share": float(len(group) / len(df)),
            "interarrival_mean_h": float(service_interarrival_h.mean()),
            "interarrival_sd_h": float(service_interarrival_h.std()),
            "interarrival_cv": float(service_interarrival_h.std() / service_interarrival_h.mean()),
            "moves_mean": {
                "dry": float(group["mov_dry"].mean()),
                "reefer": float(group["mov_reefer"].mean()),
                "oog": float(group["mov_oog"].mean()),
                "total": float(group["total_mov"].mean()),
            },
            "moves_sd": {
                "dry": float(group["mov_dry"].std()),
                "reefer": float(group["mov_reefer"].std()),
                "oog": float(group["mov_oog"].std()),
                "total": float(group["total_mov"].std()),
            },
            "workload_1_crane_mean_h": float(service_work_h.mean()),
            "berth_time_1_crane_reference_mean_h": float(
                group["servicio_berma_1grua"].mean()
            ),
        }

    high = df[df["mes"].isin([10, 11, 12])]
    low = df[~df["mes"].isin([10, 11, 12])]
    cv_arrival = float(interarrival_h.std() / interarrival_h.mean())
    mean_service = float(df["servicio_berma_1grua"].mean())
    sd_service = float(df["servicio_berma_1grua"].std())
    cv_service = sd_service / mean_service
    mmc = erlang_c(lambd, mean_service, BERTHS)
    mgc_ac = allen_cunneen(mmc, 1.0, cv_service)
    ggc_ac = allen_cunneen(mmc, cv_arrival, cv_service)

    queue_models = [
        {
            "model": "M/M/3 Erlang C",
            "arrival_assumption": "Poisson estacionario",
            "service_assumption": "Exponencial con media empírica de trabajo nominal",
            **mmc,
        },
        {
            "model": "M/G/3 Allen-Cunneen",
            "arrival_assumption": "Poisson estacionario",
            "service_assumption": "Servicio general; variabilidad empírica construida",
            "servers": BERTHS,
            "lambda_per_h": lambd,
            "rho": mmc["rho"],
            "mean_service_h": mean_service,
            **mgc_ac,
        },
        {
            "model": "G/G/3 Allen-Cunneen",
            "arrival_assumption": "Variabilidad agregada medida; estacionariedad no demostrada",
            "service_assumption": "Servicio general; variabilidad empírica construida",
            "servers": BERTHS,
            "lambda_per_h": lambd,
            "rho": mmc["rho"],
            "mean_service_h": mean_service,
            **ggc_ac,
        },
    ]

    summary: dict[str, Any] = {
        "metadata": {
            "dataset": csv_path.name,
            "rows": int(len(df)),
            "unique_scale_ids": int(df["id_escala"].nunique()),
            "start": start.strftime("%Y-%m-%d %H:%M"),
            "end": end.strftime("%Y-%m-%d %H:%M"),
            "span_days": span_h / 24.0,
            "arrival_rate_per_day": lambd * 24.0,
            "arrival_rate_per_h": lambd,
            "interarrival_mean_h": float(interarrival_h.mean()),
            "interarrival_sd_h": float(interarrival_h.std()),
            "interarrival_cv": cv_arrival,
        },
        "integrity": {
            "missing_required_values": 0,
            "duplicate_scale_ids": 0,
            "non_decreasing_arrivals": True,
            "simultaneous_arrival_pairs": int((interarrival_h == 0).sum()),
            "negative_moves": 0,
        },
        "arrivals_by_service": service_summary,
        "reefer_seasonality": {
            "high_months": [10, 11, 12],
            "low_months": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "high_arrivals": int(len(high)),
            "low_arrivals": int(len(low)),
            "reefer_mean_high": float(high["mov_reefer"].mean()),
            "reefer_mean_low": float(low["mov_reefer"].mean()),
            "reefer_high_to_low_ratio": float(
                high["mov_reefer"].mean() / low["mov_reefer"].mean()
            ),
        },
        "technical_parameters": {
            "crane_rates_moves_per_h": CRANE_RATES,
            "two_crane_joint_factor": 1.7,
            "berths_base": BERTHS,
            "maneuver_reference_mean_h": MANEUVER_REFERENCE_H,
            "maneuver_reference_status": "Midpoint of the stated 1-2 h combined range; assumption, not observed mean.",
            "mean_nominal_work_1_crane_h": float(df["horas_grua_1"].mean()),
            "sd_nominal_work_1_crane_h": float(df["horas_grua_1"].std()),
            "mean_constructed_berth_time_1_crane_h": mean_service,
            "sd_constructed_berth_time_1_crane_h": sd_service,
            "cv_constructed_berth_time_1_crane": cv_service,
        },
        "a_priori_queue_estimates": queue_models,
        "distribution_fit_diagnostics": _fit_diagnostics(),
        "assumptions_and_limits": [
            "Las tres bermas se aproximan como servidores paralelos homogéneos.",
            "El tiempo de servicio usa una grúa por buque y la maniobra media de referencia de 1.5 h; no modela asignación dinámica ni interferencias entre buques.",
            "No se incluyen turnos, patio, camiones, bloqueos de transporte ni cruceros en las fórmulas de filas.",
            "El registro no contiene zarpadas; el tiempo de servicio de la fila se construye a partir de tasas nominales y no es una observación de estadía.",
            "La aproximación G/G/3 es una sensibilidad; el CV agregado recoge agrupamiento y estacionalidad y no prueba estacionariedad.",
        ],
    }
    return summary, queue_models


def write_outputs(summary: dict[str, Any], queue_models: list[dict[str, Any]]) -> tuple[Path, Path]:
    summary_path = DATA_DIR / "resumen_modelo_datos_g08.json"
    queue_path = PLOTS_DIR / "estimaciones_filas_g08.csv"
    with summary_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)

    queue_fields = [
        "model",
        "servers",
        "arrival_assumption",
        "service_assumption",
        "lambda_per_h",
        "mean_service_h",
        "rho",
        "wq_h",
        "w_h",
        "lq_vessels",
        "l_vessels",
    ]
    with queue_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=queue_fields, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(queue_models)
    return summary_path, queue_path


def run() -> dict[str, Any]:
    summary, queue_models = build_summary()
    summary_path, queue_path = write_outputs(summary, queue_models)
    meta = summary["metadata"]
    print(f"Escalas: {meta['rows']:,}; período: {meta['start']} a {meta['end']}")
    print(
        "Arribos: "
        f"{meta['arrival_rate_per_day']:.3f} buques/día; "
        f"interarribo CV={meta['interarrival_cv']:.3f}"
    )
    print("\nEstimaciones a priori (horas):")
    for model in queue_models:
        print(
            f"{model['model']}: rho={model['rho']:.3f}; "
            f"Wq={model['wq_h']:.2f}; W={model['w_h']:.2f}; "
            f"L={model['l_vessels']:.2f}"
        )
    print(f"\nResumen: {summary_path}")
    print(f"Filas: {queue_path}")
    return summary


if __name__ == "__main__":
    run()
