# TRABAJO PRÁCTICO N° 2 — INVESTIGACIÓN OPERATIVA (IO51)
## MODELO CONCEPTUAL: TERMINAL PORTUARIA "PUERTO SUR"
**Instituto Tecnológico de Buenos Aires (ITBA) — Departamento de Ingeniería Industrial**  
**Cátedra:** 11.51 / IO51 - Investigación Operativa — 2° Cuatrimestre 2026  
**Grupo:** Grupo 08  
**Dataset Oficial:** `data/PuertoSur_escalas_G08.csv` (8.852 escalas históricas registradas)

---

## 1. Objetivo

### 1.1. Objetivo del Sistema Portuario (Perspectiva de Negocio)
La Terminal Portuaria Puerto Sur es una empresa concesionada que compite con el puerto de la ciudad capital por la captación del tráfico marítimo de la región patagónica (exportación de productos agrícolas e importación de insumos industriales). El objetivo del sistema real consiste en:
1. **Sostener el compromiso contractual de servicio:** Garantizar un tiempo de estadía promedio de buques portacontenedores feeder en puerto menor o igual a **16 horas** ($W \le 16\text{ h}$), umbral crítico establecido por las navieras regulares (*Austral Feeder*, *Andes Container Line* y *TransPatagonia Line*) a partir del cual el costo de inmovilización torna inviable la escala en Puerto Sur.
2. **Maximizar la capacidad y throughput del muelle:** Maximizar la tasa diaria de transferencia de contenedores minimizando las pérdidas económicas por buques demorados en rada.
3. **Optimizar la utilización de recursos de capital:** Evaluar racionalmente la expansión de activos fijos (flota de 3 a 4 grúas pórtico STS y de 3 a 4 bermas de atraque) garantizando un plazo de repago financiero acotado.
4. **Diversificar ingresos comerciales sin canibalizar el negocio de carga:** Analizar la viabilidad de incorporar una línea de cruceros turísticos (ingreso de USD 60.000 por escala) evaluando su costo de oportunidad sobre el negocio regular de contenedores.

### 1.2. Objetivo del Estudio de Simulación (Perspectiva Metodológica)
Formalizar, diseñar e implementar un **modelo de simulación de eventos discretos (DES)** que permita:
1. Reproducir con fidelidad el comportamiento estocástico y dinámico de la terminal operando bajo las condiciones históricas del Grupo 8.
2. Desglosar cuantitativamente el tiempo de estadía en sus componentes constitutivos reales: tiempo de espera en rada ($W_q$), tiempo de maniobras náuticas conjuntas de practicaje y remolque ($T_{maniobra} \sim U(1, 2)$ h en total), tiempo de espera amarrado por grúa libre ($T_{esp\_grua}$) y tiempo de transferencia efectiva de carga ($T_{op\_grua}$).
3. Contrastar y validar los resultados empíricos contra estimaciones analíticas a priori de Teoría de Colas ($M/M/c$ y $M/G/c$).
4. Identificar la localización exacta de los cuellos de botella del sistema (grúas pórtico STS, bermas de atraque, dotaciones nocturnas reducidas y saturación del patio de almacenamiento $>75\%$).
5. Proporcionar a la dirección del consorcio evidencia cuantitativa y estadísticamente rigurosa (mediante diseño de experimentos, ANOVA e intervalos de confianza de Tukey HSD al 95%) para respaldar decisiones de inversión en infraestructura y políticas de operación comercial.

