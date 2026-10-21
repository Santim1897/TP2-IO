# Guía de Contexto y Reglas del Proyecto para Asistentes de IA (AGENTS.md)

Este documento define el contexto, especificaciones técnicas del dominio, restricciones de modelado, estándares de código y reglas de colaboración para cualquier Asistente de IA (Antigravity, Cursor, Claude Code, Copilot, etc.) que trabaje en este repositorio.

---

## 1. Identificación y Contexto Académico
* **Institución:** Instituto Tecnológico de Buenos Aires (ITBA).
* **Materia:** 11.51 - Investigación Operativa (IO51) - 2026 2° Cuatrimestre.
* **Trabajo Práctico:** TP2 - Simulación de Eventos Discretos: **"Puerto Sur"**.
* **Grupo Asignado:** **Grupo 8**.
* **Archivo de Datos Primario:** `data/PuertoSur_escalas_G08.csv` (contiene 3 años de registros históricos de escalas).
* **Documento Oficial de Pautas:** `IO51-TP2 - Puerto Sur.pdf`.

---

## 2. Descripción del Dominio y Parámetros del Sistema Portuario

### 2.1 Infraestructura y Recursos
* **Bermas de atraque:** 3 bermas disponibles para buques.
* **Grúas pórtico Ship-to-Shore (STS):** 3 grúas móviles a lo largo del muelle que pueden asignarse a cualquiera de las bermas.
* **Patio de almacenamiento:** Capacidad para **3.000 slots** de contenedores.
* **Tractores de patio:** Transportan contenedores entre el muelle y el patio.

### 2.2 Servicios y Tipos de Buque
Existen 3 servicios regulares feeder (en el dataset se identifican en la columna `servicio`):
1. `Austral Feeder`
2. `Andes Container Line`
3. `TransPatagonia Line`
* Los buques difieren en porte (cantidad total de contenedores por escala) y frecuencia de arribo.
* **Balance de carga:** Aproximadamente el 50% de los movimientos corresponde a descarga y el 50% a carga.

### 2.3 Tipos de Contenedores y Tasas de Operación de Grúa
Cada buque transporta tres tipos de contenedores (columnas `mov_dry`, `mov_reefer`, `mov_oog`):
1. **Estándar (`dry`):** Tasa nominal directa = **28 movimientos/hora** por grúa.
2. **Refrigerados (`reefer`):** Requieren conexión eléctrica y registro de temperatura. **Rendimiento se reduce un 25%** (= 21 movimientos/hora nominal). Mayor proporción en temporada de cosecha de frutas.
3. **Sobredimensionados (`oog` - Out of Gauge):** Requieren aparejos especiales y asistencia de más de un operario. Tasa reducida a **12 movimientos/hora**.

### 2.4 Maniobras y Asignación de Grúas
* **Maniobras de atraque y desatraque:** Insumen en conjunto entre **1 y 2 horas** por buque (con práctico y remolcador). Durante este tiempo, la berma está ocupada pero las grúas no operan. Al terminar la carga/descarga, se desatraca para liberar la berma.
* **Política de asignación de grúas:** Se asignan hasta **2 grúas por buque** cuando hay disponibilidad.
* **Interferencia mutua:** Cuando 2 grúas operan simultáneamente sobre la misma nave/bodega, su productividad conjunta es aproximadamente el **85%** de la suma de sus productividades individuales.

### 2.5 Turnos y Cambios de Guardia
* **Turno Diurno (08:00 – 16:00):** 3 grúas operativas con dotación completa.
* **Turno Vespertino (16:00 – 24:00):** 3 grúas operativas con dotación completa.
* **Turno Nocturno (00:00 – 08:00):** Dotación reducida: **1 grúa activa** y **1 grúa en standby** (tiempo de alistamiento para entrar en servicio: 15 a 20 minutos). Menor cantidad de tractoristas de patio (cuello de botella de transporte).
* **Cambios de turno:** Insumen entre **10 y 15 minutos**, período en el cual las grúas no operan.

### 2.6 Patio y Camiones Externos
* **Congestión del patio:** Cuando la ocupación supera el **75%** (2.250 slots), se reportan demoras frecuentes por espera de liberación de slots antes de depositar contenedores (tasa de operación de grúa afectada).
* **Permanencia en patio:** Tiempo promedio de permanencia = **72 horas** (dependiendo del tipo de carga y puntualidad de camiones).
* **Ventanas de camiones:** Entre el **20% y 30%** de los camiones llega fuera de su ventana horaria, generando colas y retrasando la liberación de slots.

### 2.7 Escenarios de Crecimiento y Decisión
* **Umbral de estadía crítico:** **16 horas promedio** en puerto (espera + servicio). Si se supera, las navieras redirigirán sus buques al puerto capital.
* **Oportunidad Temporada de Cruceros:**
  * Temporada de 3 meses (coincide con alta frutícola / reefer).
  * 2 escalas por semana.
  * Ocupación: 1 berma completa durante **28 a 36 horas**.
  * No usa grúas STS (equipos propios).
  * Arribo matutino con variabilidad de ±3 horas.
  * Ingreso estimado: **USD 60.000 por escala**.
  * Condición exigida: reserva exclusiva de una berma durante la ventana.
