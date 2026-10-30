"""Simulador de eventos discretos para la Terminal Portuaria Puerto Sur.

La simulación usa el replay histórico como referencia. El modo estocástico
remuestrea bloques semanales del histórico para conservar agrupamientos,
servicio y mezcla de movimientos. Las salidas de ambos modos dependen de los
supuestos operativos documentados en docs/MODELO_DE_DATOS_Y_MODELO_OPERATIVO_G08.md.
"""

from dataclasses import dataclass
from datetime import datetime
import math
import random
from typing import List, Optional

import numpy as np
import pandas as pd
import simpy

from src.paths import DATA_G08_CSV


@dataclass
class EscalaData:
    id_escala: str
    fecha_hora_arribo: Optional[pd.Timestamp]
    servicio: str
    mov_dry: int
    mov_reefer: int
    mov_oog: int
    arribo_hora: float


@dataclass
class MetricasEscala:
    id_escala: str
    servicio: str
    t_arribo: float
    t_atraque_inicio: float
    t_atraque_fin: float
    t_operacion_inicio: float
    t_operacion_fin: float
    t_zarpada: float
    gruas_asignadas: int
    mov_descarga: int
    mov_carga: int
    tiempo_espera_rada: float
    tiempo_espera_grua: float
    tiempo_operacion_grua: float
    tiempo_en_berma: float
    tiempo_estadia_total: float
    excede_16h: bool
    tiempo_espera_patio: float = 0.0
    tiempo_alistamiento_grua: float = 0.0
    tiempo_pausa_turno: float = 0.0
    tiempo_trabajo_efectivo: float = 0.0
    slots_patio_final: int = 0
    is_cruise: bool = False


