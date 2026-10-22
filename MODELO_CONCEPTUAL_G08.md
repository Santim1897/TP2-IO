# TRABAJO PRÁCTICO N° 2 — INVESTIGACIÓN OPERATIVA (IO51)
## MODELO CONCEPTUAL: TERMINAL PORTUARIA "PUERTO SUR"
**Instituto Tecnológico de Buenos Aires (ITBA) — Departamento de Ingeniería Industrial**  
**Cátedra:** 11.51 / IO51 - Investigación Operativa — 2° Cuatrimestre 2026  
**Grupo:** Grupo 08  
**Dataset Oficial:** `PuertoSur_escalas_G08.csv` (8.852 escalas históricas registradas)

---

## 1. Objetivo

### 1.1. Objetivo del Sistema Portuario (Perspectiva de Negocio)
La Terminal Portuaria Puerto Sur es una empresa consorciada que compite directamente contra el puerto de la ciudad capital por la captación del tráfico marítimo regional (exportación de productos agrícolas e importación de insumos industriales). El objetivo del sistema real consiste en:
1. **Sostener el compromiso contractual de servicio:** Garantizar un tiempo de estadía promedio de buques portacontenedores feeder en puerto menor o igual a **16 horas** ($W \le 16\text{ h}$), umbral crítico establecido por las navieras regulares (*Austral Feeder*, *Andes Container Line* y *TransPatagonia Line*) a partir del cual el costo de inmovilización torna inviable la escala en Puerto Sur.
2. **Maximizar la capacidad y throughput del muelle:** Maximizar la tasa diaria de transferencia de contenedores (TEUs/día) minimizando las pérdidas económicas por buques demorados en rada.
3. **Optimizar la utilización de recursos de capital:** Evaluar racionalmente la expansión de activos fijos (flota de 3 a 4 grúas pórtico STS y de 3 a 4 bermas de atraque) garantizando un plazo de repago financiero acotado.
4. **Diversificar ingresos comerciales sin canibalizar el negocio de carga:** Analizar la viabilidad de incorporar una línea de cruceros turísticos (ingreso de USD 60.000 por escala) evaluando su costo de oportunidad sobre el negocio regular de contenedores.

### 1.2. Objetivo del Estudio de Simulación (Perspectiva Metodológica)
Formalizar, diseñar e implementar un **modelo de simulación de eventos discretos (DES)** que permita:
1. Reproducir con precisión el comportamiento estocástico y dinámico de la terminal operando bajo las condiciones históricas del Grupo 8.
2. Desglosar cuantitativamente el tiempo de estadía en sus componentes constitutivos: tiempo de espera en rada ($W_q$), tiempo de maniobras náuticas ($T_{maniobra}$) y tiempo de transferencia en berma ($T_{operacion}$).
3. Contrastar y validar los resultados empíricos contra estimaciones analíticas a priori de Teoría de Colas ($M/M/c$ y $M/G/c$).
4. Identificar la localización exacta de los cuellos de botella del sistema (grúas pórtico STS, bermas de atraque, dotaciones nocturnas reducidas y saturación del patio de almacenamiento $>75\%$).
5. Proporcionar a la dirección del consorcio evidencia cuantitativa y estadísticamente rigurosa (mediante diseño de experimentos, ANOVA e intervalos de confianza de Tukey HSD al 95%) para respaldar decisiones de inversión en infraestructura y políticas de operación comercial.

---

## 2. Variables de Decisión y de Referencia

Para formular el modelo matemático y computacional, las variables se clasifican taxativamente según su naturaleza y grado de control:

```
                                CLASIFICACIÓN FORMAL DE VARIABLES
 ┌───────────────────────────────┬───────────────────────────────┬───────────────────────────────┐
 │   VARIABLES DE DECISIÓN       │    VARIABLES EXÓGENAS / REF.  │     VARIABLES DE SALIDA / KPI │
 │   (Controlables por Dirección)│    (Estocásticas del Entorno) │     (Métricas de Desempeño)   │
 ├───────────────────────────────┼───────────────────────────────┼───────────────────────────────┤
 │ • Bermas asignadas (B: 2,3,4) │ • Arribos de buques (Delta t) │ • Estadía total (W <= 16 h)   │
 │ • Flota grúas STS (G: 3 o 4)  │ • Mix carga (Dry, Reefer, OOG)│ • Espera en rada (Wq)         │
 │ • Asignación de grúas (1 o 2) │ • Rendimientos nominales grúa │ • Tiempo en berma (Ws)        │
 │ • Régimen nocturno grúas      │ • Maniobras entrada/salida    │ • % Tiempo en espera (Wq / W) │
 │ • Ventanas y multas camiones  │ • Paradas de cambio de turno  │ • Buques en sistema (L y Lq)  │
 │ • Reserva exclusiva crucero   │ • Permanencia en patio (72h)  │ • Nivel servicio (P(W <= 16h))│
 │ • Inversión en 4ª berma       │ • Camiones tardíos (20-30%)   │ • Payback y Años-Buque ahorro │
 └───────────────────────────────┴───────────────────────────────┴───────────────────────────────┘
```

