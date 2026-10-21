"""
Simulador de Eventos Discretos de la Terminal Portuaria Puerto Sur
Asignatura: 11.51 / IO51 - Investigación Operativa (ITBA) - 2026 2C
Grupo: Grupo 08
"""

import simpy
import random
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class EscalaData:
    id_escala: str
    fecha_hora_arribo: pd.Timestamp
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
    t_atraque_fin: float # Inicio de operación de grúas
    t_operacion_fin: float
    t_zarpada: float # Fin de desatraque
    gruas_asignadas_prom: float
    tiempo_espera_rada: float # Wq
    tiempo_operacion_grua: float
    tiempo_en_berma: float # Ws
    tiempo_estadia_total: float # W = Wq + Ws
    excede_16h: bool
    is_cruise: bool = False

class PuertoSurSim:
    def __init__(
        self,
        df_escalas: pd.DataFrame,
        num_bermas: int = 3,
        num_gruas_base: int = 3,
        politica_crucero: str = "sin_crucero", # "sin_crucero", "crucero_exclusivo", "crucero_sin_exclusividad"
        factor_demanda: float = 1.0, # 1.0 = actual, 1.35 = +35%, 2.0 = +100%
        politica_camiones: str = "estandar", # "estandar", "penalidad", "ventana_amplia"
        politica_slots_reefer: bool = False,
        seed: Optional[int] = 42
    ):
        self.df_escalas = df_escalas.copy()
        self.num_bermas = num_bermas
        self.num_gruas_base = num_gruas_base
        self.politica_crucero = politica_crucero
        self.factor_demanda = factor_demanda
        self.politica_camiones = politica_camiones
        self.politica_slots_reefer = politica_slots_reefer
        self.seed = seed
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
        self.env = simpy.Environment()
        
        # Recursos
        self.bermas = simpy.Resource(self.env, capacity=self.num_bermas)
        
        # Grúas: representadas por un recurso o contador dinámico
        # La dotación cambia según el turno:
        # 08:00 - 16:00 (Diurno): num_gruas_base
        # 16:00 - 24:00 (Vespertino): num_gruas_base
        # 00:00 - 08:00 (Nocturno): 1 activa + 1 en standby (alistamiento 15-20 min)
        self.gruas_totales_disponibles = self.num_gruas_base
        self.gruas_en_uso = 0
        self.turno_actual = "diurno" # "diurno", "vespertino", "nocturno"
        self.cambio_turno_activo = False
        
        # Patio de almacenamiento
        self.capacidad_patio = 3000
        self.slots_ocupados = 1200 # Condición inicial razonable (~40% ocupación)
        self.historial_ocupacion_patio = []
        
        # Monitoreo
        self.escalas_metricas: List[MetricasEscala] = []
        self.cruceros_metricas = []
        
        # Berma reservada para crucero
        self.berma_reservada_crucero = False
        
    def _calcular_horas_grua_nominal(self, mov_dry: int, mov_reefer: int, mov_oog: int) -> float:
        """Calcula el tiempo requerido por 1 grúa individual trabajando al 100%"""
        # Dry: 28 mov/h | Reefer: 21 mov/h (-25%) | OOG: 12 mov/h
        h_dry = mov_dry / 28.0
        h_reefer = mov_reefer / 21.0
        h_oog = mov_oog / 12.0
        return h_dry + h_reefer + h_oog

    def proceso_turnos(self):
        """Gestiona el ciclo de turnos de 8 horas, dotaciones nocturnas y paradas por cambio de turno"""
        while True:
            # Diurno: 08:00 a 16:00 (8 horas)
            self.turno_actual = "diurno"
            self.gruas_totales_disponibles = self.num_gruas_base
            yield self.env.timeout(8.0)
            
            # Parada cambio de turno 10 a 15 min (0.167 a 0.25 h)
            self.cambio_turno_activo = True
            t_cambio = random.uniform(10.0 / 60.0, 15.0 / 60.0)
            yield self.env.timeout(t_cambio)
            self.cambio_turno_activo = False
            
            # Vespertino: 16:00 a 24:00 (8 horas - t_cambio)
            self.turno_actual = "vespertino"
            self.gruas_totales_disponibles = self.num_gruas_base
            yield self.env.timeout(8.0 - t_cambio)
            
            # Parada cambio de turno
            self.cambio_turno_activo = True
            t_cambio = random.uniform(10.0 / 60.0, 15.0 / 60.0)
            yield self.env.timeout(t_cambio)
            self.cambio_turno_activo = False
            
            # Nocturno: 00:00 a 08:00 (8 horas - t_cambio)
            # En turno nocturno: 1 grúa activa + 1 en standby (alistamiento 15-20 min).
            # Si hay 4 grúas base, supongamos 2 activas + 1 standby
            self.turno_actual = "nocturno"
            if self.num_gruas_base == 3:
                self.gruas_totales_disponibles = 2 # 1 activa + 1 standby
            else:
                self.gruas_totales_disponibles = 2 # con 4 grúas, puede disponer 2 activas + 1 standby
            yield self.env.timeout(8.0 - t_cambio)
            
            # Parada cambio de turno
            self.cambio_turno_activo = True
            t_cambio = random.uniform(10.0 / 60.0, 15.0 / 60.0)
            yield self.env.timeout(t_cambio)
            self.cambio_turno_activo = False

    def proceso_gestion_patio(self):
        """Registra ocupación de patio y actualiza salidas de contenedores por camiones externos"""
        while True:
            # Monitoreo cada 1 hora
            self.historial_ocupacion_patio.append((self.env.now, self.slots_ocupados))
            
            # Salidas naturales de contenedores (tiempo de permanencia medio ~ 72 horas)
            # Tasa de retiro diaria = slots_ocupados / 72 * delta_t
            # Se ve afectado por impuntualidad de camiones (20-30% tarde)
            pct_tardios = 0.25
            if self.politica_camiones == "penalidad":
                pct_tardios = 0.10 # reduce impuntualidad por penalidades
            elif self.politica_camiones == "ventana_amplia":
                pct_tardios = 0.15
                
            eficiencia_retiro = 1.0 - (pct_tardios * 0.20)
            retiro_esperado = (self.slots_ocupados / 72.0) * eficiencia_retiro
            
            # Ruido estocástico
            retiro_real = max(0, int(np.random.poisson(max(1, retiro_esperado))))
            self.slots_ocupados = max(0, self.slots_ocupados - retiro_real)
            
            yield self.env.timeout(1.0)

    def proceso_buque(self, escala: EscalaData):
        t_arribo = escala.arribo_hora
        # Esperar hasta el tiempo de arribo
        if self.env.now < t_arribo:
            yield self.env.timeout(t_arribo - self.env.now)
            
        t_llegada_rada = self.env.now
        
        # Si hay crucero exclusivo y las bermas libres quedarían en 0, esperar
        req_berma = self.bermas.request()
        yield req_berma
        
        t_inicio_maniobra = self.env.now
        t_espera_rada = t_inicio_maniobra - t_llegada_rada
        
        # 1. Maniobra de atraque (1 a 2 horas)
        t_maniobra_in = random.uniform(1.0, 2.0)
        yield self.env.timeout(t_maniobra_in)
        
        t_inicio_operacion = self.env.now
        
        # 2. Operación de carga y descarga
        # Cantidad de movimientos de grúa
        horas_nominales_1grua = self._calcular_horas_grua_nominal(
            escala.mov_dry, escala.mov_reefer, escala.mov_oog
        )
        
        # Determinar si puede recibir 1 o 2 grúas
        # Política: asigna hasta 2 grúas si hay grúas disponibles
        gruas_asignables = 1
        gruas_libres = max(0, self.gruas_totales_disponibles - self.gruas_en_uso)
        if gruas_libres >= 2:
            gruas_asignables = 2
        elif gruas_libres == 1:
            gruas_asignables = 1
        else:
            gruas_asignables = 1 # espera o comparte
            
        self.gruas_en_uso += gruas_asignables
        
        # Si es turno nocturno y usa la 2da grúa (standby), tiempo de alistamiento de 15-20 min
        if self.turno_actual == "nocturno" and gruas_asignables == 2:
            t_alist = random.uniform(15.0 / 60.0, 20.0 / 60.0)
            yield self.env.timeout(t_alist)
            
        # Velocidad de trabajo
        # Si son 2 grúas: interferencia mutua reduce al 85% de la suma (factor 1.7)
        factor_velocidad = 1.0 if gruas_asignables == 1 else 1.7
        
        # Tiempo base de operación
        tiempo_operacion_base = horas_nominales_1grua / factor_velocidad
        
        # Penalidad si el patio está congestionado (>75% de ocupación = >2250 slots)
        if self.slots_ocupados > 2250:
            # Grúas deben esperar liberación de slots
            factor_patio = 1.25 # demora 25% extra por congestión de patio
        else:
            factor_patio = 1.0
            
        tiempo_operacion_real = tiempo_operacion_base * factor_patio
        
        # Operación fraccionada para considerar cambios de turno si ocurren durante la atención
        tiempo_remanente = tiempo_operacion_real
        while tiempo_remanente > 0:
            if self.cambio_turno_activo:
                yield self.env.timeout(0.2) # espera fin de cambio de turno
            paso = min(tiempo_remanente, 1.0)
            yield self.env.timeout(paso)
            tiempo_remanente -= paso
            
        self.gruas_en_uso = max(0, self.gruas_en_uso - gruas_asignables)
        
        # Movimientos de descarga ingresan al patio (~50% del total de movimientos)
        contenedores_descargados = int((escala.mov_dry + escala.mov_reefer + escala.mov_oog) * 0.5)
        self.slots_ocupados = min(self.capacidad_patio, self.slots_ocupados + contenedores_descargados)
        
        t_fin_operacion = self.env.now
        
        # 3. Maniobra de desatraque (1 a 2 horas)
        t_maniobra_out = random.uniform(1.0, 2.0)
        yield self.env.timeout(t_maniobra_out)
        
        t_zarpada = self.env.now
        
        # Liberar berma
        self.bermas.release(req_berma)
        
        # Registro de métricas
        w_q = t_espera_rada
        w_s = t_zarpada - t_inicio_maniobra
        w_total = t_zarpada - t_llegada_rada
        
        metrica = MetricasEscala(
            id_escala=escala.id_escala,
            servicio=escala.servicio,
            t_arribo=t_llegada_rada,
            t_atraque_inicio=t_inicio_maniobra,
            t_atraque_fin=t_inicio_operacion,
            t_operacion_fin=t_fin_operacion,
            t_zarpada=t_zarpada,
            gruas_asignadas_prom=gruas_asignables,
            tiempo_espera_rada=w_q,
            tiempo_operacion_grua=(t_fin_operacion - t_inicio_operacion),
            tiempo_en_berma=w_s,
            tiempo_estadia_total=w_total,
            excede_16h=(w_total > 16.0),
            is_cruise=False
        )
        self.escalas_metricas.append(metrica)

    def proceso_generador_cruceros(self, inicio_horas: float, fin_horas: float):
        """Genera 2 escalas de crucero por semana durante la temporada alta (meses 10 a 12)"""
        t_actual = inicio_horas
        intervalo_crucero = 168.0 / 2.0 # 84 horas entre escalas
        id_c = 1
        
        while t_actual < fin_horas:
            yield self.env.timeout(intervalo_crucero)
            t_actual = self.env.now
            # Variabilidad de arribo matutino +- 3 horas
            dispersion = random.uniform(-3.0, 3.0)
            t_llegada_crucero = max(self.env.now, self.env.now + dispersion)
            
            if self.env.now < t_llegada_crucero:
                yield self.env.timeout(t_llegada_crucero - self.env.now)
                
            # Ocupa berma completa entre 28 y 36 horas
            req_berma = self.bermas.request()
            yield req_berma
            
            duracion_crucero = random.uniform(28.0, 36.0)
            yield self.env.timeout(duracion_crucero)
            
            self.bermas.release(req_berma)
            self.cruceros_metricas.append({
                "id_crucero": f"CRU-{id_c:03d}",
                "t_arribo": t_llegada_crucero,
                "duracion": duracion_crucero,
                "t_zarpada": self.env.now
            })
            id_c += 1

    def run(self):
        # Iniciar procesos demonio
        self.env.process(self.proceso_turnos())
        self.env.process(self.proceso_gestion_patio())
        
        # Procesar escalas de buques
        df = self.df_escalas.sort_values('fecha_hora_arribo').reset_index(drop=True)
        t_cero = df['fecha_hora_arribo'].min()
        
        # Ajustar factor de demanda si corresponde
        if self.factor_demanda > 1.0:
            # Generar arribos adicionales proporcionales
            n_extra = int(len(df) * (self.factor_demanda - 1.0))
            df_extra = df.sample(n=n_extra, replace=True).copy()
            # Asignar arribos estocásticos intercalados
            jitter = np.random.uniform(0.1, 5.0, size=n_extra)
            df_extra['fecha_hora_arribo'] = df_extra['fecha_hora_arribo'] + pd.to_timedelta(jitter, unit='h')
            df = pd.concat([df, df_extra]).sort_values('fecha_hora_arribo').reset_index(drop=True)
            
        df['horas_sim'] = (df['fecha_hora_arribo'] - t_cero).dt.total_seconds() / 3600.0
        
        # Si aplica temporada de cruceros:
        if self.politica_crucero in ["crucero_exclusivo", "crucero_sin_exclusividad"]:
            # Activar cruceros en los meses 10, 11 y 12 de cada año
            # En la simulación aproximamos inicio en el día 60 (hora 1440) durante 90 días (2160 h)
            self.env.process(self.proceso_generador_cruceros(1440.0, 1440.0 + 2160.0))
            
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
            
        # Ejecutar hasta el final de las escalas registradas
        max_horas = df['horas_sim'].max() + 200.0
        self.env.run(until=max_horas)
        
        # Retornar DataFrame con resultados individuales
        res_df = pd.DataFrame([m.__dict__ for m in self.escalas_metricas])
        return res_df