class PuertoSurSim:
    """Modelo del sistema con recursos compartidos y capacidad finita de patio."""

    CAPACIDAD_PATIO = 3000
    OCUPACION_INICIAL_PATIO = 1200
    TIEMPO_MEDIO_PATIO_H = 72.0
    DURACION_CAMBIO_TURNO_MIN = 10.0 / 60.0
    DURACION_CAMBIO_TURNO_MAX = 15.0 / 60.0
    TAMANO_BLOQUE_ESTOCASTICO_H = 7.0 * 24.0

    def __init__(
        self,
        df_escalas: Optional[pd.DataFrame] = None,
        num_bermas: int = 3,
        num_gruas_base: int = 3,
        politica_crucero: str = "sin_crucero",
        factor_demanda: float = 1.0,
        politica_camiones: str = "estandar",
        politica_slots_reefer: bool = False,
        seed: Optional[int] = 42,
        modo_generacion: str = "historico",
        duracion_estocastica_dias: float = 365.0,
        ocupacion_inicial_patio: int = OCUPACION_INICIAL_PATIO,
    ):
        if num_bermas < 1 or num_gruas_base < 1:
            raise ValueError("Debe haber al menos una berma y una grúa.")
        if factor_demanda <= 0:
            raise ValueError("factor_demanda debe ser mayor que cero.")
        if duracion_estocastica_dias <= 0:
            raise ValueError("duracion_estocastica_dias debe ser mayor que cero.")
        if politica_crucero not in {
            "sin_crucero",
            "crucero_exclusivo",
            "crucero_sin_exclusividad",
        }:
            raise ValueError("politica_crucero no reconocida.")
        if politica_camiones not in {"estandar", "penalidad", "ventana_amplia"}:
            raise ValueError("politica_camiones no reconocida.")
        if modo_generacion not in {"historico", "estocastico"}:
            raise ValueError("modo_generacion debe ser 'historico' o 'estocastico'.")
        if not 0 <= ocupacion_inicial_patio <= self.CAPACIDAD_PATIO:
            raise ValueError("La ocupación inicial debe estar entre 0 y 3.000 slots.")

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
        self.rng = random.Random(seed)
        self.np_rng = np.random.default_rng(seed)

        self.env = simpy.Environment()
        self.bermas = simpy.PriorityResource(self.env, capacity=num_bermas)
        self.gruas = simpy.PriorityResource(self.env, capacity=num_gruas_base)

        self.turno_actual = "nocturno"  # t=0 representa las 00:00.
        self.cambio_turno_activo = False
        self._evento_inicio_cambio = self.env.event()
        self._evento_fin_cambio = self.env.event()
        self._evento_disponibilidad_gruas = self.env.event()

        self.capacidad_patio = self.CAPACIDAD_PATIO
        self.patio = simpy.Container(
            self.env,
            capacity=self.capacidad_patio,
            init=ocupacion_inicial_patio,
        )
        # La mezcla inicial por dirección no se observa; se adopta 50/50.
        self.stock_exportacion = ocupacion_inicial_patio // 2
        self.stock_importacion = ocupacion_inicial_patio - self.stock_exportacion
        self._evento_stock_exportacion = self.env.event()
        self.historial_ocupacion_patio: List[tuple] = []
        self.cruceros_metricas = []
        self.escalas_metricas: List[MetricasEscala] = []
        self.fecha_inicio_sim: Optional[pd.Timestamp] = None
        self._ejecutada = False

    @property
    def slots_ocupados(self) -> int:
        """Ocupación actual del contenedor SimPy, redondeada a slots enteros."""
        return int(round(self.patio.level))

    def _calcular_horas_grua_nominal(
        self, mov_dry: int, mov_reefer: int, mov_oog: int
    ) -> float:
        """Horas de trabajo de una grúa: dry 28, reefer 21 y OOG 12 mov/h."""
        return mov_dry / 28.0 + mov_reefer / 21.0 + mov_oog / 12.0

    def _turno_para_hora(self, hora: float) -> str:
        hora_del_dia = hora % 24.0
        if hora_del_dia < 8.0:
            return "nocturno"
        if hora_del_dia < 16.0:
            return "diurno"
        return "vespertino"

    def _notificar_disponibilidad_gruas(self) -> None:
        evento = self._evento_disponibilidad_gruas
        if not evento.triggered:
            evento.succeed()
        self._evento_disponibilidad_gruas = self.env.event()

    def _notificar_stock_exportacion(self) -> None:
        evento = self._evento_stock_exportacion
        if not evento.triggered:
            evento.succeed()
        self._evento_stock_exportacion = self.env.event()

    def proceso_turnos(self):
        """Aplica cambios 00/08/16 y pausa de grúas de 10 a 15 minutos."""
        proxima_frontera = 8.0
        while True:
            yield self.env.timeout(max(0.0, proxima_frontera - self.env.now))
            evento_fin = self.env.event()
            self._evento_fin_cambio = evento_fin
            self.cambio_turno_activo = True
            self._evento_inicio_cambio.succeed()
            self._notificar_disponibilidad_gruas()

            duracion = self.rng.uniform(
                self.DURACION_CAMBIO_TURNO_MIN,
                self.DURACION_CAMBIO_TURNO_MAX,
            )
            yield self.env.timeout(duracion)

            self.cambio_turno_activo = False
            self.turno_actual = self._turno_para_hora(proxima_frontera)
            evento_fin.succeed()
            self._evento_inicio_cambio = self.env.event()
            self._notificar_disponibilidad_gruas()
            proxima_frontera += 8.0

    def _limite_gruas_para_inicio(self) -> int:
        # Durante la noche comienza una sola grúa; la segunda puede habilitarse
        # como standby para el mismo buque si está libre.
        if self.turno_actual == "nocturno":
            return 1
        return self.num_gruas_base

    def _limite_gruas_para_equipo(self) -> int:
        if self.turno_actual == "nocturno":
            return min(2, self.num_gruas_base)
        return self.num_gruas_base

    def _solicitar_grua_principal(self):
        """Espera sin crear solicitudes huérfanas en la cola de SimPy."""
        while True:
            if self.cambio_turno_activo:
                yield self._evento_fin_cambio
                continue

            limite = min(self._limite_gruas_para_inicio(), self.gruas.capacity)
            if self.gruas.count < limite and not self.gruas.queue:
                solicitud = self.gruas.request(priority=0)
                yield solicitud
                return solicitud

            evento = self._evento_disponibilidad_gruas
            yield evento

    def _intentar_segunda_grua(self):
        """Toma la segunda grúa solo si se concede de inmediato; nunca la simula antes."""
        if self.cambio_turno_activo:
            return None
        limite = min(self._limite_gruas_para_equipo(), self.gruas.capacity)
        if self.gruas.count >= limite or self.gruas.queue:
            return None

        solicitud = self.gruas.request(priority=1)
        yield solicitud
        return solicitud

    def _trabajar_horas_efectivas(self, horas: float):
        """Consume horas productivas y detiene el trabajo durante cada relevo."""
        restantes = max(0.0, float(horas))
        pausa_total = 0.0
        epsilon = 1e-9

        while restantes > epsilon:
            if self.cambio_turno_activo:
                inicio_pausa = self.env.now
                yield self._evento_fin_cambio
                pausa_total += self.env.now - inicio_pausa
                continue

            proxima_frontera = (math.floor(self.env.now / 8.0) + 1) * 8.0
            hasta_frontera = proxima_frontera - self.env.now
            if hasta_frontera <= epsilon:
                yield self.env.timeout(0)
                continue

            if restantes <= hasta_frontera + epsilon:
                yield self.env.timeout(restantes)
                restantes = 0.0
                continue

            yield self.env.timeout(hasta_frontera)
            restantes -= hasta_frontera
            if not self.cambio_turno_activo:
                yield self._evento_inicio_cambio
            inicio_pausa = self.env.now
            yield self._evento_fin_cambio
            pausa_total += self.env.now - inicio_pausa

        return pausa_total

    def proceso_gestion_patio(self):
        """Retiro agregado con permanencia media de 72 h y capacidad física finita.

        La impuntualidad se incorpora como una reducción de disponibilidad dentro
        del rango de sensibilidad usado en el repositorio. La magnitud de su efecto
        es un supuesto de escenario, no una estimación causal de una política real.
        """
        fraccion_tardia = {
            "estandar": 0.25,
            "penalidad": 0.10,
            "ventana_amplia": 0.15,
        }[self.politica_camiones]
        eficiencia = 1.0 - fraccion_tardia * 0.20

        while True:
            self.historial_ocupacion_patio.append(
                (self.env.now, self.slots_ocupados)
            )
            media_retiro = max(
                0.0, self.stock_importacion / self.TIEMPO_MEDIO_PATIO_H * eficiencia
            )
            retiro = int(self.np_rng.poisson(media_retiro))
            retiro = min(retiro, self.stock_importacion)
            if retiro:
                yield self.patio.get(retiro)
                self.stock_importacion -= retiro
            yield self.env.timeout(1.0)

    @staticmethod
    def _movimientos_por_direccion(escala: EscalaData) -> tuple[int, int]:
        total = escala.mov_dry + escala.mov_reefer + escala.mov_oog
        # Aproximación 50/50. Cuando el total es impar, la unidad sobrante se
        # asigna a carga, que llega previamente por camión según el supuesto de
        # permanencia de 72 h.
        return total // 2, (total + 1) // 2

    def proceso_llegada_exportacion(self, escala: EscalaData, t_entrega: float):
        """Representa exportaciones que llegan por camión antes de la escala."""
        if self.env.now < t_entrega:
            yield self.env.timeout(t_entrega - self.env.now)
        _, mov_carga = self._movimientos_por_direccion(escala)
        if mov_carga:
            yield self.patio.put(mov_carga)
            self.stock_exportacion += mov_carga
            self._notificar_stock_exportacion()

    def proceso_buque(self, escala: EscalaData):
        """Atiende un buque y registra sus tiempos en rada, berma y transferencia."""
        if self.env.now < escala.arribo_hora:
            yield self.env.timeout(escala.arribo_hora - self.env.now)

        t_llegada_rada = self.env.now
        req_berma = self.bermas.request(priority=0)
        yield req_berma
        t_inicio_maniobra = self.env.now
        t_espera_rada = t_inicio_maniobra - t_llegada_rada

        maniobra_total = self.rng.uniform(1.0, 2.0)
        maniobra_in = maniobra_total * self.rng.uniform(0.45, 0.55)
        maniobra_out = maniobra_total - maniobra_in
        yield self.env.timeout(maniobra_in)
        t_fin_atraque = self.env.now

        mov_descarga, mov_carga = self._movimientos_por_direccion(escala)

        # La exportación debe estar disponible en el patio. El plazo de entrega
        # terrestre de 72 h se usa como supuesto central hasta tener sus marcas.
        inicio_reserva = self.env.now
        while self.stock_exportacion < mov_carga:
            evento = self._evento_stock_exportacion
            yield evento
        self.stock_exportacion -= mov_carga
        t_espera_patio = self.env.now - inicio_reserva

        t_pedido_grua = self.env.now
        req_grua1 = yield from self._solicitar_grua_principal()
        t_inicio_operacion = self.env.now
        t_espera_grua = t_inicio_operacion - t_pedido_grua

        req_grua2 = yield from self._intentar_segunda_grua()
        gruas_asignadas = 2 if req_grua2 is not None else 1
        tiempo_alistamiento = 0.0
        if self.turno_actual == "nocturno" and req_grua2 is not None:
            tiempo_alistamiento = self.rng.uniform(15.0 / 60.0, 20.0 / 60.0)

        horas_nominales = self._calcular_horas_grua_nominal(
            escala.mov_dry, escala.mov_reefer, escala.mov_oog
        )
        factor_interferencia = 1.7 if gruas_asignadas == 2 else 1.0
        factor_patio = 1.25 if self.patio.level > 0.75 * self.capacidad_patio else 1.0
        tiempo_trabajo = horas_nominales / factor_interferencia * factor_patio

        tiempo_pausa_turno = 0.0
        if tiempo_alistamiento:
            tiempo_pausa_turno += yield from self._trabajar_horas_efectivas(
                tiempo_alistamiento
            )
        tiempo_pausa_turno += yield from self._trabajar_horas_efectivas(
            tiempo_trabajo
        )
        t_fin_operacion = self.env.now

        self.gruas.release(req_grua1)
        self._notificar_disponibilidad_gruas()
        if req_grua2 is not None:
            self.gruas.release(req_grua2)
            self._notificar_disponibilidad_gruas()

        # Se registra el balance simultáneo al terminar la escala: entran
        # importaciones y salen exportaciones. El retiro se aplica al balance neto
        # para no bloquear el buque entre dos movimientos que ocurren en paralelo.
        inicio_balance_patio = self.env.now
        cambio_neto_patio = mov_descarga - mov_carga
        if cambio_neto_patio > 0:
            yield self.patio.put(cambio_neto_patio)
        elif cambio_neto_patio < 0:
            yield self.patio.get(-cambio_neto_patio)
        self.stock_importacion += mov_descarga
        t_espera_patio += self.env.now - inicio_balance_patio

        yield self.env.timeout(maniobra_out)
        t_zarpada = self.env.now
        self.bermas.release(req_berma)

        tiempo_berma = t_zarpada - t_inicio_maniobra
        tiempo_total = t_zarpada - t_llegada_rada
        self.escalas_metricas.append(
            MetricasEscala(
                id_escala=escala.id_escala,
                servicio=escala.servicio,
                t_arribo=t_llegada_rada,
                t_atraque_inicio=t_inicio_maniobra,
                t_atraque_fin=t_fin_atraque,
                t_operacion_inicio=t_inicio_operacion,
                t_operacion_fin=t_fin_operacion,
                t_zarpada=t_zarpada,
                gruas_asignadas=gruas_asignadas,
                mov_descarga=mov_descarga,
                mov_carga=mov_carga,
                tiempo_espera_rada=t_espera_rada,
                tiempo_espera_grua=t_espera_grua,
                tiempo_operacion_grua=t_fin_operacion - t_inicio_operacion,
                tiempo_trabajo_efectivo=tiempo_trabajo,
                tiempo_en_berma=tiempo_berma,
                tiempo_estadia_total=tiempo_total,
                excede_16h=tiempo_total > 16.0,
                tiempo_espera_patio=t_espera_patio,
                tiempo_alistamiento_grua=tiempo_alistamiento,
                tiempo_pausa_turno=tiempo_pausa_turno,
                slots_patio_final=self.slots_ocupados,
            )
        )

    def proceso_generador_cruceros(self, inicio_horas: float, fin_horas: float):
        """Programa 24 arribos por temporada y mide por separado su ocupación."""
        intervalo = 84.0
        primer_arribo_planificado = inicio_horas + intervalo / 2.0
        id_crucero = 1

        for indice in range(24):
            t_planificado = primer_arribo_planificado + indice * intervalo
            if t_planificado >= fin_horas:
                break
            t_llegada = max(
                inicio_horas,
                t_planificado + self.rng.uniform(-3.0, 3.0),
            )

            if self.politica_crucero == "crucero_exclusivo":
                t_reserva = max(self.env.now, t_llegada - 6.0)
                if t_reserva > self.env.now:
                    yield self.env.timeout(t_reserva - self.env.now)
                req_berma = self.bermas.request(priority=-5)
                yield req_berma
                t_inicio_reserva = self.env.now
                if self.env.now < t_llegada:
                    yield self.env.timeout(t_llegada - self.env.now)
            else:
                if self.env.now < t_llegada:
                    yield self.env.timeout(t_llegada - self.env.now)
                req_berma = self.bermas.request(priority=0)
                yield req_berma
                t_inicio_reserva = self.env.now

            t_atraque = self.env.now
            duracion = self.rng.uniform(28.0, 36.0)
            yield self.env.timeout(duracion)
            self.bermas.release(req_berma)
            self.cruceros_metricas.append(
                {
                    "id_crucero": f"CRU-{id_crucero:03d}",
                    "t_arribo": t_llegada,
                    "t_inicio_reserva_berma": t_inicio_reserva,
                    "t_atraque": t_atraque,
                    "espera": max(0.0, t_atraque - t_llegada),
                    "horas_reserva_previa": max(0.0, t_llegada - t_inicio_reserva),
                    "duracion": duracion,
                    "t_zarpada": self.env.now,
                }
            )
            id_crucero += 1

    def _preparar_escalas(self) -> pd.DataFrame:
        if self.df_escalas is None:
            if not DATA_G08_CSV.exists():
                raise FileNotFoundError(f"No se encontró el histórico: {DATA_G08_CSV}")
            df = pd.read_csv(DATA_G08_CSV)
        else:
            df = self.df_escalas.copy()

        columnas = {
            "fecha_hora_arribo",
            "servicio",
            "mov_dry",
            "mov_reefer",
            "mov_oog",
        }
        faltantes = columnas - set(df.columns)
        if faltantes:
            raise ValueError(f"Faltan columnas requeridas: {sorted(faltantes)}")
        if df.empty:
            raise ValueError("El histórico de escalas está vacío.")

        df["fecha_hora_arribo"] = pd.to_datetime(
            df["fecha_hora_arribo"], errors="coerce"
        )
        if df["fecha_hora_arribo"].isna().any():
            raise ValueError("Hay fechas de arribo vacías o inválidas.")
        for columna in ("mov_dry", "mov_reefer", "mov_oog"):
            df[columna] = pd.to_numeric(df[columna], errors="coerce")
            if df[columna].isna().any() or (df[columna] < 0).any():
                raise ValueError(f"{columna} debe contener cantidades no negativas.")
            df[columna] = df[columna].astype(int)
        if "id_escala" not in df.columns:
            df["id_escala"] = [f"ESC-{i:05d}" for i in range(1, len(df) + 1)]

        df = df.sort_values("fecha_hora_arribo", kind="stable").reset_index(drop=True)
        self.fecha_inicio_sim = df["fecha_hora_arribo"].min().normalize()
        delta = (df["fecha_hora_arribo"] - self.fecha_inicio_sim).dt.total_seconds() / 3600.0
        df["horas_sim"] = delta / self.factor_demanda
        return df

    def _generar_escalas_estocasticas(
        self, df_historico: pd.DataFrame, dias_sim: float
    ) -> List[EscalaData]:
        """Remuestrea bloques semanales históricos del mismo mes calendario."""
        horas_totales = dias_sim * 24.0
        fuente = df_historico.copy()
        fuente["mes"] = fuente["fecha_hora_arribo"].dt.month
        fuente["hora_historica"] = (
            fuente["fecha_hora_arribo"] - self.fecha_inicio_sim
        ).dt.total_seconds() / 3600.0
        bloques: dict[int, list[pd.DataFrame]] = {}

        for mes, grupo_mes in fuente.groupby("mes"):
            grupo_mes = grupo_mes.sort_values("fecha_hora_arribo").reset_index(drop=True)
            bloques_mes = []
            for inicio_idx in range(len(grupo_mes)):
                t_inicio = grupo_mes.loc[inicio_idx, "hora_historica"]
                bloque = grupo_mes[
                    (grupo_mes["hora_historica"] >= t_inicio)
                    & (
                        grupo_mes["hora_historica"]
                        < t_inicio + self.TAMANO_BLOQUE_ESTOCASTICO_H
                    )
                ].copy()
                if not bloque.empty:
                    bloques_mes.append((t_inicio, bloque))
            bloques[int(mes)] = bloques_mes

        generadas: List[EscalaData] = []
        inicio_bloque_sim = 0.0
        indice = 1
        while inicio_bloque_sim < horas_totales:
            fecha_bloque = self.fecha_inicio_sim + pd.to_timedelta(
                inicio_bloque_sim, unit="h"
            )
            opciones = bloques.get(int(fecha_bloque.month), [])
            if not opciones:
                opciones = [op for sublista in bloques.values() for op in sublista]
            t_inicio_hist, bloque = opciones[self.rng.randrange(len(opciones))]

            for _, fila in bloque.iterrows():
                relativo = (fila["hora_historica"] - t_inicio_hist) / self.factor_demanda
                t_arribo = inicio_bloque_sim + float(relativo)
                if t_arribo >= horas_totales:
                    continue
                generadas.append(
                    EscalaData(
                        id_escala=f"ESC-ESTOC-{indice:05d}",
                        fecha_hora_arribo=None,
                        servicio=str(fila["servicio"]),
                        mov_dry=int(fila["mov_dry"]),
                        mov_reefer=int(fila["mov_reefer"]),
                        mov_oog=int(fila["mov_oog"]),
                        arribo_hora=t_arribo,
                    )
                )
                indice += 1

            inicio_bloque_sim += self.TAMANO_BLOQUE_ESTOCASTICO_H / self.factor_demanda

        return sorted(generadas, key=lambda escala: escala.arribo_hora)

    def _temporadas_cruceros(self, fecha_fin: pd.Timestamp):
        """Devuelve las ventanas de 12 semanas que comienzan en octubre."""
        ventanas = []
        for anio in range(self.fecha_inicio_sim.year, fecha_fin.year + 1):
            inicio = pd.Timestamp(datetime(anio, 10, 1))
            fin = inicio + pd.to_timedelta(84.0 * 24.0, unit="h")
            inicio_h = (inicio - self.fecha_inicio_sim).total_seconds() / 3600.0
            fin_h = (fin - self.fecha_inicio_sim).total_seconds() / 3600.0
            if fin_h >= 0 and inicio <= fecha_fin:
                ventanas.append((max(0.0, inicio_h), fin_h))
        return ventanas

    def run(self) -> pd.DataFrame:
        """Ejecuta una réplica y devuelve una fila de métricas por escala."""
        if self._ejecutada:
            raise RuntimeError("Cada instancia de PuertoSurSim ejecuta una sola réplica.")
        self._ejecutada = True

        df = self._preparar_escalas()
        if self.modo_generacion == "estocastico":
            lista_escalas = self._generar_escalas_estocasticas(
                df, self.duracion_estocastica_dias
            )
            fecha_fin = self.fecha_inicio_sim + pd.to_timedelta(
                self.duracion_estocastica_dias, unit="D"
            )
        else:
            lista_escalas = [
                EscalaData(
                    id_escala=str(fila["id_escala"]),
                    fecha_hora_arribo=fila["fecha_hora_arribo"],
                    servicio=str(fila["servicio"]),
                    mov_dry=int(fila["mov_dry"]),
                    mov_reefer=int(fila["mov_reefer"]),
                    mov_oog=int(fila["mov_oog"]),
                    arribo_hora=float(fila["horas_sim"]),
                )
                for _, fila in df.iterrows()
            ]
            fecha_fin = df["fecha_hora_arribo"].max()

        self.env.process(self.proceso_turnos())
        self.env.process(self.proceso_gestion_patio())

        procesos_a_completar = []
        if self.politica_crucero != "sin_crucero":
            for inicio_h, fin_h in self._temporadas_cruceros(fecha_fin):
                procesos_a_completar.append(
                    self.env.process(
                        self.proceso_generador_cruceros(inicio_h, fin_h)
                    )
                )

        for escala in lista_escalas:
            t_entrega = max(0.0, escala.arribo_hora - self.TIEMPO_MEDIO_PATIO_H)
            procesos_a_completar.append(
                self.env.process(
                    self.proceso_llegada_exportacion(escala, t_entrega)
                )
            )

        for escala in lista_escalas:
            procesos_a_completar.append(
                self.env.process(self.proceso_buque(escala))
            )

        # Completa toda la cohorte y las escalas de crucero, aunque exista una
        # cola residual después del último arribo. Los procesos de turnos y patio
        # continúan como procesos de fondo y no forman parte de este evento.
        self.env.run(until=self.env.all_of(procesos_a_completar))
        columnas = list(MetricasEscala.__dataclass_fields__)
        return pd.DataFrame(
            [metrica.__dict__ for metrica in self.escalas_metricas],
            columns=columnas,
        )