### 2.1. Variables de Decisión (Controlables por el Puerto)
* $B$: Número de bermas asignadas a buques de carga regular ($B \in \{2, 3, 4\}$).
  * $B = 3$: Configuración operativa actual.
  * $B = 2$: Cuando se cede 1 berma de forma exclusiva para la temporada de cruceros.
  * $B = 4$: Si se aprueba la inversión en la 4ª berma de atraque.
* $G$: Dotación de grúas pórtico Ship-to-Shore (STS) en el muelle ($G \in \{3, 4\}$).
* $\Pi_{gruas}$: Política de despacho y asignación de grúas a buques en berma:
  * Asignación de hasta 2 grúas por buque si hay disponibilidad en el muelle.
  * Reasignación dinámica al finalizar la operación de un buque vecino.
* $\Pi_{nocturno}$: Régimen operativo del turno nocturno (00:00–08:00):
  * Política base: 1 grúa activa + 1 en standby con tiempo de alistamiento de 15 a 20 min.
  * Política optimizada: mantener 2 grúas activas continuas con dotación completa.
* $\Pi_{camiones}$: Política de gestión de ventanas horarias de camiones externos:
  * Política actual: tolerancia abierta (20% a 30% de camiones fuera de ventana).
  * Política con penalización: aplicación de multas por impuntualidad (reduce tardíos al 10%).
  * Política de ampliación: extender la ventana horaria asignada.
* $S_{reefer}$: Política de zonificación del patio (reserva exclusiva de slots refrigerados vs. patio común).
* $Dec_{crucero} \in \{\text{Rechazar}, \text{Aceptar sin reserva de berma}, \text{Aceptar con reserva exclusiva}\}$.
* $Dec_{berma4} \in \{\text{Invertir en 4ª berma (USD 12M)}, \text{No invertir}\}$.

### 2.2. Variables de Referencia y Exógenas (No Controlables / Estocásticas)
* $t_{arr, i}$: Instante de llegada del buque feeder $i$ a la rada (extraído de `PuertoSur_escalas_G08.csv`).
* $\Delta t_i = t_{arr, i} - t_{arr, i-1}$: Tiempo entre arribos sucesivos (media = $2.968$ h, $CV = 2.494$).
* $S_i$: Servicio regular al que pertenece la escala ($S_i \in \{\text{Austral Feeder}, \text{Andes Container Line}, \text{TransPatagonia Line}\}$).
* $M_{dry, i}, M_{reefer, i}, M_{oog, i}$: Cantidad de movimientos de contenedores estándar, refrigerados y sobredimensionados por escala.
* $\mu_{dry}, \mu_{reefer}, \mu_{oog}$: Productividades nominales individuales de grúa pórtico:
  * $\mu_{dry} = 28$ movimientos/hora.
  * $\mu_{reefer} = 28 \times (1 - 0.25) = 21$ movimientos/hora.
  * $\mu_{oog} = 12$ movimientos/hora.
* $\eta$: Factor de interferencia operativa entre grúas concurrentes sobre la misma bodega ($\eta = 0.85$ de la suma de productividades; rendimiento combinado = $1.7 \times$ productividad unitaria).
* $T_{man\_in}, T_{man\_out}$: Tiempos de maniobras náuticas de practicaje y remolque ($T_{man} \sim U(1.0, 2.0)$ horas).
* $T_{cambio\_turno}$: Parada no operativa por relevo de estiba ($T_{cambio} \sim U(10, 15)$ minutos cada 8 horas, a las 00:00, 08:00 y 16:00).
* $Cap_{patio}$: Capacidad estática máxima de almacenamiento (3.000 slots).
* $T_{dwell}$: Tiempo de permanencia promedio de un contenedor en patio ($\mu = 72$ horas).
* $P_{camion\_tardio}$: Probabilidad de llegada de camión fuera de ventana horaria ($20\% \le P \le 30\%$).
* $T_{crucero}$: Duración de escala de un crucero ($T_{crucero} \sim U(28, 36)$ horas, 2 escalas/sem durante meses 10 a 12).
* Parámetros de costo:
  * Costo diario de inmovilización de buque detenido: $C_{inmov} \in [15.000, 30.000]$ USD/día.
  * Ingreso por escala de crucero: $I_{crucero} = 60.000$ USD/escala.
  * Costo de inversión de la 4ª berma: $Inv_{berma} = 12.000.000$ USD (vida útil: 20 años).

