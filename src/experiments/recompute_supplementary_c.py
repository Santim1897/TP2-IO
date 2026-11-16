"""Supplementary 30-replication campaign for warm-up and industrial demand.

Uses the same historical CSV, model, and seed sequence as recompute_campaign_c.py.
"""
import sys, time, json
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats

BASE_DIR=Path(__file__).resolve().parent.parent.parent
sys.path.insert(0,str(BASE_DIR))
from src.paths import DATA_G08_CSV, PLOTS_DIR
from src.simulador import PuertoSurSim

N=30
BASE=202601
STEP=101
WARMUP=1440.0
OUT=PLOTS_DIR/"entrega_c_reproducible"
OUT.mkdir(parents=True,exist_ok=True)

def ci95(x):
    x=np.asarray(x,dtype=float)
    m=float(np.mean(x))
    h=float(stats.t.ppf(.975,len(x)-1)*stats.sem(x)) if len(x)>1 else 0.0
    return m,m-h,m+h

def main():
    start=time.time()
    df=pd.read_csv(DATA_G08_CSV)
    df["fecha_hora_arribo"]=pd.to_datetime(df["fecha_hora_arribo"])
    warm_rows=[]
    high_rows=[]
    for r in range(N):
        seed=BASE+r*STEP
        # One historical replay per seed; derive warm-up sensitivity from same run.
        sim=PuertoSurSim(df_escalas=df,num_bermas=3,num_gruas_base=3,seed=seed)
        res=sim.run()
        for days in (30,60,90):
            sample=res[res.t_arribo>=days*24]
            warm_rows.append({"scenario":f"warmup_{days}d","replication":r+1,"seed":seed,
                              "n_completed_after_cut":len(sample),
                              "W_h":float(sample.tiempo_estadia_total.mean()),
                              "Wq_h":float(sample.tiempo_espera_rada.mean()),
                              "Ws_h":float(sample.tiempo_en_berma.mean()),
                              "P_W_le_16_pct":float((sample.tiempo_estadia_total<=16).mean()*100)})
        if (r+1)%5==0: print(f"Calentamiento {r+1}/{N}",flush=True)
    pd.DataFrame(warm_rows).to_csv(OUT/"warmup_replications.csv",index=False)

    for factor in (1.35,2.0):
        n_extra=int(len(df)*(factor-1.0))
        expected=len(df)+n_extra
        for berms in (3,4):
            for r in range(N):
                seed=BASE+r*STEP
                sim=PuertoSurSim(df_escalas=df,num_bermas=berms,num_gruas_base=3,
                                 factor_demanda=factor,seed=seed)
                res=sim.run()
                complete=(len(res)==expected)
                stat=res[res.t_arribo>=WARMUP]
                high_rows.append({"scenario":f"industrial_{factor:.2f}_{berms}B_3G",
                                  "factor":factor,"berths":berms,"cranes":3,"replication":r+1,
                                  "seed":seed,"scheduled_arrivals":expected,
                                  "completed_arrivals":len(res),"completion_pct":len(res)/expected*100,
                                  "all_vessels_completed":complete,
                                  "n_after_warmup":len(stat),
                                  "W_completed_only_h":float(stat.tiempo_estadia_total.mean()) if len(stat) else np.nan,
                                  "P16_completed_only_pct":float((stat.tiempo_estadia_total<=16).mean()*100) if len(stat) else np.nan})
                pd.DataFrame(high_rows).to_csv(OUT/"industrial_replications.csv",index=False)
                if (r+1)%5==0: print(f"Demanda {factor:.2f}, {berms} bermas: réplica {r+1}/{N}",flush=True)
            print(f"Demanda {factor:.2f}, {berms} bermas: {N}/{N}",flush=True)

    w=pd.DataFrame(warm_rows)
    h=pd.DataFrame(high_rows)
    w.to_csv(OUT/"warmup_replications.csv",index=False)
    h.to_csv(OUT/"industrial_replications.csv",index=False)
    summaries=[]
    for s,g in w.groupby("scenario"):
        rec={"scenario":s,"n_replications":len(g)}
        for m in ("W_h","Wq_h","Ws_h","P_W_le_16_pct"):
            mu,lo,hi=ci95(g[m])
            rec.update({m+"_mean":mu,m+"_ci95_low":lo,m+"_ci95_high":hi})
        summaries.append(rec)
    pd.DataFrame(summaries).to_csv(OUT/"warmup_summary.csv",index=False)

    hs=[]
    for s,g in h.groupby("scenario"):
        all_ok=bool(g.all_vessels_completed.all())
        rec={"scenario":s,"n_replications":len(g),"all_completed_replicas":int(g.all_vessels_completed.sum()),
             "mean_completion_pct":float(g.completion_pct.mean()),
             "valid_steady_state_W":False}
        if all_ok:
            for m in ("W_completed_only_h","P16_completed_only_pct"):
                mu,lo,hi=ci95(g[m])
                rec.update({m+"_mean":mu,m+"_ci95_low":lo,m+"_ci95_high":hi})
            rec["valid_steady_state_W"]=True
        hs.append(rec)
    pd.DataFrame(hs).to_csv(OUT/"industrial_summary.csv",index=False)
    meta={"replications":N,"seed_formula":f"{BASE} + (replication-1)*{STEP}",
          "source_csv":"data/PuertoSur_escalas_G08.csv",
          "source_commit":"da1151976ba8d2bf1394f84623308db16607053c",
          "source_csv_sha256":"c4390d32d383a2afe6a8313de7b83fbf4500b0c10ade8671d7514b3fbe78d2d9",
          "simulator_sha256":"029219715f9e43901c500ac88b2a785ba1c158437288d03c79bed1c59648bc85",
          "script":"src/experiments/recompute_supplementary_c.py",
          "source_rows":len(df),"runtime_seconds":round(time.time()-start,2),
          "industrial_horizon":"simulador default, 200h after last scheduled arrival"}
    (OUT/"supplement_metadata.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
    print("DONE",json.dumps(meta),flush=True)
    print(pd.DataFrame(summaries).to_string(index=False),flush=True)
    print(pd.DataFrame(hs).to_string(index=False),flush=True)

if __name__=="__main__": main()
