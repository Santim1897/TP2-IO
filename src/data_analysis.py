import pandas as pd
import numpy as np
import scipy.stats as stats

# Load Grupo 8 dataset
csv_path = 'C:/Users/ASUS/.gemini/antigravity/scratch/TP2-IO/PuertoSur_escalas_G08.csv'
df = pd.read_csv(csv_path)
df['fecha_hora_arribo'] = pd.to_datetime(df['fecha_hora_arribo'])
df = df.sort_values('fecha_hora_arribo').reset_index(drop=True)

df['interarrival_hours'] = df['fecha_hora_arribo'].diff().dt.total_seconds() / 3600.0

total_days = (df['fecha_hora_arribo'].max() - df['fecha_hora_arribo'].min()).total_seconds() / (24*3600)
total_ships = len(df)
lambda_ships_per_day = total_ships / total_days
lambda_ships_per_hour = lambda_ships_per_day / 24.0

print(f"=== ANÁLISIS DE DATOS GRUPO 8 ===")
print(f"Total escalas: {total_ships}")
print(f"Período analizado: {df['fecha_hora_arribo'].min()} a {df['fecha_hora_arribo'].max()}")
print(f"Total días: {total_days:.2f}")
print(f"Tasa de arribos: {lambda_ships_per_day:.3f} buques/día ({lambda_ships_per_hour:.4f} buques/hora)")

mean_inter = df['interarrival_hours'].dropna().mean()
std_inter = df['interarrival_hours'].dropna().std()
cv_inter = std_inter / mean_inter
print(f"Tiempo entre arribos (Delta t): media = {mean_inter:.3f} h, desv = {std_inter:.3f} h, CV = {cv_inter:.3f}")

# Distribution of services
print("\n=== DISTRIBUCIÓN POR SERVICIO ===")
srv_counts = df['servicio'].value_counts()
srv_props = df['servicio'].value_counts(normalize=True)
srv_summary = pd.DataFrame({'Escalas': srv_counts, 'Proporción (%)': srv_props * 100})
print(srv_summary)

# Movements per service
df['total_mov'] = df['mov_dry'] + df['mov_reefer'] + df['mov_oog']
print("\n=== MOVIMIENTOS PROMEDIO POR SERVICIO ===")
print(df.groupby('servicio')[['mov_dry', 'mov_reefer', 'mov_oog', 'total_mov']].mean())

# Estimate crane hours per ship
# Rates: Dry = 28 mov/h, Reefer = 21 mov/h, OOG = 12 mov/h
df['crane_hours_single'] = (df['mov_dry'] / 28.0) + (df['mov_reefer'] / 21.0) + (df['mov_oog'] / 12.0)
print("\n=== HORAS DE GRÚA (1 GRÚA INDIVIDUAL) ===")
print(df.groupby('servicio')['crane_hours_single'].describe())
print(f"Promedio general horas de grúa individual: {df['crane_hours_single'].mean():.2f} h")

# If 2 cranes operate with 85% efficiency:
# dual rate = 0.85 * (rate + rate) = 1.7 * rate => time is crane_hours_single / 1.7
df['crane_hours_dual'] = df['crane_hours_single'] / 1.7
print(f"Promedio general horas de grúa dual (2 grúas con interferencia): {df['crane_hours_dual'].mean():.2f} h")

# Maneuver times: uniform(1, 2) => mean = 1.5 h each => 3.0 h total
mean_maneuver = 3.0
mean_service_time_single = df['crane_hours_single'].mean() + mean_maneuver
mean_service_time_dual = df['crane_hours_dual'].mean() + mean_maneuver

print(f"\nTiempo de berma medio (con 1 grúa): {mean_service_time_single:.2f} h")
print(f"Tiempo de berma medio (con 2 grúas): {mean_service_time_dual:.2f} h")

# Seasonality by month
df['month'] = df['fecha_hora_arribo'].dt.month
monthly = df.groupby('month').agg(
    escalas=('id_escala', 'count'),
    mov_reefer_mean=('mov_reefer', 'mean'),
    mov_total_mean=('total_mov', 'mean')
)
print("\n=== ESTACIONALIDAD MENSUAL ===")
print(monthly)

# Seasonality by hour of arrival
df['hour'] = df['fecha_hora_arribo'].dt.hour
hourly = df.groupby('hour')['id_escala'].count()
print("\n=== DISTRIBUCIÓN POR HORA DEL DÍA ===")
print(hourly)