* **Proyecto Industrial y 4ta Berma:**
  * Escenario Base: **+35% permanente en tráfico de buques**.
  * Escenario Optimista: **+100% de demanda (duplica demanda actual)**.
  * Inversión en 4ta berma: **USD 12 millones**, vida útil 20 años.
  * Costo buque detenido: entre **USD 15.000 y USD 30.000 por día** según porte y fletamento.

---

## 3. Directivas Metodológicas y de Simulación

Cualquier agente de IA que genere o modifique código para este proyecto debe seguir rigurosamente estos principios:

1. **Simulación de Eventos Discretos (DES):**
   * El simulador se implementará en **Python** utilizando **`simpy`**.
   * Las entidades principales serán buques (`Vessel`), cruceros (`Cruise`), camiones (`Truck`) y lotes de contenedores.
   * Los recursos de SimPy serán bermas (`simpy.Resource(capacity=3)`), grúas STS (`simpy.Resource(capacity=3)` con disponibilidad dinámica según turnos), y slots de patio (`simpy.Container` o almacén con capacidad 3000).

2. **Ajuste Estadístico de Entrada (Input Modeling):**
   * No asumir distribuciones arbitrarias sin validación previa.
   * Utilizar `data/PuertoSur_escalas_G08.csv` para ajustar:
     * Tiempo entre arribos por tipo de servicio y por franja horaria / estacionalidad.
     * Distribución de la cantidad de contenedores (`dry`, `reefer`, `oog`) por servicio.
   * Realizar tests de bondad de ajuste formales: Kolmogorov-Smirnov (`scipy.stats.kstest`) y/o Chi-cuadrado.

3. **Rigor Estadístico en Salidas (Output Analysis):**
   * **Semillas reproducibles:** Todo generador pseudoaleatorio (`numpy.random`, `random`) debe aceptar un parámetro `seed`.
   * **Réplicas independientes:** Nunca concluir a partir de una única corrida. Mínimo 30 réplicas por experimento para permitir la aplicación del Teorema Central del Límite.
   * **Período de Warm-up:** Descartar el período transitorio inicial antes de recolectar estadísticas de estado estacionario.
   * **Inferencia Estadística:** Reportar siempre Media ± Intervalo de Confianza al 95%.
   * **Comparación de alternativas:** Utilizar pruebas de hipótesis estadísticas, ANOVA y test de Tukey (`statsmodels.stats.multicomp.pairwise_tukeyhsd`).
   * **Contraste con Teoría de Colas:** Contrastar el caso base con un modelo de colas analítico a priori (ej. M/M/c o M/G/c).

---

## 4. Estructura del Código

El repositorio debe mantener la siguiente organización modular:

```text
├── data/                           # Datasets históricos (G08 como principal)
├── src/
│   ├── data_analysis/              # EDA y ajuste de distribuciones empíricas
│   │   ├── __init__.py
│   │   ├── loader.py               # Carga y limpieza del CSV del Grupo 8
│   │   └── distribution_fitter.py  # Ajuste y test de bondad de ajuste
│   ├── simulation/                 # Núcleo del simulador en SimPy
│   │   ├── __init__.py
│   │   ├── config.py               # Constantes del puerto, tasas, turnos, costos
│   │   ├── entities.py             # Clases Vessel, Cruise, Truck, ContainerBatch
│   │   ├── port_system.py          # Clase principal del puerto y sus recursos SimPy
│   │   └── processes.py            # Procesos: arribo, maniobra, grúas, turnos, patio
│   └── experiments/                # Scripts para responder cada inciso del TP
│       ├── __init__.py
│       ├── runner.py               # Motor de réplicas paralelas y cálculo de IC
│       ├── scenario_base.py        # Inciso b (estadía actual y colas)
│       ├── scenario_capacity.py    # Inciso c (límite 16hs y 4ta grúa)
│       ├── scenario_patio.py       # Inciso d (ventanas de camiones y slots)
│       ├── scenario_cruises.py     # Inciso e (temporada de cruceros)
│       ├── scenario_industrial.py  # Inciso f (proyecto industrial bajo incertidumbre)
│       └── scenario_payback.py     # Inciso g (análisis de repago de 4ta berma)
├── notebooks/                      # Notebooks Jupyter para gráficos y visualización
├── docs/                           # Documentación técnica, informe y diagramas IDEF0
├── tests/                          # Tests unitarios para verificación
├── AGENTS.md                       # Este archivo
├── requirements.txt                # Dependencias del proyecto
└── README.md                       # Presentación del equipo e instrucciones de ejecución
```

---

## 5. Reglas de Trabajo Colaborativo en Git

* **Nunca commitear directamente a `main`:** Todo cambio significativo debe realizarse en una rama dedicada.
* **Convención de ramas:**
  * `feat/<nombre-funcionalidad>`: para nuevas características (ej. `feat/ajuste-arribos`, `feat/modelo-cruceros`).
  * `fix/<descripcion>`: para corrección de bugs o lógicas de simulación.
  * `docs/<seccion>`: para documentación o redacción de informe.
* **Convención de commits (Conventional Commits):**
  * `feat: ...`, `fix: ...`, `sim: ...`, `docs: ...`, `refactor: ...`, `test: ...`.
* **Pull Requests:** Antes de fusionar a `main`, al menos 1 compañero de equipo debe revisar y aprobar los cambios.
* **No subir artefactos no versionables:** No subir entornos virtuales, `.ipynb_checkpoints`, carpetas de IDE ni archivos temporales.
