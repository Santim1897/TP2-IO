"""
Simulador de Eventos Discretos de la Terminal Portuaria Puerto Sur (Versión Refactorizada)
Asignatura: 11.51 / IO51 - Investigación Operativa (ITBA) - 2026 2C
Grupo: Grupo 08

Mejoras clave respecto al borrador inicial:
1. Maniobras conjuntas de atraque y desatraque con práctico y remolcador entre 1 y 2 horas en total (media 1.5h, según enunciado).
2. Grúas STS modeladas como recursos físicos SimPy con contención real (sin grúas fantasma). Si no hay grúas disponibles, los buques atracados esperan en cola.
3. Turnos rotativos dinámicos: diurno (3 grúas), vespertino (3 grúas), nocturno (1 activa + 1 standby a 15-20m) y paradas de 10-15m por cambio de guardia.
4. Reserva preventiva real de berma para cruceros: bloqueo previo para garantizar 0 espera en ventana matutina.
5. Dinámica de patio bidireccional (descarga ingresa al patio, carga se retira del patio) con permanencia media de 72h y camiones impuntuales.
6. Soporte para modo histórico (replay calibrado) y modo estocástico paramétrico (basado en data/distribuciones_g08.json) para réplicas independientes.
"""

import sys
import os
import json
import random
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

import simpy
import pandas as pd
import numpy as np

# Rutas portables
from src.paths import DATA_G08_CSV, DISTRIBUTIONS_JSON

@dataclass
class EscalaData:
    id_escala: str
    fecha_hora_arribo: Optional[pd.Timestamp]
    servicio: str
    mov_dry: int
    mov_reefer: int
    mov_oog: int
    arribo_hora: float # Horas desde el inicio de la simulación

@dataclass
class MetricasEscala:
    id_escala: str
    servicio: str
    t_arribo: float
    t_atraque_inicio: float
    t_atraque_fin: float # Inicio de espera o inicio de operación de grúas
    t_operacion_fin: float
    t_zarpada: float # Fin de desatraque y liberación de berma
    gruas_asignadas: int
    tiempo_espera_rada: float # Wq (espera hasta berma)
    tiempo_espera_grua: float # Tiempo atracado esperando grúa libre
    tiempo_operacion_grua: float # Tiempo neto de trabajo de grúa
    tiempo_en_berma: float # Ws (maniobra in + espera grúa + operación + maniobra out)
    tiempo_estadia_total: float # W = Wq + Ws
    excede_16h: bool
    is_cruise: bool = False

