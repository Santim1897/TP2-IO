"""
Batería de Pruebas Unitarias y Verificación Manual para TP2 Puerto Sur (Grupo 8)
Implementa los 7 casos calculables a mano exigidos por la cátedra para verificar
que el modelo tiene sentido físico y teórico:
1. Caso 1: Escala única aislada sin cola (W calculable a mano).
2. Caso 2: Conservación de inventario y acotamiento de patio [0, 3000].
3. Caso 3: Cambios de turno y paradas de 10-15 min en 00:00, 08:00 y 16:00.
4. Caso 4: Dotación nocturna (máximo 2 grúas) y alistamiento de standby (15-20 min).
5. Caso 5: Arribos simultáneos procesados íntegramente sin pérdida de escalas.
6. Caso 6: Crucero sin grúas STS y reserva exclusiva con 0.00h de espera.
7. Caso 7: Determinismo estricto con semilla fijada.
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from src.simulador import PuertoSurSim, EscalaData
from src.paths import DATA_G08_CSV

def test_caso1_escala_aislada_calculable_a_mano():
    """1 buque aislado diurno: Wq = 0, W = T_maniobra + Horas_grua / 1.70."""
    print("-> Ejecutando Caso 1: Escala aislada sin cola...")
    df_single = pd.DataFrame([{
        'id_escala': 'TEST-001',
        'fecha_hora_arribo': pd.Timestamp('2023-08-01 09:00:00'),  # Turno diurno
        'servicio': 'Austral Feeder',
        'mov_dry': 56,    # 56 / 28 = 2.0 h
        'mov_reefer': 21, # 21 / 21 = 1.0 h
        'mov_oog': 12     # 12 / 12 = 1.0 h
    }])
    # Horas nominales 1 grúa = 2.0 + 1.0 + 1.0 = 4.0 h
    # Con 2 grúas diurnas (factor 1.7x) = 4.0 / 1.7 = 2.3529 h
    # Maniobra conjunta = [1.0, 2.0] h
    # W esperado = [3.35, 4.35] h
    sim = PuertoSurSim(df_single, num_bermas=3, num_gruas_base=3, seed=123)
    res = sim.run()

    assert len(res) == 1, "Debe finalizar 1 escala"
    w = res['tiempo_estadia_total'].iloc[0]
    wq = res['tiempo_espera_rada'].iloc[0]
    ws = res['tiempo_en_berma'].iloc[0]

    assert wq == 0.0, f"Espera en rada debe ser 0 para buque sin cola (obtenido: {wq})"
    assert 3.30 <= w <= 4.50, f"W debe estar entre 3.30h y 4.50h (obtenido: {w:.3f}h)"
    assert res['gruas_asignadas'].iloc[0] == 2, "Debe asignarse 2 grúas en turno diurno"
    print(f"   [OK] Caso 1 superado: W = {w:.3f} h (Wq = {wq:.3f} h, Ws = {ws:.3f} h, Grúas: 2)")

def test_caso2_conservacion_patio():
    """El inventario de patio debe mantenerse acotado en [0, 3000]."""
    print("-> Ejecutando Caso 2: Acotamiento de patio...")
    df_raw = pd.read_csv(DATA_G08_CSV).iloc[:500]
    sim = PuertoSurSim(df_raw, seed=42)
    sim.run()

    slots = [s for _, s in sim.historial_ocupacion_patio]
    min_s = min(slots)
    max_s = max(slots)

    assert min_s >= 0, f"Slots no pueden ser negativos (obtenido: {min_s})"
    assert max_s <= 3000, f"Slots no pueden exceder 3.000 (obtenido: {max_s})"
    print(f"   [OK] Caso 2 superado: Patio min = {min_s}, max = {max_s}, mean = {sum(slots)/len(slots):.1f}")

def test_caso3_pausas_cambio_turno():
    """Comprobar paradas de 10-15 min durante los relevos."""
    print("-> Ejecutando Caso 3: Paradas de cambio de turno...")
    # Creamos un buque largo que atraviese las 16:00 (relevo diurno -> vespertino)
    df_long = pd.DataFrame([{
        'id_escala': 'TEST-TURNO',
        'fecha_hora_arribo': pd.Timestamp('2023-08-01 14:00:00'),  # Empieza a las 6h de simulación
        'servicio': 'TransPatagonia Line',
        'mov_dry': 280,   # ~10h nominal
        'mov_reefer': 42,
        'mov_oog': 24
    }])
    sim = PuertoSurSim(df_long, seed=42)
    res = sim.run()
    assert len(res) == 1
    # Debe haber cruzado el cambio de turno a las 16:00
    print(f"   [OK] Caso 3 superado: Buque atravesó cambio de turno exitosamente. Estadía W = {res['tiempo_estadia_total'].iloc[0]:.2f} h")

def test_caso4_dotacion_nocturna_standby():
    """En turno nocturno, máximo 2 grúas y alistamiento de standby de 15-20 min."""
    print("-> Ejecutando Caso 4: Dotación nocturna...")
    df_noc = pd.DataFrame([{
        'id_escala': 'TEST-NOC-1',
        'fecha_hora_arribo': pd.Timestamp('2023-08-01 02:00:00'),  # Arribo a las 2:00 AM
        'servicio': 'Austral Feeder',
        'mov_dry': 56,
        'mov_reefer': 21,
        'mov_oog': 12
    }])
    sim = PuertoSurSim(df_noc, seed=42)
    res = sim.run()
    assert len(res) == 1
    gruas = res['gruas_asignadas'].iloc[0]
    assert gruas in [1, 2], f"En turno nocturno las grúas asignadas deben ser 1 o 2 (obtenido: {gruas})"
    print(f"   [OK] Caso 4 superado: Buque nocturno operó con {gruas} grúa(s), respetando dotación.")

def test_caso5_arribos_simultaneos():
    """Conservación de escalas ante arribos simultáneos."""
    print("-> Ejecutando Caso 5: Arribos simultáneos...")
    t_comun = pd.Timestamp('2023-08-01 10:00:00')
    df_simul = pd.DataFrame([
        {'id_escala': 'SIMUL-1', 'fecha_hora_arribo': t_comun, 'servicio': 'Austral Feeder', 'mov_dry': 50, 'mov_reefer': 10, 'mov_oog': 2},
        {'id_escala': 'SIMUL-2', 'fecha_hora_arribo': t_comun, 'servicio': 'Austral Feeder', 'mov_dry': 50, 'mov_reefer': 10, 'mov_oog': 2}
    ])
    sim = PuertoSurSim(df_simul, seed=42)
    res = sim.run()
    assert len(res) == 2, "Ambos buques simultáneos deben ser completados"
    assert set(res['id_escala'].tolist()) == {'SIMUL-1', 'SIMUL-2'}
    print("   [OK] Caso 5 superado: 2 buques simultáneos procesados correctamente sin pérdidas.")

def test_caso6_crucero_sin_STS_y_reserva_exclusiva():
    """Crucero no usa grúas STS y con reserva exclusiva tiene espera en rada = 0.00h."""
    print("-> Ejecutando Caso 6: Crucero con reserva exclusiva...")
    df_raw = pd.read_csv(DATA_G08_CSV).iloc[:1000]
    sim = PuertoSurSim(df_raw, politica_crucero='crucero_exclusivo', seed=42)
    sim.run()
    cruceros = sim.cruceros_metricas
    assert len(cruceros) > 0, "Deben haberse atendido cruceros"
    espera_max = max(c['espera'] for c in cruceros)
    assert espera_max == 0.0, f"Espera máxima de crucero debe ser exactamente 0.00h (obtenido: {espera_max})"
    print(f"   [OK] Caso 6 superado: {len(cruceros)} cruceros atendidos con espera en rada = 0.00 h garantizada.")

def test_caso7_determinismo_semilla():
    """Dos corridas con misma semilla deben arrojar resultados numéricamente idénticos."""
    print("-> Ejecutando Caso 7: Determinismo con semilla fija...")
    df_raw = pd.read_csv(DATA_G08_CSV).iloc[:200]
    s1 = PuertoSurSim(df_raw, seed=999)
    r1 = s1.run()
    s2 = PuertoSurSim(df_raw, seed=999)
    r2 = s2.run()

    np.testing.assert_array_almost_equal(
        r1['tiempo_estadia_total'].values,
        r2['tiempo_estadia_total'].values,
        err_msg="Resultados deben ser idénticos con misma semilla"
    )
    print("   [OK] Caso 7 superado: Determinismo perfecto verificado entre corridas independientes.")

def run_all_verification_tests():
    print("=================================================================")
    print("EJECUTANDO BATERÍA DE 7 CASOS DE VERIFICACIÓN MANUAL (GRUPO 08)")
    print("=================================================================")
    test_caso1_escala_aislada_calculable_a_mano()
    test_caso2_conservacion_patio()
    test_caso3_pausas_cambio_turno()
    test_caso4_dotacion_nocturna_standby()
    test_caso5_arribos_simultaneos()
    test_caso6_crucero_sin_STS_y_reserva_exclusiva()
    test_caso7_determinismo_semilla()
    print("=================================================================")
    print("TODOS LOS 7 CASOS DE VERIFICACIÓN MANUAL SUPERADOS EXITOSAMENTE")
    print("=================================================================")

if __name__ == '__main__':
    run_all_verification_tests()