### 1.3. Alcance y Supuestos Simplificatorios del Modelo
Conforme a la metodología formal de modelado conceptual de la cátedra (orientada a responder sistemáticamente a *¿Qué? ¿Por qué? ¿Dónde? ¿Cuándo? ¿Quién? ¿Cuánto?* - Diapositivas 4 y 21 de `IO51_Teoria_Modelo_Conceptual_Simulacion.pdf`):
* **¿Qué? (Objeto de modelado):** Operación integral del muelle y frente de atraque, asignación dinámica de grúas pórtico STS, patio de almacenamiento de contenedores y maniobras náuticas de prácticos y remolcadores.
* **¿Por qué? (Propósito):** Diagnosticar los cuellos de botella que amenazan el umbral contractual de 16 horas de estadía promedio ($W \le 16\text{ h}$) y fundamentar cuantitativamente decisiones estratégicas de expansión física (4ª berma, 4ª grúa, políticas de camiones y cruceros).
* **¿Dónde? (Límites espaciales):** Desde el área de fondeo en rada exterior hasta el muelle de transferencia y la puerta de salida terrestre de camiones externos (*terminal gate*).
* **¿Cuándo? (Horizonte temporal):** Simulación continua de 3 años de operación (correspondiente al horizonte muestral del Grupo 8 con 8.852 escalas), considerando variaciones estacionales (cosecha frutícola) y ciclos diarios de 3 turnos de 8 horas.
* **¿Quién? (Actores e interacciones):** Buques portacontenedores feeder de 3 servicios regulares, buques de crucero turístico, camiones de transporte terrestre, prácticos náuticos y operarios de estiba.
* **¿Cuánto? (Nivel de detalle):** Modelado discreto a nivel de escala individual de buque, grúa pórtico y slot de patio, agregando el movimiento de contenedores por tipo (Dry, Reefer, OOG).

**Supuestos Simplificatorios Fundamentales:**
1. **Maniobras Náuticas:** Práctico y remolcador tienen disponibilidad suficiente para atender a los buques ni bien se libera una berma; la duración combinada de atraque y desatraque es de 1 a 2 horas en total ($T_{maniobra\_total} \sim U(1.0, 2.0)$ h, con media de 1.5h total por buque).
2. **Asignación de Grúas:** Se asigna un máximo de 2 grúas por buque cuando hay disponibilidad en el muelle. Dos grúas concurrentes operan con una interferencia mutua que reduce su productividad combinada al 85% de la suma directa (factor $1.70\times$).
3. **Balance de Masa en Patio:** Cada escala transfiere al patio contenedores de importación (descarga) y retira contenedores de exportación (carga) en proporción balanceada (aproximadamente 50% descarga y 50% carga).
4. **Permanencia en Patio:** El tiempo medio de permanencia de los contenedores en el patio es de 72 horas, modulado por la puntualidad de llegada de los camiones externos (20% a 30% fuera de ventana horaria).
5. **Condiciones Meteorológicas:** No se contemplan cierres hidrometeorológicos extraordinarios de puerto, asumiéndose operatividad continua los 365 días del año.

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
 │ • Régimen nocturno grúas      │ • Maniobras conjuntas (1-2h)  │ • % Espera inactiva vs Atenc. │
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
* $t_{arr, i}$: Instante de llegada del buque feeder $i$ a la rada (extraído de `data/PuertoSur_escalas_G08.csv`).
* $\Delta t_i = t_{arr, i} - t_{arr, i-1}$: Tiempo entre arribos sucesivos (media = $2.968$ h, $CV = 2.494$, ajustado paramétricamente en `data/distribuciones_g08.json`).
* $S_i$: Servicio regular al que pertenece la escala ($S_i \in \{\text{Austral Feeder}, \text{Andes Container Line}, \text{TransPatagonia Line}\}$).
* $M_{dry, i}, M_{reefer, i}, M_{oog, i}$: Cantidad de movimientos de contenedores estándar, refrigerados y sobredimensionados por escala.
* $\mu_{dry}, \mu_{reefer}, \mu_{oog}$: Productividades nominales individuales de grúa pórtico:
  * $\mu_{dry} = 28$ movimientos/hora.
  * $\mu_{reefer} = 28 \times (1 - 0.25) = 21$ movimientos/hora.
  * $\mu_{oog} = 12$ movimientos/hora.