### 2.3. Variables de Salida y Desempeño (KPIs del Negocio)
* $W$: Tiempo medio de estadía total del buque en el puerto ($W = W_q + W_s$). **Meta: $W \le 16\text{ h}$**.
* $W_q$: Tiempo medio de espera en rada antes de amarrar en una berma desocupada.
* $W_s$: Tiempo medio de permanencia en berma ($W_s = T_{man\_in} + T_{operacion} + T_{man\_out}$).
* $\% Espera$: Proporción de la estadía consumida en cola de rada: $\frac{W_q}{W} \times 100\%$.
* $L, L_q$: Cantidad promedio de buques en el sistema portuario total y fondeados en rada.
* $NS_{16}$: Nivel de servicio portuario: porcentaje de buques atendidos con estadía $\le 16$ horas ($P(W \le 16\text{ h})$).
* $\rho_B, \rho_G$: Factores de utilización media de bermas y grúas pórtico.
* $P(O_{patio} > 2.250)$: Probabilidad de que la ocupación del patio supere el 75%, induciendo demoras a las grúas STS.
* $Payback$: Período de repago financiero simple de las inversiones en años.

---

## 3. Plan de Análisis y Visualización de Resultados

### 3.1. Diseño de Experimentos (DOE)
Se estructuró una matriz factorial de simulación que cubre los factores clave de decisión:

| Factor Experimental | Niveles Evaluados | Objetivo del Ensayo |
| :--- | :---: | :--- |
| **Flota de Grúas ($G$)** | 3 grúas (Base) vs. 4 grúas | Evaluar reducción de $W_q$ y cumplimiento del umbral de 16h (Consigna c). |
| **Demanda Diaria ($\lambda$)** | Barrido de factores: $0.5\times$ a $1.2\times$ de la actual | Determinar la demanda diaria máxima soportable antes de que $W > 16\text{ h}$. |
| **Política de Patio ($\Pi_{cam}$)** | Estándar (25% tardíos) vs. Penalidad (10%) vs. Ventana Amplia | Cuantificar el alivio en los slots y la eliminación del cuello de botella en grúas (Consigna d). |
| **Régimen de Cruceros** | Sin crucero vs. Con crucero libre vs. Reserva exclusiva | Medir el sobrecosto de inmovilización trasladado a buques de carga (Consigna e). |
| **Tráfico Industrial** | Actual ($1.0\times$) vs. Base ($1.35\times$) vs. Optimista ($2.0\times$) | Evaluar colapso del muelle y aplicar matrices de decisión bajo incertidumbre (Consigna f). |
| **Infraestructura Bermas ($B$)** | 3 bermas vs. 4 bermas | Calcular el período de repago de USD 12M según el ahorro de años-buque (Consigna g). |

### 3.2. Protocolo de Ejecución y Rigor Estadístico
1. **Período de Calentamiento (*Warm-up*):** Se determinó mediante el método de Welch una ventana de 100 escalas iniciales para alcanzar el régimen estacionario en la ocupación del patio y rada, descartándose de las estadísticas finales.
2. **Réplicas Independientes:** Para los barridos de sensibilidad se emplearon réplicas independientes generadas con semillas aleatorias diferenciadas.
3. **Pruebas de Hipótesis y Comparaciones Múltiples:** Se aplicó ANOVA unifactorial y el **Test de Comparaciones Múltiples de Tukey (HSD)** con nivel de significancia familiar $\text{FWER} = 0.05$ para validar si las diferencias de medias entre configuraciones son estadísticamente significativas.