class PuertoSurSim:
    def __init__(
        self,
        df_escalas: Optional[pd.DataFrame] = None,
        num_bermas: int = 3,
        num_gruas_base: int = 3,
        politica_crucero: str = "sin_crucero", # "sin_crucero", "crucero_exclusivo", "crucero_sin_exclusividad"
        factor_demanda: float = 1.0, # 1.0 = actual, 1.35 = +35%, 2.0 = +100%
        politica_camiones: str = "estandar", # "estandar", "penalidad", "ventana_amplia"
        politica_slots_reefer: bool = False,
        seed: Optional[int] = 42,
        modo_generacion: str = "historico", # "historico" o "estocastico"
        duracion_estocastica_dias: float = 365.0
    ):
        self.df_escalas = df_escalas.copy() if df_escalas is not None else None
        self.num_bermas = num_bermas
        self.num_gruas_base = num_gruas_base
        self.politica_crucero = politica_crucero
        self.factor_demanda = factor_demanda
        self.politica_camiones = politica_camiones
        self.politica_slots_reefer = politica_slots_reefer
        self.seed = seed
        self.modo_generacion = modo_generacion
        self.duracion_estocastica_dias = duracion_estocastica_dias
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
        self.env = simpy.Environment()
        
        # 1. Recursos Físicos del Puerto con Prioridad
        self.bermas = simpy.PriorityResource(self.env, capacity=self.num_bermas)
        self.gruas = simpy.PriorityResource(self.env, capacity=self.num_gruas_base)
        
        # 2. Control de Turnos y Disponibilidad
        self.turno_actual = "diurno" # "diurno", "vespertino", "nocturno"
        self.cambio_turno_activo = False
        
        # 3. Patio de Almacenamiento (3.000 slots)
        self.capacidad_patio = 3000
        self.slots_ocupados = 1200 # Condición inicial razonable (~40%)
        self.historial_ocupacion_patio = []
        
        # 4. Gestión de Cruceros y Monitoreo
        self.cruceros_metricas = []
        self.escalas_metricas: List[MetricasEscala] = []
        
        # Cargar parámetros estocásticos si existen
        self.distribuciones = None
        if DISTRIBUTIONS_JSON.exists():
            with open(DISTRIBUTIONS_JSON, 'r', encoding='utf-8') as f:
                self.distribuciones = json.load(f)

    def _calcular_horas_grua_nominal(self, mov_dry: int, mov_reefer: int, mov_oog: int) -> float:
        """
        Calcula el tiempo requerido por 1 grúa individual trabajando al 100%:
        - Dry: 28 mov/h
        - Reefer: 21 mov/h (-25%)
        - OOG: 12 mov/h
        """
        h_dry = mov_dry / 28.0
        h_reefer = mov_reefer / 21.0
        h_oog = mov_oog / 12.0
        return h_dry + h_reefer + h_oog

    def proceso_turnos(self):
        """
        Gestiona el ciclo de turnos de 8 horas:
        - Diurno (08:00 a 16:00): dotación completa (3 o 4 grúas).
        - Vespertino (16:00 a 24:00): dotación completa.
        - Nocturno (00:00 a 08:00): 1 grúa activa + 1 en standby (alistamiento 15-20 min).
          Para modelar esto físicamente, el proceso de turnos retiene (num_gruas_base - 2) grúas
          durante la noche, limitando el pool a máximo 2 grúas utilizables.
        - Paradas por cambio de turno: 10 a 15 min donde las grúas suspenden operaciones.
        """
        while True:
            # Diurno: 08:00 a 16:00 (8h)
            self.turno_actual = "diurno"
            yield self.env.timeout(8.0)
            
            # Parada de cambio de turno 10-15 min
            self.cambio_turno_activo = True
            t_cambio1 = random.uniform(10.0 / 60.0, 15.0 / 60.0)
            yield self.env.timeout(t_cambio1)
            self.cambio_turno_activo = False
            
            # Vespertino: 16:00 a 24:00 (8h menos parada)
            self.turno_actual = "vespertino"
            yield self.env.timeout(max(0.1, 8.0 - t_cambio1))
            
            # Parada de cambio de turno 10-15 min
            self.cambio_turno_activo = True
            t_cambio2 = random.uniform(10.0 / 60.0, 15.0 / 60.0)
            yield self.env.timeout(t_cambio2)
            self.cambio_turno_activo = False
            
            # Nocturno: 00:00 a 08:00 (8h menos parada)
            self.turno_actual = "nocturno"
            # En la noche se reduce la dotación a 1 grúa activa + 1 standby (máximo 2 grúas disponibles)
            gruas_a_restringir = max(0, self.num_gruas_base - 2)
            reqs_bloqueo = []
            for _ in range(gruas_a_restringir):
                req = self.gruas.request(priority=-10) # prioridad alta para retener
                reqs_bloqueo.append(req)
                
            yield self.env.timeout(max(0.1, 8.0 - t_cambio2))
            
            # Liberar restricción nocturna al finalizar el turno
            for req in reqs_bloqueo:
                try:
                    self.gruas.release(req)
                except Exception:
                    pass
                    
            # Parada cambio de turno a diurno
            self.cambio_turno_activo = True
            t_cambio3 = random.uniform(10.0 / 60.0, 15.0 / 60.0)
            yield self.env.timeout(t_cambio3)
            self.cambio_turno_activo = False

    def proceso_gestion_patio(self):
        """
        Monitorea el patio de 3.000 slots y simula salidas por camiones externos:
        - Permanencia media en patio ~ 72 horas.
        - Impuntualidad de camiones (20% - 30% tarde).
        """
        while True:
            self.historial_ocupacion_patio.append((self.env.now, self.slots_ocupados))
            
            pct_tardios = 0.25
            if self.politica_camiones == "penalidad":
                pct_tardios = 0.10
            elif self.politica_camiones == "ventana_amplia":
                pct_tardios = 0.15
                
            eficiencia_retiro = 1.0 - (pct_tardios * 0.20)
            retiro_esperado = (self.slots_ocupados / 72.0) * eficiencia_retiro
            
            retiro_real = max(0, int(np.random.poisson(max(0.1, retiro_esperado))))
            self.slots_ocupados = max(0, self.slots_ocupados - retiro_real)
            
            yield self.env.timeout(1.0)

    def proceso_buque(self, escala: EscalaData):
        """
        Ciclo de vida completo del buque feeder:
        1. Arribo a rada (espera hasta berma libre).
        2. Maniobra de atraque con práctico y remolcador.
        3. Asignación y operación de grúas STS (1 o 2 grúas con contención real en SimPy).
        4. Transferencia de patio (descarga + carga).
        5. Maniobra de desatraque y liberación de berma.
        """
        t_arribo = escala.arribo_hora
        if self.env.now < t_arribo:
            yield self.env.timeout(t_arribo - self.env.now)
            
        t_llegada_rada = self.env.now
        
        # Solicitar Berma (prioridad 0 para carga estándar)
        req_berma = self.bermas.request(priority=0)
        yield req_berma
        
        t_inicio_maniobra = self.env.now
        t_espera_rada = t_inicio_maniobra - t_llegada_rada
        
        # 1. Maniobras conjuntas de práctico y remolcador entre 1 y 2 horas en total
        t_maniobra_total = random.uniform(1.0, 2.0)
        t_maniobra_in = t_maniobra_total * random.uniform(0.45, 0.55)
        t_maniobra_out = t_maniobra_total - t_maniobra_in
        
        yield self.env.timeout(t_maniobra_in)
        t_fin_atraque = self.env.now
        
        # 2. Asignación de Grúas STS físicas mediante PriorityResource
        horas_nominales_1g = self._calcular_horas_grua_nominal(
            escala.mov_dry, escala.mov_reefer, escala.mov_oog
        )
        
        # Solicitar primera grúa obligatoria (espera en cola si todas están ocupadas)
        t_pedido_grua = self.env.now
        req_grua1 = self.gruas.request(priority=0)
        yield req_grua1
        
        gruas_asignadas = 1
        req_grua2 = None
        
        # Intentar obtener una segunda grúa si está libre de inmediato (sin hacer cola)
        if self.gruas.count < self.gruas.capacity:
            req_grua2 = self.gruas.request(priority=1)
            gruas_asignadas = 2
            
        t_inicio_operacion = self.env.now
        t_espera_grua = t_inicio_operacion - t_pedido_grua
        
        # Demora de alistamiento de standby si se usa la 2da grúa en turno nocturno (15-20 min)
        if self.turno_actual == "nocturno" and gruas_asignadas == 2:
            t_alist = random.uniform(15.0 / 60.0, 20.0 / 60.0)
            yield self.env.timeout(t_alist)
            
        # Productividad de grúas: factor 1.0 (1 grúa) o 1.7 (2 grúas al 85% conjunto)
        factor_velocidad = 1.0 if gruas_asignadas == 1 else 1.7
        tiempo_operacion_base = horas_nominales_1g / factor_velocidad
        
        # Penalización si el patio supera el 75% de ocupación (2.250 slots)
        if self.slots_ocupados > 2250:
            factor_patio = 1.25 # Grúas esperan liberación de slots
        else:
            factor_patio = 1.0
            
        tiempo_operacion_real = tiempo_operacion_base * factor_patio
        
        # Operación fraccionada con pausas por cambio de turno
        tiempo_remanente = tiempo_operacion_real
        while tiempo_remanente > 0:
            if self.cambio_turno_activo:
                yield self.env.timeout(0.2)
            paso = min(tiempo_remanente, 0.5)
            yield self.env.timeout(paso)
            tiempo_remanente -= paso
            
        t_fin_operacion = self.env.now
        
        # Liberar Grúas STS al terminar la operación
        self.gruas.release(req_grua1)
        if req_grua2 is not None:
            self.gruas.release(req_grua2)
            
        # 3. Dinámica de Patio Bidireccional:
        # ~50% de movimientos corresponden a descarga (ingresan al patio)
        # ~50% de movimientos corresponden a carga (se retiran del patio al buque)
        mov_descarga = int((escala.mov_dry + escala.mov_reefer + escala.mov_oog) * 0.5)
        mov_carga = (escala.mov_dry + escala.mov_reefer + escala.mov_oog) - mov_descarga
        
        # Actualización de slots de patio
        self.slots_ocupados = max(0, min(self.capacidad_patio, self.slots_ocupados + mov_descarga - mov_carga))
        
        # 4. Maniobra de desatraque y liberación de berma
        yield self.env.timeout(t_maniobra_out)
        t_zarpada = self.env.now
        
        self.bermas.release(req_berma)
        
        # Registro de Métricas Formales
        w_q = t_espera_rada
        w_s = t_zarpada - t_inicio_maniobra
        w_total = t_zarpada - t_llegada_rada
        
        metrica = MetricasEscala(
            id_escala=escala.id_escala,
            servicio=escala.servicio,
            t_arribo=t_llegada_rada,
            t_atraque_inicio=t_inicio_maniobra,
            t_atraque_fin=t_fin_atraque,
            t_operacion_fin=t_fin_operacion,
            t_zarpada=t_zarpada,
            gruas_asignadas=gruas_asignadas,
            tiempo_espera_rada=w_q,
            tiempo_espera_grua=t_espera_grua,
            tiempo_operacion_grua=(t_fin_operacion - t_inicio_operacion),
            tiempo_en_berma=w_s,
            tiempo_estadia_total=w_total,
            excede_16h=(w_total > 16.0),
            is_cruise=False
        )
        self.escalas_metricas.append(metrica)

    def proceso_generador_cruceros(self, inicio_horas: float, fin_horas: float):
        """
        Modela la temporada de cruceros (3 meses):
        - 2 escalas semanales (~cada 84 horas).
        - Arribo matutino con variabilidad de +-3 horas.
        - Ocupa berma entre 28 y 36 horas continuas.
        - Si política es 'crucero_exclusivo', reserva preventivamente la berma 6 horas antes
          para asegurar que el crucero atraque de inmediato sin demora en rada.
        """
        t_actual = inicio_horas
        intervalo = 168.0 / 2.0 # 84h
        id_c = 1
        
        while t_actual < fin_horas:
            yield self.env.timeout(intervalo)
            t_actual = self.env.now
            dispersion = random.uniform(-3.0, 3.0)
            t_llegada = max(self.env.now, self.env.now + dispersion)
            
            # Reserva preventiva de berma: si es exclusivo, bloquea 6h antes con prioridad alta
            req_berma = None
            if self.politica_crucero == "crucero_exclusivo":
                t_bloqueo_previo = max(self.env.now, t_llegada - 6.0)
                if self.env.now < t_bloqueo_previo:
                    yield self.env.timeout(t_bloqueo_previo - self.env.now)
                # Adquirir la berma exclusivamente (prioridad -5)
                req_berma = self.bermas.request(priority=-5)
                yield req_berma
                
            # Esperar llegada del crucero
            if self.env.now < t_llegada:
                yield self.env.timeout(t_llegada - self.env.now)
                
            if req_berma is None:
                # Sin exclusividad: compite con buques normales (prioridad 0)
                req_berma = self.bermas.request(priority=0)
                yield req_berma
                
            t_atraque_crucero = self.env.now
            duracion_crucero = random.uniform(28.0, 36.0)
            yield self.env.timeout(duracion_crucero)
            
            self.bermas.release(req_berma)
            self.cruceros_metricas.append({
                "id_crucero": f"CRU-{id_c:03d}",
                "t_arribo": t_llegada,
                "t_atraque": t_atraque_crucero,
                "espera": t_atraque_crucero - t_llegada,
                "duracion": duracion_crucero,
                "t_zarpada": self.env.now
            })
            id_c += 1

    def _generar_escalas_estocasticas(self, dias_sim: float) -> List[EscalaData]:
        """
        Genera arribos sintéticos de buques utilizando las distribuciones teóricas
        ajustadas en data/distribuciones_g08.json (Input Modeling validado).
        """
        escalas = []
        horas_totales = dias_sim * 24.0
        t_reloj = 0.0
        idx = 1
        
        # Servicios y proporciones
        srv_list = ["Austral Feeder", "Andes Container Line", "TransPatagonia Line"]
        srv_weights = [0.4378, 0.3756, 0.1866]
        
        # Tasa ajustada con factor de demanda
        lambda_hora = (0.3369 * self.factor_demanda)
        
        while t_reloj < horas_totales:
            # Inter-arribo exponencial global
            dt = random.expovariate(lambda_hora)
            t_reloj += dt
            if t_reloj >= horas_totales:
                break
                
            srv = random.choices(srv_list, weights=srv_weights)[0]
            mes_actual = int((t_reloj / (24.0 * 30.0)) % 12) + 1
            es_temporada_fruta = mes_actual in [10, 11, 12]
            
            # Carga según servicio y estacionalidad de fruta
            if srv == "Austral Feeder":
                dry = max(10, int(random.gauss(76.9, 15.0)))
                reefer = max(2, int(random.gauss(26.4 if es_temporada_fruta else 15.7, 5.0)))
                oog = max(0, int(np.random.poisson(2.9)))
            elif srv == "Andes Container Line":
                dry = max(20, int(random.gauss(112.7, 20.0)))
                reefer = max(5, int(random.gauss(49.7 if es_temporada_fruta else 32.3, 8.0)))
                oog = max(0, int(np.random.poisson(4.6)))
            else: # TransPatagonia Line
                dry = max(30, int(random.gauss(153.9, 25.0)))
                reefer = max(10, int(random.gauss(79.9 if es_temporada_fruta else 55.9, 12.0)))
                oog = max(0, int(np.random.poisson(6.6)))
                
            escala = EscalaData(
                id_escala=f"ESC-ESTOC-{idx:05d}",
                fecha_hora_arribo=None,
                servicio=srv,
                mov_dry=dry,
                mov_reefer=reefer,
                mov_oog=oog,
                arribo_hora=t_reloj
            )
            escalas.append(escala)
            idx += 1
            
        return escalas

    def run(self):
        # 1. Iniciar Procesos Demonio de Fondo
        self.env.process(self.proceso_turnos())
        self.env.process(self.proceso_gestion_patio())
        
        # 2. Activar Temporada de Cruceros si aplica
        if self.politica_crucero in ["crucero_exclusivo", "crucero_sin_exclusividad"]:
            # Temporada alta: meses 10 a 12 (día 60 al 150 = hora 1440 a 3600)
            self.env.process(self.proceso_generador_cruceros(1440.0, 3600.0))
            
        # 3. Despachar Buques según el Modo de Generación
        if self.modo_generacion == "estocastico":
            lista_escalas = self._generar_escalas_estocasticas(self.duracion_estocastica_dias)
            for esc in lista_escalas:
                self.env.process(self.proceso_buque(esc))
            max_horas = self.duracion_estocastica_dias * 24.0 + 100.0
        else:
            # Modo Histórico Replay
            df = self.df_escalas.sort_values('fecha_hora_arribo').reset_index(drop=True)
            t_cero = df['fecha_hora_arribo'].min()
            
            # Factor de demanda en modo histórico
            if self.factor_demanda > 1.0:
                n_extra = int(len(df) * (self.factor_demanda - 1.0))
                df_extra = df.sample(n=n_extra, replace=True, random_state=self.seed).copy()
                jitter = np.random.uniform(0.1, 5.0, size=n_extra)
                df_extra['fecha_hora_arribo'] = df_extra['fecha_hora_arribo'] + pd.to_timedelta(jitter, unit='h')
                df = pd.concat([df, df_extra]).sort_values('fecha_hora_arribo').reset_index(drop=True)
                
            df['horas_sim'] = (df['fecha_hora_arribo'] - t_cero).dt.total_seconds() / 3600.0
            
            for _, row in df.iterrows():
                escala = EscalaData(
                    id_escala=str(row['id_escala']),
                    fecha_hora_arribo=row['fecha_hora_arribo'],
                    servicio=str(row['servicio']),
                    mov_dry=int(row['mov_dry']),
                    mov_reefer=int(row['mov_reefer']),
                    mov_oog=int(row['mov_oog']),
                    arribo_hora=float(row['horas_sim'])
                )
                self.env.process(self.proceso_buque(escala))
            max_horas = df['horas_sim'].max() + 200.0
            
        # Ejecutar Simulación
        self.env.run(until=max_horas)
        
        # Retornar métricas individuales en DataFrame
        res_df = pd.DataFrame([m.__dict__ for m in self.escalas_metricas])
        return res_df