* $\eta$: Factor de interferencia operativa entre grúas concurrentes sobre la misma bodega ($\eta = 0.85$ de la suma de productividades; rendimiento combinado = $1.7 \times$ productividad unitaria).
* $T_{maniobra}$: Tiempo conjunto de practicaje y remolque para atraque y desatraque: **entre 1 y 2 horas en total por buque** ($T_{maniobra} \sim U(1.0, 2.0)$ h en conjunto, media $1.5$ h total). Durante ese lapso la berma está ocupada pero las grúas no operan.
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
* $W_s$: Tiempo medio de permanencia en berma ($W_s = T_{man\_in} + T_{esp\_grua} + T_{op\_grua} + T_{man\_out}$).
* $T_{esp\_grua}$: Tiempo que el buque permanece amarrado en berma esperando que se libere una grúa STS.
* $T_{op\_grua}$: Tiempo de atención efectiva de transferencia de carga con grúas STS activas.
* $\% Espera$: Proporción de tiempo que el buque espera inactivo (en rada y esperando grúa amarrado) respecto a la estadía total: $\frac{W_q + T_{esp\_grua}}{W} \times 100\%$.
* $L, L_q$: Cantidad promedio de buques en el sistema portuario total y fondeados en rada.
* $NS_{16}$: Nivel de servicio portuario: porcentaje de buques atendidos con estadía $\le 16$ horas ($P(W \le 16\text{ h})$).
* $\rho_B, \rho_G$: Factores de utilización media de bermas y grúas pórtico.
* $P(O_{patio} > 2.250)$: Probabilidad de que la ocupación del patio supere el 75%, induciendo demoras a las grúas STS.
* $Payback$: Período de repago financiero simple de las inversiones en años.

### 2.4. Modelo de Datos Cuantificado (Parámetros Empíricos G08)
Siguiendo el estándar de especificación formal de datos de la cátedra (Diapositiva 19 de `IO51_Teoria_Simulacion_Modelo_de_Datos_Ajuste.pdf`):

| Variable | Descripción | U.M. | Valor Base / Rango | Relación / Expresión | Característica (Tipo y Parámetros) |
| :--- | :--- | :---: | :---: | :---: | :--- |
| $\lambda$ | Tasa de arribo de buques feeder | buques/día | 8.09 b/d | Histórico `PuertoSur_escalas_G08.csv` | Poisson no homogéneo ($\Delta t \sim \text{Exp}(\mu=2.97\text{h})$) |
| $Mix$ | Composición de carga por buque | % mov | 55% Dry, 35% Reefer, 10% OOG | Registros empíricos de 8.852 escalas | Distribución empírica por servicio |
| $\mu_{dry}$ | Rendimiento nominal grúa contenedor Dry | mov/hora | 28 | Tasa directa de diseño | Constante determinística |
| $\mu_{reefer}$ | Rendimiento grúa contenedor Reefer | mov/hora | 21 | $\mu_{dry} \times 0.75$ (-25% por conexión eléctrica) | Constante determinística |
| $\mu_{oog}$ | Rendimiento grúa contenedor OOG | mov/hora | 12 | Aparejos especiales y operarios extra | Constante determinística |
| $\eta$ | Factor de interferencia por doble grúa | factor | 0.85 | Productividad combinada = $1.70 \times \mu_i$ | Constante determinística |
| $T_{maniobra}$ | Maniobras náuticas (atraque + desatraque) | horas | [1.0, 2.0] | Insumen en conjunto entre 1 y 2 horas | Aleatoria $U(1.0, 2.0)$ h ($\mu=1.5\text{ h}$) |
| $T_{cambio}$ | Paradas por cambio de turno (3 por día) | minutos | [10, 15] | Ocurren a las 00:00, 08:00 y 16:00 | Aleatoria $U(10, 15)$ min |
| $G_{noc}$ | Grúas activas en turno nocturno | grúas | 1 activa + 1 standby | Standby demora 15 a 20 min alistamiento | $1 + U(15/60, 20/60)\text{ h}$ de demora |
| $Cap_{patio}$ | Capacidad estática del patio | slots | 3.000 | Capacidad física instalada | Límite determinístico |
| $T_{dwell}$ | Tiempo de permanencia en patio | horas | 72 | Tiempo medio de almacenaje en tierra | Exponencial ($\mu=72\text{ h}$) |
| $P_{tardio}$ | Proporción camiones fuera de ventana | % | 20% a 30% | Factor de puntualidad de transporte | Aleatoria $U(0.20, 0.30)$ |
| $T_{crucero}$ | Duración de escala de crucero | horas | [28, 36] | 2 escalas semanales (meses 10 a 12) | Aleatoria $U(28, 36)$ h |
| $C_{inmov}$ | Costo buque detenido en rada/puerto | USD/día | 15.000 - 30.000 | Según porte y fletamento de naviera | Parámetro de sensibilidad |
| $Inv_{B4}$ | Inversión en 4ª berma de atraque | USD | 12.000.000 | Vida útil proyectada: 20 años | Inversión de capital fija |