### 3.3. Plan de Visualización Gráfica
Se definieron y generaron 4 figuras de alta resolución (300 DPI) para sustentar el reporte gerencial:
* **Figura 1 (`fig1_capacidad_demanda.png`):** Curva paramétrica de estadía $W$ y nivel de servicio vs. demanda diaria (buques/día) para 3 y 4 grúas.
* **Figura 2 (`fig2_desglose_estadia.png`):** Gráfico de barras apiladas comparando el tiempo en berma ($W_s$) vs. espera en rada ($W_q$).
* **Figura 3 (`fig3_repago_berma.png`):** Curva de período de repago (meses) de la 4ª berma en función del costo diario de inmovilización.
* **Figura 4 (`fig4_tukey_hsd.png`):** Gráfico de intervalos de confianza al 95% para las diferencias de medias del Test de Tukey HSD.

---

## 4. Relación entre Variables (Diagrama de Influencias Causal)

El sistema portuario opera como una red estocástica altamente acoplada. A continuación se presenta el **Diagrama Causal de Influencias y Bucles de Retroalimentación**:

![Diagrama Causal de Relación entre Variables](file:///C:/Users/ASUS/.gemini/antigravity/scratch/TP2-IO/plots/fig_relacion_variables_causal.png)

### Bucles de Retroalimentación y Mecanismos de Fricción:
1. **Bucle de Muelle (Congestión en Rada):**
   * Un aumento en la demanda de arribos ($\lambda$) incrementa los buques en rada ($L_q$), lo que eleva el tiempo de espera ($W_q$) y la estadía total ($W$).
   * Al agregar una 4ª grúa ($G = 4$), los buques se despachan más rápido, disminuyendo el tiempo en berma ($W_s$), lo cual libera las bermas con mayor celeridad y corta la acumulación de buques en rada.
2. **Bucle de Patio (Efecto Cuello de Botella Secundario):**
   * Cada buque que descarga transfiere contenedores al patio de 3.000 slots. Si los camiones externos arriban fuera de ventana (20% a 30% tardíos), los contenedores se acumulan prolongando el tiempo medio de estadía en tierra ($T_{dwell} \approx 72\text{ h}$).
   * Si la ocupación del patio supera el 75% ($>2.250$ slots), las grúas STS no pueden depositar contenedores de manera fluida y deben esperar la liberación de slots. Esto reduce su productividad efectiva, incrementa $W_s$, bloquea la berma y realimenta la cola de rada $W_q$.
3. **Bucle de Restricción Nocturna:**
   * La reducción a 1 grúa activa (+ 1 en standby con 15–20 min de alistamiento) de 00:00 a 08:00 reduce la capacidad de descarga a un tercio de su régimen diurno, provocando que los buques que operan durante la noche retengan la berma hasta la mañana siguiente, generando picos de congestión matutina en rada.
4. **Bucle de Reserva de Cruceros:**
   * Conceder reserva exclusiva a un crucero durante 28 a 36 horas reduce la capacidad de atraque comercial de 3 a 2 bermas, provocando un estrangulamiento inmediato que transfiere demoras masivas a la flota de buques de carga.

---

## 5. Diagramas IDEF0

La estructura funcional de los procesos de la terminal se formalizó siguiendo la metodología estándar **IDEF0 (Integration Definition for Function Modeling)**:

### 5.1. Diagrama de Contexto A-0
Representa la función global del sistema, sus Entradas (Inputs), Controles (Controls), Mecanismos (Mechanisms) y Salidas (Outputs):

![Diagrama IDEF0 A-0 Contexto](file:///C:/Users/ASUS/.gemini/antigravity/scratch/TP2-IO/plots/fig_idef0_a_menos_0.png)

* **Entradas (I):** Buques portacontenedores feeder en rada (G08), carga de importación/exportación (Dry, Reefer, OOG), camiones externos de retiro y arribos de cruceros.
* **Controles (C):** Umbral contractual de navieras ($W \le 16\text{ h}$), régimen de turnos de estiba (8h) con paradas de 10-15 min, capacidad física de patio (3.000 slots) y políticas de ventanas de camiones.
* **Mecanismos (M):** 3 Bermas de atraque (o 4), flota de 3 grúas pórtico STS (o 4), tractoristas y playa de contenedores, prácticos y remolcadores, y el simulador en SimPy.
* **Salidas (O):** Buques atendidos y despachados, métricas de estadía ($W, W_q, W_s$), nivel de servicio contractual ($P(W \le 16\text{ h})$), utilización de activos e indemnizaciones por buques inmovilizados.

### 5.2. Descomposición de Primer Nivel A0
Descompone la terminal en sus cuatro actividades operativas secuenciales:

![Diagrama IDEF0 A0 Descomposición](file:///C:/Users/ASUS/.gemini/antigravity/scratch/TP2-IO/plots/fig_idef0_a0_descomposicion.png)

* **A1: Recepción y Fondeo en Rada:** Los buques arriban con tasa $\lambda = 8.09$ b/d. Si todas las bermas están ocupadas (o reservadas para crucero), aguardan en cola bajo disciplina FIFO acumulando tiempo de espera $W_q$.
* **A2: Maniobra de Entrada y Atraque:** Al liberarse una berma, se asigna práctico y remolcador. Insume entre 1 y 2 horas ($U(1, 2)$ h). Durante este lapso la berma pasa a estar ocupada, pero las grúas pórtico no pueden operar.
* **A3: Operación de Grúas y Gestión de Patio:** El buque amarrado solicita hasta 2 grúas disponibles. Las grúas operan a tasas específicas según el mix de carga (dry, reefer, OOG), afectadas por interferencia combinada (85%), cambio de turnos y dotaciones nocturnas. Si la ocupación del patio supera el 75%, se induce una penalidad de espera por slot.
* **A4: Desatraque y Salida:** Finalizada la transferencia de carga, se solicita práctico y remolcador para desamarrar y salir a mar abierto ($U(1, 2)$ h). Al concluir, la berma queda formalmente libre para el siguiente buque en cola.

---

## 6. Lógicas Operativas del Sistema

A continuación se ilustra el **Diagrama de Flujo Lógico Operativo** que rige el ciclo de vida de cada buque:

![Diagrama de Flujo Lógico Operativo](file:///C:/Users/ASUS/.gemini/antigravity/scratch/TP2-IO/plots/fig_logica_flujo_buque.png)

### Detalle de las Lógicas Algorítmicas:

#### Lógica 1: Arribo y Asignación de Berma
```text
ALGORITMO Asignar_Berma(Buque):
    Encolar Buque en Cola_Rada (disciplina FIFO)
    SI (Bermas_Ocupadas < B_total) Y NO (Berma_Reservada_Crucero):
        Desencolar Buque
        Asignar Berma
        Iniciar Maniobra_Atraque
    SINO:
        Buque permanece fondeado acumulando Wq
```

#### Lógica 2: Maniobra Náutica de Entrada
```text
DURACIÓN: T_atraque = Uniforme(1.0, 2.0) horas
ESTADO: Berma = OCUPADA
RECURSOS STS: INACTIVOS (las grúas no pueden posicionarse sobre la bodega durante la maniobra)
```

#### Lógica 3: Asignación y Operación de Grúas STS
```text
CÁLCULO DE TIEMPO BASE DE CARGA (1 Grúa Individual):
    H_nominal = (mov_dry / 28) + (mov_reefer / 21) + (mov_oog / 12)

DETERMINACIÓN DE GRÚAS ASIGNADAS:
    SI Grúas_Libres >= 2 EN Muelle:
        Gruas_Asignadas = 2
        Factor_Velocidad = 1.70  # (0.85 * (1 + 1))
        SI Turno_Actual == "Nocturno":
            Demora_Alistamiento = Uniforme(15/60, 20/60) horas  # Standby
    SINO:
        Gruas_Asignadas = 1
        Factor_Velocidad = 1.00

FACTOR DE CONGESTIÓN DE PATIO:
    SI Slots_Ocupados > 2.250:  # (>75% capacidad)
        Factor_Patio = 1.25     # Demora adicional de 25% por falta de espacio
    SINO:
        Factor_Patio = 1.00

TIEMPO DE OPERACIÓN EFECTIVO:
    T_op = (H_nominal / Factor_Velocidad) * Factor_Patio + Demora_Alistamiento
    # Si ocurre un cambio de turno durante T_op, se añade pausa de Uniforme(10/60, 15/60) h
```

#### Lógica 4: Ciclo de Turnos y Paradas de Guardia
```text
RELOJ CÍCLICO DE 8 HORAS:
    08:00 - 16:00 (Diurno): 3 Grúas activas al 100%
    16:00: Parada de cambio de turno: Uniforme(10, 15) minutos (Grúas detenidas)
    16:00 - 24:00 (Vespertino): 3 Grúas activas al 100%
    00:00: Parada de cambio de turno: Uniforme(10, 15) minutos
    00:00 - 08:00 (Nocturno): 1 Grúa activa + 1 en standby (15-20 min alistamiento)
    08:00: Parada de cambio de turno: Uniforme(10, 15) minutos
```

#### Lógica 5: Dinámica de Patio y Camiones Externos
```text
INGRESO: Por cada escala finalizada, Contenedores_Ingreso = 0.5 * Total_Movimientos
RETIRO: Modelo estocástico con tasa de salida lambda_retiro = Slots_Ocupados / 72 h
        Modulado por factor de puntualidad:
        - Estándar (25% tardíos): Eficiencia = 0.95
        - Con Penalidad (10% tardíos): Eficiencia = 0.98
BALANCE: Slots_Ocupados(t) = min(3.000, max(0, Slots(t-1) + Ingresos - Retiros))
```

#### Lógica 6: Cruceros y Reserva Exclusiva
```text
TEMPORADA ALTA: Meses 10, 11 y 12 (2 escalas semanales = 24 cruceros)
VENTANA: Arribo matutino +- 3 horas | Permanencia: Uniforme(28, 36) horas
REGLA DE EXCLUSIVIDAD: Si rige exclusividad, se bloquea 1 berma comercial impidiendo el atraque de buques de carga durante la ventana del crucero
GRÚAS PÓRTICO: 0 (No utiliza equipos de muelle; opera con medios propios)
```

#### Lógica 7: Desatraque y Salida
```text
DURACIÓN: T_desatraque = Uniforme(1.0, 2.0) horas
AL FINALIZAR: Se libera formalmente la berma y se registra W_total = t_zarpada - t_arribo
```

---

## 7. Elementos del Simulador (Arquitectura SimPy)

El simulador computacional se construyó en Python utilizando la librería de eventos discretos **SimPy**. La siguiente figura ilustra la arquitectura de clases, recursos y monitores:

![Arquitectura de Componentes del Simulador SimPy](file:///C:/Users/ASUS/.gemini/antigravity/scratch/TP2-IO/plots/fig_elementos_simulador.png)

### 7.1. Entidades (Processes de SimPy)
* `proceso_buque(env, escala, recursos, monitor)`: Modela el ciclo de vida de cada buque feeder (arribo, espera en rada, maniobra de entrada, amarre, despacho de grúas, transferencia y maniobra de salida).
* `proceso_crucero(env, inicio, fin, recursos)`: Modela la ocupación periódica y prolongada de una berma durante la temporada de cruceros.
* `proceso_turnos(env, recursos)`: Proceso demonio cíclico que controla el temporizador de 8 horas, ejecuta las pausas de cambio de turno y conmuta las grúas diurnas vs. nocturnas.
* `proceso_gestion_patio(env, recursos)`: Proceso demonio que actualiza de manera horaria el inventario de slots del patio y modela la extracción estocástica de contenedores por camiones externos.

### 7.2. Recursos del Entorno (`simpy.Environment`)
* `bermas = simpy.Resource(env, capacity=B)`: Modela las bermas físicas del muelle ($B = 3$ o $B = 4$). Cola con disciplina First-In, First-Out (FIFO).
* `gruas_totales_disponibles`: Variable entera dinámica controlada por `proceso_turnos` para regular el número de grúas pórtico que pueden operar concurrentemente en el muelle.
* `patio_slots = simpy.Container(env, capacity=3000, init=1200)`: Almacena el número instantáneo de contenedores depositados, activando alertas al rebasar los 2.250 slots ($75\%$).

### 7.3. Monitor Estadístico y Variables de Estado
* Registrador individual por buque que captura:
  * `t_arribo`: Instante de llegada a rada.
  * `t_atraque_inicio`: Inicio de maniobra náutica de entrada.
  * `t_atraque_fin`: Fin de atraque e inicio de operación de grúas.
  * `t_operacion_fin`: Fin de faena de carga/descarga e inicio de desatraque.
  * `t_zarpada`: Salida a mar abierto.
* Cálculo vectorizado de métricas:
  $$W_q = t_{atraque\_inicio} - t_{arribo}$$
  $$W_s = t_{zarpada} - t_{atraque\_inicio}$$
  $$W = t_{zarpada} - t_{arribo} = W_q + W_s$$
  $$\text{Indicador Binario } (W > 16\text{ h})$$
* Validación cruzada automatizada de la **Ley de Little** ($L = \lambda W$) y exportación a formatos tabulares para análisis de varianza (ANOVA) y comparaciones múltiples de Tukey HSD.
