"""Reproduce Parte C results from the historical G08 dataset.

Run from repository root:
python src/experiments/recompute_campaign_c.py
"""
import json
import time
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
from src.paths import DATA_G08_CSV, PLOTS_DIR
from src.simulador import PuertoSurSim

N = 30
BASE_SEED = 202601
SEED_STEP = 101
WARMUP_H = 1440.0
OUT = PLOTS_DIR / "entrega_c_reproducible"
OUT.mkdir(parents=True, exist_ok=True)


def ci95(values):
    x = np.asarray(values, dtype=float)
    m = float(x.mean())
    if len(x) < 2:
        return m, m, m
    h = float(stats.t.ppf(0.975, len(x)-1) * stats.sem(x))
    return m, m-h, m+h


def run_one(df, label, *, berms=3, cranes=3, cruise="sin_crucero", factor=1.0, rep, seed):
    sim = PuertoSurSim(df_escalas=df, num_bermas=berms, num_gruas_base=cranes,
                       politica_crucero=cruise, factor_demanda=factor, seed=seed)
    result = sim.run()
    steady = result[result["t_arribo"] >= WARMUP_H].copy()
    if steady.empty:
        raise RuntimeError(f"No observations after warm-up for {label} rep {rep}")
    w = steady["tiempo_estadia_total"].astype(float)
    cruise_metrics = pd.DataFrame(sim.cruceros_metricas)
    return {
        "scenario": label, "replication": rep, "seed": seed,
        "berths": berms, "cranes": cranes, "demand_factor": factor,
        "cruise_policy": cruise, "n_feeders": len(steady),
        "W_h": float(w.mean()),
        "Wq_h": float(steady["tiempo_espera_rada"].mean()),
        "Ws_h": float(steady["tiempo_en_berma"].mean()),
        "P_W_le_16_pct": float((w <= 16).mean() * 100),
        "n_cruises": len(cruise_metrics),
        "cruise_wait_h": float(cruise_metrics["espera"].mean()) if len(cruise_metrics) else np.nan,
        "cruise_dwell_h": float(cruise_metrics["duracion"].mean()) if len(cruise_metrics) else np.nan,
    }