---

## 3. Plan de Análisis y Visualización de Resultados

### 3.1. Diseño de Experimentos (DOE)
Se estructuró una matriz factorial de simulación que cubre los factores clave de decisión:

| Factor Experimental | Niveles Evaluados | Objetivo del Ensayo |
| :--- | :---: | :--- |
| **Flota de Grúas ($G$)** | 3 grúas (Base) vs. 4 grúas | Evaluar reducción de $W_q$ y cumplimiento del umbral de 16h (Consigna c). |
| **Demanda Diaria ($\lambda$)** | Barrido de factores: $0.5\times$ a $1.2\times$ de la actual | Determinar la demanda diaria máxima soportable antes de que $W > 16\text{ h}$. |
| **Política de Patio ($\Pi_{cam}$)** | Estándar (25% tardíos) vs. Penalidad (10%) vs. Ventana Amplia | Cuantificar el alivio en los slots y la eliminación del cuello de botella en grúas (Consigna d). |
| **Régimen de Cruceros** | Sin crucero vs. Con crucero libre vs. Reserva preventiva exclusiva | Medir el sobrecosto de inmovilización trasladado a buques de carga (Consigna e). |
| **Tráfico Industrial** | Actual ($1.0\times$) vs. Base ($1.35\times$) vs. Optimista ($2.0\times$) | Evaluar saturación del muelle y aplicar matrices de decisión bajo incertidumbre (Consigna f). |
| **Infraestructura Bermas ($B$)** | 3 bermas vs. 4 bermas | Calcular el período de repago de USD 12M según el ahorro de años-buque (Consigna g). |

### 3.2. Plan de Cuadros y Matriz de Resultados
Conforme al estándar formal de la cátedra (Diapositiva 15 de `IO51_Teoria_Modelo_Conceptual_Simulacion.pdf`), el **Plan de Cuadros** define la estructura tabular con la que se reportarán y contrastarán los resultados de simulación, especificando las variables de decisión (control) y las variables de referencia con sus respectivos intervalos de confianza al 95%:

| Escenario Evaluado | Variables de Decisión ($B, G, \Pi_{cam}, \Pi_{noc}$) | $W$ [h] (Media $\pm \text{IC}_{95\%}$) | $W_q$ [h] (Espera en Rada) | $W_s$ [h] (Tiempo en Berma) | Nivel de Servicio $P(W \le 16\text{h})$ | Ocupación Bermas ($\rho_B$) | Ocupación Grúas ($\rho_G$) | Decisión / Conclusión |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Escenario Base (Inciso b)** | $B=3, G=3, \Pi_{std}, 1G_{noc}$ | $W_{base} \pm \Delta W$ | $W_{q, base}$ | $W_{s, base}$ | $NS_{base}$ | $\rho_{B, base}$ | $\rho_{G, base}$ | Diagnóstico de situación actual |
| **Escenario Capacidad (Inciso c)** | $B=3, G=4$ vs. $\lambda$ barrido | $W_{cap} \pm \Delta W$ | $W_{cap}$ | $W_{s, cap}$ | $NS_{cap}$ | $\rho_{B, cap}$ | $\rho_{G, cap}$ | Límite máx. buques/día con $W \le 16\text{h}$ |
| **Escenario Patio (Inciso d)** | $\Pi_{cam} \in \{\text{Multa}, \text{Ventana}\}$ | $W_{pat} \pm \Delta W$ | $W_{q, pat}$ | $W_{s, pat}$ | $NS_{pat}$ | $\rho_{B, pat}$ | $\rho_{G, pat}$ | Descongestión patio $<75\%$ |
| **Escenario Cruceros (Inciso e)** | Cede 1 Berma ($B=2$ p/carga) | $W_{cruc} \pm \Delta W$ | $W_{q, cruc}$ | $W_{s, cruc}$ | $NS_{cruc}$ | $\rho_{B, cruc}$ | $\rho_{G, cruc}$ | Impacto inmovilización vs. USD 60k |
| **Escenario Industrial (Inciso f)** | $\lambda +35\%$ (Base) y $+100\%$ (Opt) | $W_{ind} \pm \Delta W$ | $W_{q, ind}$ | $W_{s, ind}$ | $NS_{ind}$ | $\rho_{B, ind}$ | $\rho_{G, ind}$ | Matrices bajo incertidumbre |
| **Escenario Payback (Inciso g)** | Expansión a 4ª Berma ($B=4$) | $W_{inv} \pm \Delta W$ | $W_{q, inv}$ | $W_{s, inv}$ | $NS_{inv}$ | $\rho_{B, inv}$ | $\rho_{G, inv}$ | Período de repago de USD 12M |

### 3.3. Protocolo de Ejecución y Rigor Estadístico
1. **Período de Calentamiento (*Warm-up*):** Ventana de estabilización inicial para alcanzar régimen permanente en inventario de patio y colas de rada.
2. **Réplicas Independientes:** Se emplearon réplicas independientes generadas con semillas aleatorias diferenciadas para los barridos de sensibilidad.
3. **Pruebas de Hipótesis y Comparaciones Múltiples:** Se aplicó ANOVA unifactorial y el **Test de Comparaciones Múltiples de Tukey (HSD)** con nivel de significancia familiar $\text{FWER} = 0.05$ para validar si las diferencias de medias entre configuraciones son estadísticamente significativas.

### 3.4. Plan de Visualización Gráfica
Se definieron y generaron figuras analíticas integradas:
* **Figura 1 (`plots/fig1_capacidad_demanda.png`):** Curva paramétrica de estadía $W$ y nivel de servicio vs. demanda diaria (buques/día) para 3 y 4 grúas.
* **Figura 2 (`plots/fig2_desglose_estadia.png`):** Gráfico de barras apiladas comparando el tiempo en berma ($W_s$) vs. espera en rada ($W_q$).
* **Figura 3 (`plots/fig3_repago_berma.png`):** Curva de período de repago (meses) de la 4ª berma en función del costo diario de inmovilización.
* **Figura 4 (`plots/fig4_tukey_hsd.png`):** Gráfico de intervalos de confianza al 95% para las diferencias de medias del Test de Tukey HSD.

---

## 4. Relación entre Variables (Diagrama de Influencias Causal)

El sistema portuario opera como una red estocástica altamente acoplada. A continuación se presenta el **Diagrama Causal de Influencias y Bucles de Retroalimentación**:

![Diagrama Causal de Relación entre Variables](plots/fig_relacion_variables_causal.png)

### Bucles de Retroalimentación y Mecanismos de Fricción:
1. **Bucle de Muelle (Congestión en Rada):**
   * Un aumento en la demanda de arribos ($\lambda$) incrementa los buques en rada ($L_q$), lo que eleva el tiempo de espera ($W_q$) y la estadía total ($W$).
   * Al agregar una 4ª grúa ($G = 4$), los buques se atienden más rápido, disminuyendo el tiempo en berma ($W_s$), lo cual libera las bermas con mayor celeridad y contrae la acumulación en rada.
