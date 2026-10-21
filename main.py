"""
Orquestador Principal - TP2: Simulación de la Terminal Portuaria "Puerto Sur"
Asignatura: 11.51 / IO51 - Investigación Operativa (ITBA) - 2026 2C
Grupo: Grupo 08
"""

import os
import sys
import subprocess
import time

def print_banner():
    print("=" * 75)
    print("   TRABAJO PRÁCTICO N° 2: INVESTIGACIÓN OPERATIVA (IO51) - ITBA 2026")
    print("   SIMULACIÓN DE EVENTOS DISCRETOS: TERMINAL PORTUARIA 'PUERTO SUR'")
    print("   GRUPO 08 - DATASET: PuertoSur_escalas_G08.csv (8.852 Escalas)")
    print("=" * 75)

def run_step(step_name, command):
    print(f"\n[PASO] {step_name}...")
    t0 = time.time()
    res = subprocess.run([sys.executable] + command.split(), capture_output=True, text=True)
    t1 = time.time()
    if res.returncode == 0:
        print(f" -> Completado exitosamente en {t1 - t0:.2f} s")
        if res.stdout.strip():
            print("\n" + "\n".join(res.stdout.strip().split("\n")[:15])) # Primeras 15 líneas
    else:
        print(f" -> Error en el paso: {res.stderr}")
        sys.exit(1)

def main():
    print_banner()
    
    # 1. Análisis de datos y Teoría de Colas a Priori
    run_step("1. Análisis Exploratorio de Datos Históricos", "src/data_analysis.py")
    run_step("2. Modelo Analítico de Teoría de Colas a Priori", "src/queue_theory_apriori.py")
    
    # 2. Simulación Operativa y Batería de Experimentos
    run_step("3. Simulación de Línea Base (Operación Actual)", "src/run_baseline.py")
    run_step("4. Batería Experimental de Escenarios (Consignas c a g)", "src/run_experiments.py")
    
    # 3. Generación de Gráficos de Publicación (300 DPI)
    run_step("5. Generación de Gráficos Analíticos de Alta Resolución", "src/generate_plots.py")
    
    print("\n" + "=" * 75)
    print("   ¡SUITE COMPLETA EJECUTADA CON ÉXITO!")
    print("   Consulte el informe detallado en: INFORME_EJECUTIVO_PUERTO_SUR.md")
    print("   Gráficos generados en: plots/")
    print("=" * 75)

if __name__ == "__main__":
    main()
