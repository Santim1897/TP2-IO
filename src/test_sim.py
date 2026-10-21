import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from src.simulador import PuertoSurSim
from src.paths import DATA_G08_CSV
import time

df = pd.read_csv(DATA_G08_CSV)
df['fecha_hora_arribo'] = pd.to_datetime(df['fecha_hora_arribo'])

print("Running test with 1000 scales...")
t0 = time.time()
sim = PuertoSurSim(df.iloc[:1000], num_bermas=3, num_gruas_base=3, seed=42)
res = sim.run()
t1 = time.time()

print(f"Done in {t1-t0:.2f} s. Completed ships: {len(res)}")
print(res[['tiempo_espera_rada', 'tiempo_en_berma', 'tiempo_estadia_total', 'excede_16h']].describe())
pct_excede = res['excede_16h'].mean() * 100.0
pct_espera = (res['tiempo_espera_rada'].mean() / res['tiempo_estadia_total'].mean()) * 100.0
print(f"Porcentaje que excede 16h: {pct_excede:.2f}%")
print(f"Porcentaje del tiempo que espera en rada: {pct_espera:.2f}%")