2. **Bucle de Contención de Grúas en Berma:**
   * Si las 3 bermas están ocupadas pero solo hay 3 grúas disponibles (o 1+1 de noche), un buque amarrado puede tener que esperar inactivo hasta que un buque vecino libere grúas. Esto genera $T_{esp\_grua} > 0$.
3. **Bucle de Patio (Efecto Cuello de Botella Secundario):**
   * Cada buque que descarga transfiere contenedores al patio de 3.000 slots. Si los camiones externos arriban fuera de ventana (20% a 30% tardíos), los contenedores se acumulan prolongando el tiempo medio de permanencia ($T_{dwell} \approx 72\text{ h}$).
   * Si la ocupación del patio supera el 75% ($>2.250$ slots), las grúas STS sufren demoras esperando la liberación de slots. Esto reduce su productividad efectiva, incrementa $W_s$, bloquea la berma y realimenta la cola de rada $W_q$.
4. **Bucle de Restricción Nocturna:**
   * La reducción a 1 grúa activa (+ 1 en standby con 15–20 min de alistamiento) de 00:00 a 08:00 reduce la capacidad de descarga a un tercio de su régimen diurno, reteniendo los buques amarrados hasta la mañana siguiente y generando picos de congestión matutina en rada.
5. **Bucle de Reserva Preventiva de Cruceros:**
   * Conceder reserva exclusiva a un crucero durante 28 a 36 horas exige bloquear preventivamente 1 berma para que esté vacía cuando arribe el crucero, reduciendo la capacidad de atraque comercial de 3 a 2 bermas y transfiriendo demoras a los buques feeder.

---

## 5. Diagramas IDEF0

La estructura funcional de los procesos de la terminal se formalizó siguiendo la metodología estándar **IDEF0 (Integration Definition for Function Modeling)**:

### 5.1. Diagrama de Contexto A-0
Representa la función global del sistema, sus Entradas (Inputs), Controles (Controls), Mecanismos (Mechanisms) y Salidas (Outputs):

![Diagrama IDEF0 A-0 Contexto](plots/fig_idef0_a_menos_0.png)

* **Entradas (I):** Buques portacontenedores feeder en rada (G08), carga de importación/exportación (Dry, Reefer, OOG), camiones externos de retiro y arribos de cruceros.
* **Controles (C):** Umbral contractual de navieras ($W \le 16\text{ h}$), régimen de turnos de estiba (8h) con paradas de 10-15 min, capacidad física de patio (3.000 slots) y ventanas horarias de camiones.
* **Mecanismos (M):** 3 Bermas de atraque (o 4), flota de 3 grúas pórtico STS (o 4), tractoristas y playa de contenedores, prácticos y remolcadores, y el simulador en SimPy.
* **Salidas (O):** Buques atendidos y despachados, métricas de estadía ($W, W_q, W_s$), desglose de espera inactiva vs. atención efectiva, nivel de servicio contractual ($P(W \le 16\text{ h})$), utilización de activos e indemnizaciones por buques inmovilizados.

### 5.2. Descomposición de Primer Nivel A0
Descompone la terminal en sus cuatro actividades operativas secuenciales:

![Diagrama IDEF0 A0 Descomposición](plots/fig_idef0_a0_descomposicion.png)

* **A1: Recepción y Fondeo en Rada:** Los buques arriban con tasa $\lambda = 8.09$ b/d. Si todas las bermas están ocupadas (o bloqueadas preventivamente para crucero), aguardan en cola bajo disciplina FIFO acumulando tiempo de espera $W_q$.
* **A2: Maniobra de Entrada y Atraque:** Al liberarse una berma, se asigna práctico y remolcador. Insume la fracción correspondiente de las maniobras conjuntas ($T_{man\_in} \sim U(0.5, 1.0)$ h, para un total de atraque + desatraque de 1 a 2 horas). Durante este lapso la berma pasa a estar ocupada, pero las grúas pórtico no pueden operar.
* **A3: Operación de Grúas y Gestión de Patio:** El buque amarrado solicita hasta 2 grúas disponibles de forma competitiva. Si no hay grúas libres en muelle, espera amarrado. Las grúas operan a tasas específicas según el mix de carga, afectadas por interferencia combinada (85%), cambio de turnos y dotaciones nocturnas. Si la ocupación del patio supera el 75%, se induce penalidad de espera por slot.
* **A4: Desatraque y Salida:** Finalizada la faena, se realiza la maniobra de desatraque con práctico y remolcador ($T_{man\_out} \sim U(0.5, 1.0)$ h). Al concluir, la berma queda formalmente libre para el siguiente buque en cola.

