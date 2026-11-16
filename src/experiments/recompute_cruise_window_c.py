import hashlib, subprocess, sys, time
from pathlib import Path
import pandas as pd, numpy as np
from scipy import stats

BASE_DIR=Path(__file__).resolve().parent.parent.parent
sys.path.insert(0,str(BASE_DIR))
from src.paths import DATA_G08_CSV, PLOTS_DIR
from src.simulador import PuertoSurSim
N=30; BASE=202601; STEP=101
OUT=PLOTS_DIR/"entrega_c_reproducible"; OUT.mkdir(parents=True,exist_ok=True)
start=time.time()
rows=[]
for pol in ("sin_crucero","crucero_sin_exclusividad","crucero_exclusivo"):
    for i in range(N):
        seed=BASE+i*STEP
        d=pd.read_csv(DATA_G08_CSV); d["fecha_hora_arribo"]=pd.to_datetime(d["fecha_hora_arribo"])
        sim=PuertoSurSim(df_escalas=d,num_bermas=3,num_gruas_base=3,politica_crucero=pol,seed=seed)
        res=sim.run()
        season=res[(res.t_arribo>=1440)&(res.t_arribo<3600)]
        if season.empty: raise RuntimeError(f"Season empty {pol} {i+1}")
        cr=pd.DataFrame(sim.cruceros_metricas)
        rows.append({"policy":pol,"replication":i+1,"seed":seed,"n_feeders":len(season),
                     "W_h":season.tiempo_estadia_total.mean(),"Wq_h":season.tiempo_espera_rada.mean(),
                     "Ws_h":season.tiempo_en_berma.mean(),"P_W_le_16_pct":(season.tiempo_estadia_total<=16).mean()*100,
                     "n_cruises":len(cr),"cruise_wait_h":cr.espera.mean() if len(cr) else np.nan,
                     "cruise_dwell_h":cr.duracion.mean() if len(cr) else np.nan})
        if (i+1)%5==0: print(f"Cruceros {pol}: {i+1}/{N}",flush=True)
    pd.DataFrame(rows).to_csv(OUT/"cruise_window_replications.csv",index=False)
def ci(x):
    x=np.asarray(x,float); m=x.mean(); h=stats.t.ppf(.975,len(x)-1)*stats.sem(x)
    return m,m-h,m+h
df=pd.DataFrame(rows); ss=[]
for pol,g in df.groupby("policy",sort=False):
    rec={"policy":pol,"n":len(g)}
    for metric in ("W_h","P_W_le_16_pct","cruise_wait_h","cruise_dwell_h"):
        x=g[metric].dropna().to_numpy()
        if len(x):
            m,lo,hi=ci(x); rec.update({metric+"_mean":m,metric+"_ci_low":lo,metric+"_ci_high":hi})
    rec["cruises_per_replication_mean"] = float(g["n_cruises"].mean())
    ss.append(rec)
pd.DataFrame(ss).to_csv(OUT/"cruise_window_summary.csv",index=False)
cs=[]
for pol in ("crucero_sin_exclusividad","crucero_exclusivo"):
    b=df[df.policy=="sin_crucero"].W_h.to_numpy()
    a=df[df.policy==pol].W_h.to_numpy()
    dif=a-b; m,lo,hi=ci(dif)
    cs.append({"contrast":pol+" minus sin_crucero","mean_delta_W_h":m,"ci95_low":lo,"ci95_high":hi,
               "p_paired_two_sided":stats.ttest_rel(a,b).pvalue})
pd.DataFrame(cs).to_csv(OUT/"cruise_window_contrasts.csv",index=False)
csv_path=Path(DATA_G08_CSV)
sim_path=BASE_DIR/"src/simulador.py"
meta={"source_csv":str(csv_path.relative_to(BASE_DIR)),"source_rows":int(len(pd.read_csv(csv_path))),
      "source_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=BASE_DIR,text=True).strip(),
      "source_csv_sha256":hashlib.sha256(csv_path.read_bytes()).hexdigest(),
      "simulator_sha256":hashlib.sha256(sim_path.read_bytes()).hexdigest(),
      "replications":N,"seed_formula":f"{BASE} + (replication-1)*{STEP}",
      "window_hours":[1440,3600],"cruise_interval_hours":84,"arrival_jitter_hours":[-3,3],
      "expected_cruises_per_replication":25,"runtime_seconds":round(time.time()-start,2),
      "script":"src/experiments/recompute_cruise_window_c.py"}
(OUT/"cruise_window_metadata.json").write_text(__import__("json").dumps(meta,indent=2),encoding="utf-8")
print(pd.DataFrame(ss).to_string(index=False),flush=True)
print(pd.DataFrame(cs).to_string(index=False),flush=True)
print("runtime",round(time.time()-start,2),flush=True)
