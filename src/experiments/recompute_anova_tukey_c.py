import sys,time
from pathlib import Path
import pandas as pd,numpy as np
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
BASE_DIR=Path(__file__).resolve().parent.parent.parent; sys.path.insert(0,str(BASE_DIR))
from src.paths import DATA_G08_CSV,PLOTS_DIR
from src.simulador import PuertoSurSim
N=30; OUT=PLOTS_DIR/"entrega_c_reproducible"; OUT.mkdir(parents=True,exist_ok=True)
d=pd.read_csv(DATA_G08_CSV); d["fecha_hora_arribo"]=pd.to_datetime(d["fecha_hora_arribo"])
rows=[]; start=time.time()
configs=[("3B_3G",3,3),("3B_4G",3,4),("4B_3G",4,3)]
for ci,(name,berms,cranes) in enumerate(configs):
 for r in range(N):
  seed=910001+ci*100000+r*131
  sim=PuertoSurSim(df_escalas=d,num_bermas=berms,num_gruas_base=cranes,seed=seed)
  res=sim.run(); stat=res[res.t_arribo>=1440]
  rows.append({"scenario":name,"replication":r+1,"seed":seed,"W_h":stat.tiempo_estadia_total.mean(),
               "P_W_le_16_pct":(stat.tiempo_estadia_total<=16).mean()*100})
 if (r+1)%5==0: print(f"{name}: {r+1}/{N}",flush=True)
raw=pd.DataFrame(rows); raw.to_csv(OUT/"anova_tukey_independent_replications.csv",index=False)
anova=[]
for m in ("W_h","P_W_le_16_pct"):
 gs=[raw[raw.scenario==n][m].to_numpy() for n,_,_ in configs]
 f,p=stats.f_oneway(*gs)
 anova.append({"metric":m,"F":f,"p_value":p,"df_between":2,"df_within":87})
pd.DataFrame(anova).to_csv(OUT/"anova_independent.csv",index=False)
tukey=[]
for m in ("W_h","P_W_le_16_pct"):
 res=pairwise_tukeyhsd(raw[m],raw.scenario,alpha=.05)
 for row in res.summary().data[1:]:
  tukey.append({"metric":m,"group1":row[0],"group2":row[1],"mean_difference":row[2],
                "p_adjusted":row[3],"ci95_low":row[4],"ci95_high":row[5],"reject":row[6]})
pd.DataFrame(tukey).to_csv(OUT/"tukey_hsd_independent.csv",index=False)
summary=raw.groupby("scenario").agg(n=("W_h","size"),W_mean=("W_h","mean"),W_sd=("W_h","std"),P16_mean=("P_W_le_16_pct","mean"),P16_sd=("P_W_le_16_pct","std")).reset_index()
summary.to_csv(OUT/"anova_scenario_summary.csv",index=False)
print("summary\\n",summary.to_string(index=False),flush=True)
print("anova\\n",pd.DataFrame(anova).to_string(index=False),flush=True)
print("tukey\\n",pd.DataFrame(tukey).to_string(index=False),flush=True)
print("runtime",round(time.time()-start,2),flush=True)