---

## 6. Lógicas Operativas del Sistema

A continuación se ilustra el **Diagrama de Flujo Lógico Operativo** que rige el ciclo de vida de cada buque:

![Diagrama de Flujo Lógico Operativo](plots/fig_logica_flujo_buque.png)

### Detalle de las Lógicas Algorítmicas:

#### Lógica 1: Arribo y Asignación de Berma
```text
ALGORITMO Asignar_Berma(Buque):
    Encolar Buque en Cola_Rada (disciplina FIFO)
    SI (Bermas_Ocupadas < B_total) Y NO (Berma_Bloqueada_Crucero):
        Desencolar Buque
        Asignar Berma
        Iniciar Maniobra_Atraque
    SINO:
        Buque permanece fondeado en rada acumulando Wq
```

#### Lógica 2: Maniobras Náuticas Conjuntas de Entrada y Salida
```text
CONJUNTO TOTAL: T_maniobra_total = Uniforme(1.0, 2.0) horas por buque (media 1.5 h)
- Atraque: T_man_in = T_maniobra_total * 0.5
- Desatraque: T_man_out = T_maniobra_total * 0.5
ESTADO: Berma = OCUPADA
RECURSOS STS: INACTIVOS (las grúas no pueden posicionarse durante maniobras de remolque)
```

#### Lógica 3: Contención Física y Asignación de Grúas STS
```text
SOLICITUD DE GRÚAS:
    El buque amarrado solicita 1 o hasta 2 grúas al pool físico de grúas STS.
    SI Grúas_Libres == 0:
        Buque permanece atracado en estado ESPERA_GRUA acumulando T_esp_grua
    AL LIBERARSE GRÚA:
        Gruas_Asignadas = min(2, Grúas_Libres)
        Factor_Velocidad = 1.0 si Gruas_Asignadas == 1 sino 1.70 (0.85 * (1 + 1))
        
        SI Turno_Actual == "Nocturno" Y usa grúa standby:
            Demora_Alistamiento = Uniforme(15/60, 20/60) horas
            
FACTOR DE CONGESTIÓN DE PATIO:
    SI Slots_Ocupados > 2.250:  # (>75% capacidad)
        Factor_Patio = 1.25     # Demora de 25% por falta de espacio
    SINO:
        Factor_Patio = 1.00

TIEMPO DE OPERACIÓN EFECTIVO DE GRÚAS:
    H_nominal = (mov_dry / 28) + (mov_reefer / 21) + (mov_oog / 12)
    T_op_grua = (H_nominal / Factor_Velocidad) * Factor_Patio + Demora_Alistamiento
    # Si ocurre cambio de turno durante T_op_grua, se pausa durante Uniforme(10/60, 15/60) h
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

#### Lógica 5: Dinámica de Patio Bidireccional y Camiones
```text
DESCARGA (Importación): 50% de movimientos ingresan al patio -> ocupan slots.
CARGA (Exportación): 50% de movimientos egresan del patio al buque -> liberan slots.
FLUJO DE CAMIONES:
    - Retiro de importación y entrega de exportación con tiempo de permanencia medio de 72 h.
    - Modulado por puntualidad: 20-30% de camiones llegan fuera de ventana horaria,
      lo que ralentiza la liberación de slots y eleva el inventario.