def main():
    started = time.time()
    df = pd.read_csv(DATA_G08_CSV)
    df["fecha_hora_arribo"] = pd.to_datetime(df["fecha_hora_arribo"])
    rows = []

    # Core historical baseline, paired by seed.
    for r in range(N):
        seed = BASE_SEED + r * SEED_STEP
        for cranes in (3, 4):
            rows.append(run_one(df, f"base_{cranes}G", cranes=cranes, rep=r+1, seed=seed))
        if (r+1) % 5 == 0:
            print(f"Base histórica: {r+1}/{N} réplicas", flush=True)

    # Demand frontier: 30 paired replications at each tested factor.
    for factor in (0.80, 0.85, 0.90, 0.95, 1.00):
        if factor == 1.0:
            dsub = df
        else:
            dsub = df.sample(frac=factor, random_state=42).sort_values(
                "fecha_hora_arribo").reset_index(drop=True)
        for r in range(N):
            seed = BASE_SEED + r * SEED_STEP
            for cranes in (3, 4):
                rows.append(run_one(dsub, f"demand_{factor:.2f}_{cranes}G",
                                    cranes=cranes, factor=factor, rep=r+1, seed=seed))
        print(f"Barrido de demanda {factor:.2f}: {N}/{N} por dotación", flush=True)
        pd.DataFrame(rows).to_csv(OUT / "replications.csv", index=False)

    # Berth payback: 3 vs 4 berths, keeping cranes and arrivals unchanged.
    for r in range(N):
        seed = BASE_SEED + r * SEED_STEP
        for berms in (3, 4):
            rows.append(run_one(df, f"berths_{berms}", berms=berms, cranes=3,
                                rep=r+1, seed=seed))
        if (r+1) % 5 == 0:
            print(f"Comparación de bermas: {r+1}/{N} réplicas", flush=True)
    pd.DataFrame(rows).to_csv(OUT / "replications.csv", index=False)

    # Cruise alternatives: report feeder and cruise outcomes separately.
    for policy in ("sin_crucero", "crucero_sin_exclusividad", "crucero_exclusivo"):
        for r in range(N):
            seed = BASE_SEED + r * SEED_STEP
            rows.append(run_one(df, f"cruise_{policy}", cruise=policy,
                                rep=r+1, seed=seed))
        print(f"Cruceros {policy}: {N}/{N} réplicas", flush=True)
        pd.DataFrame(rows).to_csv(OUT / "replications.csv", index=False)

    raw = pd.DataFrame(rows)
    raw.to_csv(OUT / "replications.csv", index=False)

    summaries = []
    for label, g in raw.groupby("scenario", sort=False):
        rec = {"scenario": label, "n_replications": len(g)}
        for metric in ("W_h", "Wq_h", "Ws_h", "P_W_le_16_pct",
                       "cruise_wait_h", "cruise_dwell_h"):
            x = g[metric].dropna().to_numpy()
            if len(x):
                m, lo, hi = ci95(x)
                rec.update({f"{metric}_mean": m, f"{metric}_ci95_low": lo,
                            f"{metric}_ci95_high": hi})
        summaries.append(rec)
    pd.DataFrame(summaries).to_csv(OUT / "scenario_summary.csv", index=False)

    # Formal base contrasts.
    def vec(name, metric):
        return raw.loc[raw.scenario == name, metric].to_numpy(dtype=float)
    def paired_test(a, b, metric):
        xa, xb = vec(a, metric), vec(b, metric)
        d = xa-xb
        m, lo, hi = ci95(d)
        return {"contrast": f"{a} minus {b}", "metric": metric,
                "difference_mean": m, "ci95_low": lo, "ci95_high": hi,
                "p_two_sided": float(stats.ttest_rel(xa, xb).pvalue)}
    contrasts = [
        paired_test("base_3G", "base_4G", "W_h"),
        paired_test("base_3G", "base_4G", "P_W_le_16_pct"),
        paired_test("berths_3", "berths_4", "W_h"),
        paired_test("cruise_sin_crucero", "cruise_crucero_sin_exclusividad", "W_h"),
        paired_test("cruise_sin_crucero", "cruise_crucero_exclusivo", "W_h"),
    ]
    pd.DataFrame(contrasts).to_csv(OUT / "paired_contrasts.csv", index=False)

    # Per-scenario one-sided tests against the stated service targets.
    tests = []
    for scenario, g in raw.groupby("scenario", sort=False):
        if scenario.startswith("base_") or scenario.startswith("demand_"):
            for metric, target, alternative in (
                ("W_h", 16.0, "less"),
                ("P_W_le_16_pct", 90.0, "greater"),
            ):
                x = g[metric].to_numpy(dtype=float)
                tests.append({"scenario": scenario, "metric": metric, "target": target,
                              "alternative": alternative,
                              "p_one_sided": float(stats.ttest_1samp(
                                  x, target, alternative=alternative).pvalue)})
    pd.DataFrame(tests).to_csv(OUT / "service_target_tests.csv", index=False)

    meta = {
        "source_csv": str(DATA_G08_CSV.relative_to(BASE_DIR)), "source_rows": int(len(df)),
        "source_commit": "da1151976ba8d2bf1394f84623308db16607053c",
        "source_csv_sha256": "c4390d32d383a2afe6a8313de7b83fbf4500b0c10ade8671d7514b3fbe78d2d9",
        "simulator_sha256": "029219715f9e43901c500ac88b2a785ba1c158437288d03c79bed1c59648bc85",
        "replications": N, "seed_formula": f"{BASE_SEED} + (replication-1)*{SEED_STEP}",
        "warmup_hours": WARMUP_H, "completed_rows": len(raw),
        "runtime_seconds": round(time.time()-started, 2),
        "script": "src/experiments/recompute_campaign_c.py",
        "notes": [
            "Historical G08 arrival data; same 60-day warm-up in all alternatives.",
            "Demand factors below 1.00 are reproducible random subsamples (random_state=42).",
            "Cruise outcomes and feeder outcomes are reported separately.",
            "Payback is gross simple payback using the paired simulated berth effect and stated USD 15k-30k per vessel-day, before operating costs."
        ]
    }
    (OUT / "run_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("DONE", json.dumps(meta, ensure_ascii=False), flush=True)
    print(pd.DataFrame(summaries).to_string(index=False), flush=True)
    print(pd.DataFrame(contrasts).to_string(index=False), flush=True)

if __name__ == "__main__":
    main()
