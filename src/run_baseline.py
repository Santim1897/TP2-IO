import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from src.simulador import PuertoSurSim
import time

df = pd.read_csv('C:/Users/ASUS/.gemini/antigravity/scratch/TP2-IO/PuertoSur_escalas_G08.csv')
df['fecha_hora_arribo'] = pd.to_datetime(df['fecha_hora_arribo'])

print(f"Running baseline simulation with all {len(df)} scales of Grupo 8...")
t0 = time.time()
sim = PuertoSurSim(df, num_bermas=3, num_gruas_base=3, seed=42)
res = sim.run()
t1 = time.time()

print(f"Completed in {t1-t0:.2f} s. Ships: {len(res)}")
pct_excede = res['excede_16h'].mean() * 100.0
pct_espera = (res['tiempo_espera_rada'].mean() / res['tiempo_estadia_total'].mean()) * 100.0
pct_atendido = (res['tiempo_en_berma'].mean() / res['tiempo_estadia_total'].mean()) * 100.0

total_horas_sim = res['t_zarpada'].max() - res['t_arribo'].min()
lambda_sim = len(res) / total_horas_sim
L = lambda_sim * res['tiempo_estadia_total'].mean()
Lq = lambda_sim * res['tiempo_espera_rada'].mean()

print("\n=== RESULTADOS CONSIGNAS A & B (OPERACIÓN ACTUAL) ===")
print(f"Estadía promedio total (W): {res['tiempo_estadia_total'].mean():.2f} horas (std: {res['tiempo_estadia_total'].std():.2f})")
print(f"Tiempo promedio en espera en rada (Wq): {res['tiempo_espera_rada'].mean():.2f} horas (std: {res['tiempo_espera_rada'].std():.2f})")
print(f"Tiempo promedio en berma/atendido (Ws): {res['tiempo_en_berma'].mean():.2f} horas (std: {res['tiempo_en_berma'].std():.2f})")
print(f"Porcentaje del tiempo en espera: {pct_espera:.2f}%")
print(f"Porcentaje del tiempo siendo atendido: {pct_atendido:.2f}%")
print(f"Cantidad promedio de buques en el puerto (L): {L:.2f} buques")
print(f"Cantidad promedio de buques esperando en rada (Lq): {Lq:.2f} buques")
print(f"Porcentaje de buques que superan el umbral de 16h: {pct_excede:.2f}%")

print("\nPor servicio:")
print(res.groupby('servicio')[['tiempo_espera_rada', 'tiempo_en_berma', 'tiempo_estadia_total', 'excede_16h']].mean())