BALANCE: Slots_Ocupados(t) = min(3.000, max(0, Slots(t-1) + Ingresos - Egresos))
```

#### Lógica 6: Cruceros y Reserva Preventiva Exclusiva
```text
TEMPORADA ALTA: Meses 10, 11 y 12 (2 escalas semanales = 24 cruceros)
VENTANA: Arribo matutino +- 3 horas | Permanencia: Uniforme(28, 36) horas
REGLA DE RESERVA PREVENTIVA: Se bloquea 1 berma antes de la llegada programada
para garantizar 0 horas de espera al crucero.
GRÚAS STS: 0 (No utiliza equipos de muelle; opera con medios propios)
```

#### Lógica 7: Desatraque y Salida
```text
DURACIÓN: T_desatraque = T_maniobra_total * 0.5 (media 0.75 h)
AL FINALIZAR: Se libera formalmente la berma y se registra W = W_q + W_s
```

---

## 7. Elementos del Simulador (Arquitectura SimPy)

A continuación se presenta el diagrama de arquitectura y componentes del simulador SimPy:

![Arquitectura de Componentes del Simulador SimPy](plots/fig_elementos_simulador.png)

### 7.1. Entidades (Processes de SimPy)
* `proceso_buque(env, escala, recursos, monitor)`: Modela el ciclo de vida de cada buque feeder (arribo, espera en rada, maniobra de entrada, amarre, contención de grúas, faena efectiva y maniobra de salida).
* `proceso_crucero(env, inicio, fin, recursos)`: Modela la ocupación de berma con reserva preventiva durante la temporada de cruceros.
* `proceso_turnos(env, recursos)`: Proceso demonio cíclico que controla el temporizador de 8 horas, ejecuta las pausas de cambio de turno y conmuta las grúas diurnas vs. nocturnas.
* `proceso_gestion_patio(env, recursos)`: Proceso demonio que actualiza de manera horaria el inventario de slots del patio y modela la extracción e ingreso estocástico de contenedores por camiones externos.

### 7.2. Recursos del Entorno (`simpy.Environment`)
* `bermas = simpy.Resource(env, capacity=B)`: Modela las bermas físicas del muelle ($B = 3$ o $B = 4$). Cola con disciplina First-In, First-Out (FIFO).
* `gruas_sts = simpy.Resource(env, capacity=G)`: Recurso físico estricto en SimPy que gestiona la disponibilidad simultánea de grúas pórtico.
* `patio_slots = simpy.Container(env, capacity=3000, init=1200)`: Almacena el número instantáneo de contenedores depositados, activando alertas al rebasar los 2.250 slots ($75\%$).

### 7.3. Monitor Estadístico y Variables de Estado
* Registrador individual por buque que captura:
  * `t_arribo`: Instante de llegada a rada.
  * `t_atraque_inicio`: Inicio de maniobra náutica de entrada.
  * `t_atraque_fin`: Fin de atraque y amarre.
  * `t_operacion_inicio`: Inicio de transferencia efectiva con grúas STS.
  * `t_operacion_fin`: Fin de faena de grúas e inicio de desatraque.
  * `t_zarpada`: Salida a mar abierto.
* Cálculo vectorizado de métricas:
  $$W_q = t_{atraque\_inicio} - t_{arribo} \quad (\text{Espera en rada})$$
  $$T_{esp\_grua} = t_{operacion\_inicio} - t_{atraque\_fin} \quad (\text{Espera por grúa amarrado})$$
  $$T_{op\_grua} = t_{operacion\_fin} - t_{operacion\_inicio} \quad (\text{Atención efectiva de grúa})$$
  $$W_s = t_{zarpada} - t_{atraque\_inicio} \quad (\text{Tiempo total en berma})$$
  $$W = t_{zarpada} - t_{arribo} = W_q + W_s \quad (\text{Estadía total})$$
* Validación cruzada automatizada de la **Ley de Little** ($L = \lambda W$) y exportación a formatos tabulares para análisis de varianza (ANOVA) y comparaciones múltiples de Tukey HSD.
