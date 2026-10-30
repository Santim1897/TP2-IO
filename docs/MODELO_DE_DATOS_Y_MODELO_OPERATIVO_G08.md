# Modelo de Datos y Modelo Operativo

Trabajo Práctico 2 · Puerto Sur · IO51 · Grupo 08
Instituto Tecnológico de Buenos Aires · Segundo cuatrimestre de 2026
De Palma, Benicio · Fanelli, Bautista · Malbrán, Santiago
30 de octubre de 2026

## Alcance

Este documento desarrolla los dos puntos de la segunda entrega establecidos por la consigna: modelo de datos y modelo operativo. Toma como base el modelo conceptual presentado por el Grupo 08 y el archivo histórico `PuertoSur_escalas_G08.csv`. Distingue los datos observados, los valores provistos por la consigna, los supuestos de cálculo y los parámetros que todavía requieren medición. Los defectos encontrados y corregidos corresponden a la implementación del simulador; por sí solos no invalidan el modelo conceptual de la entrega anterior.

El histórico permite caracterizar arribos, servicio y movimientos por tipo de contenedor. No contiene horas de zarpada ni observaciones de patio y camiones; por eso la estadía y el desempeño del patio que produzca el simulador no pueden validarse contra registros históricos. Se corrigió y ejecutó el simulador para verificar su funcionamiento y sus invariantes básicos. La corrida sirve como evidencia de ejecución, no como validación de resultados ni como recomendación de inversión.

## 1. Modelo de Datos

### 1.1 Cuantificación de las variables

El archivo de Grupo 08 contiene 8.852 escalas entre el 1 de agosto de 2023 y el 30 de julio de 2026. El intervalo observado es de 1.094,69 días. Las variables de entrada medidas en el archivo son fecha y hora de arribo, servicio y cantidad de movimientos dry, reefer y OOG. Cada movimiento equivale a un contenedor; los datos no permiten convertir movimientos a TEU.

| Variable | Cuantificación | Fuente y tratamiento |
|---|---:|---|
| Arribos observados | 8.852 escalas | Registro histórico G08; identificadores únicos. |
| Tasa agregada de arribo, λ | 8,086 buques/día; 0,33693 buques/h | Escalas dividido por duración observada; no supone que los arribos sean Poisson. |
| Tiempo entre arribos agregado | Media 2,968 h; desvío 7,404 h; CV 2,494 | Calculado sobre arribos ordenados. El CV elevado refleja agrupamiento y/o estacionalidad. |
| Bermas y grúas actuales | 3 bermas; 3 grúas STS | Datos de la consigna; las grúas forman una flota compartida. |
| Patio | 3.000 slots; congestión reportada sobre 2.250 slots | Capacidad y umbral de la consigna. No se conoce ocupación inicial observada. |
| Tasas nominales por grúa | Dry 28; reefer 21; OOG 12 movimientos/h | Reefer reduce 25% la tasa dry; OOG usa aparejos y asistencia especiales. |
| Dos grúas en un buque | Factor conjunto 1,70 respecto de una grúa | 85% de la suma de las tasas nominales; se aplica solo mientras las dos operan juntas. |
| Maniobra de atraque y desatraque | 1 a 2 h en conjunto | Rango de la consigna. No se conoce su distribución ni su media observada. |
| Turnos | 08–16 y 16–24: 3 grúas; 00–08: 1 activa y 1 en standby | El standby requiere 15–20 min de alistamiento; el cambio de guardia dura 10–15 min. |
| Patio y camiones | Permanencia media de carga: 72 h; 20–30% de camiones fuera de ventana | La consigna da un promedio y una proporción, pero no la distribución del atraso ni la capacidad de tractores. |
| Cruceros | 2 escalas/semana durante 3 meses; 28–36 h por escala; arribo ±3 h; USD 60.000/escala | Escenario de la consigna. No usan grúas STS y ocupan una berma. |
| Proyecto industrial | Demanda ×1,35 o ×2,00; cuarta berma: USD 12 millones; vida útil 20 años | Escenarios y costos de la consigna. No se asignan probabilidades. |
| Costo de buque detenido | USD 15.000–30.000/día | Rango de la consigna para evaluar la inmovilización evitada. |

La tasa agregada de arribo resume el período completo y sirve para los modelos analíticos a priori. Para generar arribos sintéticos se conservarán el servicio y el calendario: no se impondrá un proceso homogéneo sin comprobarlo. En los registros pueden existir arribos con la misma marca horaria; se conservarán como eventos simultáneos y se desempatarán en la simulación con una regla reproducible.

#### Perfil de movimientos por servicio

| Servicio | Escalas | Participación | Dry medio | Reefer medio | OOG medio | Movimientos medios/escala |
|---|---:|---:|---:|---:|---:|---:|
| Austral Feeder | 3.875 | 43,8% | 76,9 | 18,5 | 2,9 | 98,3 |
| Andes Container Line | 3.325 | 37,6% | 112,7 | 36,9 | 4,6 | 154,2 |
| TransPatagonia Line | 1.652 | 18,7% | 153,9 | 62,3 | 6,6 | 222,7 |

La estacionalidad se ve en los reefer. En octubre-diciembre se observan 45,5 movimientos reefer por escala, frente a 29,3 en los otros meses, un cociente aproximado de 1,55. Para la operación estocástica se preservará la dependencia entre servicio y composición de carga mediante remuestreo de vectores completos por servicio y temporada; no se sorteará cada tipo de carga por separado.

#### Conversión de movimientos a tiempo nominal

Para una escala *i*, la carga de trabajo nominal de una grúa es:

`H_i = mov_dry_i / 28 + mov_reefer_i / 21 + mov_oog_i / 12` horas.

Con una grúa por buque y una maniobra total de referencia de 1,5 h, el tiempo de ocupación simplificado de una berma es `S_i = H_i + 1,5`. La tabla siguiente resume la media por servicio. El valor de 1,5 h es el punto medio del rango 1–2 h y se usa únicamente como supuesto central para el cálculo a priori; no es una media observada.

| Servicio | Trabajo de grúa con 1 grúa, H | Tiempo de berma de referencia, S = H + 1,5 |
|---|---:|---:|
| Austral Feeder | 3,87 h | 5,37 h |
| Andes Container Line | 6,17 h | 7,67 h |
| TransPatagonia Line | 9,01 h | 10,51 h |
| Promedio ponderado G08 | 5,69 h | 7,19 h |

La capacidad de dos grúas se aproximaría por `H_i / 1,70`, pero no se aplica a todas las escalas en los cálculos centrales porque solo hay tres grúas compartidas. En la simulación, su asignación debe depender de la disponibilidad real, el turno y el trabajo elegible.

#### Ajuste de distribuciones de entrada

El repositorio contiene ajustes exploratorios de interarribos por servicio. El mejor candidato según el menor estadístico D de Kolmogorov-Smirnov no supera el contraste nominal al 5% para ninguno de los servicios; además, esos valores p convencionales no corrigen que los parámetros se estimaron con la misma muestra.

| Serie | Candidato mejor rankeado | D de K-S | p nominal | Decisión para el modelo |
|---|---|---:|---:|---|
| Austral Feeder | Exponencial | 0,0314 | 0,00093 | No aceptar como modelo validado. |
| Andes Container Line | Lognormal | 0,0419 | 0,000016 | No aceptar como modelo validado. |
| TransPatagonia Line | Exponencial | 0,0344 | 0,0396 | No aceptar al nivel 5%. |
| Arribos agregados | Lognormal | 0,0325 | 0,000000016 | No aceptar como modelo validado. |

Por lo tanto, el caso de referencia se basará en el replay de arribos históricos. Para escenarios sintéticos se propone remuestrear bloques de datos por servicio y temporada y contrastar la variabilidad resultante con la observada. Una distribución paramétrica podrá usarse como sensibilidad, luego de recalibrar su bondad de ajuste con bootstrap y de analizar tendencias, horas del día y estacionalidad.

### 1.2 Estimaciones a priori con modelos de filas

Se construye una referencia analítica simplificada para contrastarla con el simulador. Se consideran tres bermas como servidores paralelos homogéneos, tasa de arribo `λ = 0,33693` buques/h y tiempo de servicio `S = H + 1,5 h` con una grúa por buque. Esta aproximación no incluye turnos, asignación dinámica de grúas, patio, camiones, cruceros ni bloqueos de transporte.

Para el modelo M/M/3 se usa Erlang C con servicio exponencial. Para M/G/3 y G/G/3 se usa Allen-Cunneen como aproximación:

`Wq_AC ≈ ((Ca² + Cs²) / 2) × Wq_M/M/3`, donde `Ca` y `Cs` son los coeficientes de variación de los interarribos y del tiempo de servicio.

El servicio construido tiene media 7,193 h, desvío 2,232 h y `Cs = 0,310`. La ocupación analítica de las tres bermas es `ρ = λ × E[S] / 3 = 0,808`.

| Modelo | Hipótesis adicional | ρ | Prob. espera | Wq | S | W | L |
|---|---|---:|---:|---:|---:|---:|---:|
| M/M/3, Erlang C | Arribos Poisson y servicio exponencial; 3 servidores | 0,808 | 66,0% | 8,24 h | 7,19 h | 15,43 h | 5,20 buques |
| M/G/3, Allen-Cunneen | Arribos Poisson; servicio general con variabilidad empírica construida | 0,808 | - | 4,51 h | 7,19 h | 11,71 h | 3,94 buques |
| G/G/3, Allen-Cunneen | Usa `Ca = 2,494` medido y el mismo servicio construido | 0,808 | - | 26,02 h | 7,19 h | 33,21 h | 11,19 buques |

`Wq` es espera en rada aproximada, `S` es servicio simplificado en berma, `W = Wq + S` y `L = λ × W`. La probabilidad de espera se informa solo para M/M/3; no se traslada a los otros modelos. Las estimaciones cambian sustancialmente al representar la variabilidad observada de los arribos. La fila G/G/3 debe leerse como análisis de sensibilidad: el CV agregado incorpora agrupamiento y estacionalidad, por lo que la aproximación estacionaria de Allen-Cunneen no es una predicción validada.

Estos modelos son referencias a priori, no una validación de la simulación. En particular, no equivalen al sistema físico: las bermas no tienen grúas independientes, cada buque puede recibir hasta dos grúas y las tres grúas se comparten. El registro tampoco contiene las zarpadas necesarias para comparar `W` observado contra `W` simulado. La diferencia entre las filas muestra por qué no se debe presentar una única estimación de filas como resultado definitivo.

Los valores se reproducen con `python -m src.modelo_datos`. El script genera `data/resumen_modelo_datos_g08.json` y `plots/estimaciones_filas_g08.csv` a partir del CSV de G08.

### 1.3 Plan de experimentación

El objetivo de esta etapa es dejar fijado el diseño; la comparación estadística de alternativas y las conclusiones corresponden a una etapa posterior. Se mantendrán constantes las definiciones de indicadores y el tratamiento de arribos, carga y calendario dentro de cada comparación.

| Experimento | Escenarios y factores | Indicadores principales |
|---|---|---|
| Operación actual | 3 bermas, 3 grúas, turnos informados, sin cruceros y demanda G08 | Estadía total y sus componentes, porcentaje con `W ≤ 16 h`, buques en sistema, utilización y bloqueos. |
| Capacidad y crecimiento | 3/4 grúas, 3/4 bermas y demanda ×0,50 a ×2,00; incluir ×1,35 | Media de W e intervalo al 95%, porcentaje con W ≤ 16 h, buques y movimientos atendidos, colas y utilización. |
| Patio y camiones | Impuntualidad 20/25/30%; ventanas actuales o ampliadas; definir capacidad y reglas de slots reefer antes de compararlos | Ocupación y bloqueos del patio, espera terrestre, demora de transferencia y efecto sobre W. El efecto de una multa se tratará como sensibilidad, no como mejora dada. |
| Cruceros | Sin cruceros, con prioridad no exclusiva y con reserva exclusiva; 24 escalas en 12 semanas | Estadísticas de carga y crucero por separado, espera del crucero, reserva ociosa, efecto en W de carga e ingreso de equilibrio por escala. |
| Proyecto industrial y cuarta berma | Demanda ×1,00, ×1,35 y ×2,00; 3 frente a 4 bermas; cruzar con cruceros | Capacidad, W, horas-buque evitadas, ahorro con USD 15.000–30.000/día y repago simple. Sin probabilidades inventadas; informar criterio de incertidumbre y sensibilidad. |

**Ejecución estadística prevista.** Se usarán al menos 30 réplicas independientes por escenario, semillas registradas y números aleatorios comunes entre alternativas comparables para mejorar la precisión de las diferencias. Cada réplica, no cada buque individual, será la unidad de inferencia. Se calcularán intervalos de confianza al 95% para medias y diferencias; ANOVA y Tukey HSD se aplicarán a resúmenes por réplica si se cumplen sus supuestos. Si no se cumplen, se elegirá un contraste robusto y se documentará.

El flujo de arribos tiene estacionalidad anual, así que el período de calentamiento no se fijará como una cantidad arbitraria de días. Se revisará mediante curvas de Welch y se conservarán ciclos anuales completos; el calentamiento inicial se evaluará con una sensibilidad adicional. Para el baseline se reproducirán las fechas históricas de los tres años y se extenderá la corrida hasta que finalicen las escalas iniciadas dentro del período. En escenarios sintéticos, se preservará la temporada y se reportarán por separado los meses de cosecha.

La consigna fija el umbral de 16 h para la estadía media, pero no establece un porcentaje objetivo de escalas por debajo de ese umbral. Se reportará `P(W ≤ 16 h)` como indicador complementario sin llamarlo requisito contractual.

## 2. Modelo Operativo

### 2.1 Simulador

El simulador del repositorio está implementado en Python con SimPy en `src/simulador.py`. La simulación mide el tiempo desde el arribo a rada hasta que termina el desatraque y se libera la berma. Una réplica utiliza generadores aleatorios locales con semilla, recursos SimPy para bermas y grúas y un `Container` para la capacidad del patio. El modo histórico es la referencia. El modo estocástico remuestrea bloques semanales del mismo mes del histórico para conservar agrupamientos y composición de carga; todavía requiere validación estadística.

| Etapa del proceso | Lógica del modelo operativo | Recursos y estado que deben actualizarse |
|---|---|---|
| Arribo y espera | Reproducir las marcas históricas desde la medianoche local de la primera fecha; procesar escalas simultáneas por orden de llegada al recurso. | Cola de rada y recurso de bermas. |
| Atraque | Simular 1–2 h conjuntas; dividir el tiempo entre atraque y desatraque con una proporción uniforme 45–55%. | Berma ocupada; el práctico y el remolcador se representan como tiempo de maniobra. La distribución y división son supuestos. |
| Transferencia | Solicitar una grúa y esperar su concesión; tomar una segunda solo si está libre. Dos grúas rinden 1,70 veces una. Las tareas se pausan en el cambio de turno. | Recurso compartido de grúas; en turno nocturno inicia una grúa y una segunda puede activarse como standby tras 15–20 min. |
| Patio y camiones | Aproximar carga y descarga como flujos balanceados 50/50. Exportaciones llegan 72 h antes; importaciones quedan en el patio y el retiro terrestre sigue una tasa agregada con media de permanencia de 72 h. | `Container` de 3.000 slots, ocupación inicial supuesta de 1.200, inventario separado en exportación e importación y bloqueo de entregas cuando no hay slots. |
| Desatraque y salida | Terminar la maniobra de salida, liberar berma y registrar la escala una sola vez. | Métricas por buque: espera en rada, espera de grúa, espera de patio, alistamiento, pausa de turno, trabajo efectivo y estadía. |
| Crucero | Programar 24 escalas por ventana de 12 semanas en cada temporada de octubre; variabilidad de arribo ±3 h, reserva exclusiva desde 6 h antes cuando corresponde, permanencia de 28–36 h y sin grúas STS. | Recurso de berma y métricas independientes, incluidas las horas de reserva anticipada. |

La estadía total cumple `W = Wq + Ws`, donde `Wq` es espera en rada y `Ws` es permanencia en berma. La duración de grúa reporta por separado trabajo efectivo, tiempo de reloj, espera de grúa, alistamiento y pausa de cambio de turno. La ocupación del patio nunca se recorta a 3.000: los incrementos usan `Container.put` y esperan capacidad; los retiros usan `Container.get`. Al finalizar la réplica, ocupación y suma de inventarios importación/exportación deben coincidir.

La corrección del simulador resolvió estos defectos identificados en la versión anterior:

| Defecto anterior | Corrección aplicada | Evidencia o limitación vigente |
|---|---|---|
| La solicitud de segunda grúa podía contarse antes de adquirir el recurso. | Ahora se espera la concesión; si no está libre, el buque opera con una grúa. | La asignación registrada no supera dos grúas ni la disponibilidad del recurso. |
| El patio limitaba ocupación con un `min/max`, ocultando excesos y pérdidas. | Ahora usa `simpy.Container` con capacidad y esperas explícitas, sin truncar inventario. | La corrida G08 se mantuvo entre 1.200 y 3.000 slots; inventario final e inventarios por dirección coinciden. |
| El proceso de camiones actuaba sobre toda la ocupación y no había un flujo previo de exportaciones. | Se separan stocks agregados; exportaciones llegan 72 h antes y el retiro terrestre solo consume importaciones. | El retiro sigue agregado: no hay camiones individuales, ventanas observadas ni tractores. |
| El modo estocástico generaba interarribos exponenciales homogéneos. | Ahora remuestrea bloques históricos de siete días del mismo mes. | La generación conserva marca de servicio y movimientos, pero requiere contraste estadístico con G08. |
| Los turnos comenzaban siempre como diurnos, sin conservar la hora del registro. | La simulación se ancla a medianoche local; asigna el turno por hora y pausa tareas durante el relevo. | Verificada una operación que atraviesa el cambio de turno; falta revisar los tres límites con trazas controladas. |
| La reserva de crucero podía empezar en el momento incorrecto y solo se evaluaba una temporada. | Se programan ventanas anuales de 12 semanas y la reserva exclusiva empieza seis horas antes. | El calendario de la consigna se aproxima; confirmar fechas exactas antes del análisis de cruceros. |

### Simplificaciones que permanecen

El patio no modela camiones ni tractores como entidades individuales: la permanencia se aproxima con retiros Poisson por hora y media de 72 h. Las exportaciones se programan exactamente 72 h antes de cada escala, no según una distribución de entrega observada. El stock inicial de 1.200 slots se reparte mitad importación y mitad exportación. Los casos de camiones `penalidad` (10% tardíos) y `ventana_amplia` (15%) son sensibilidades asumidas; el multiplicador de disponibilidad de camiones también es supuesto y no estima el efecto causal de esas políticas. `politica_slots_reefer` se conserva por compatibilidad pero no modifica el simulador hasta definir capacidad y reglas de segregación.

### 2.2 Verificación y validación

**Verificación: comprobar que el código representa las reglas especificadas.** Se ejecutó `python src/run_baseline.py` sobre las 8.852 escalas de G08 con semilla 42. Las 8.852 escalas finalizaron; al cierre no había solicitudes pendientes de berma ni grúa; la ocupación observada del patio se mantuvo entre 1.200 y 3.000 slots; el inventario final coincidió con la suma de stocks; y `W = Wq + Ws` se cumplió para todas las escalas. Una corrida reducida con la misma semilla reprodujo sus tiempos y una operación que atravesó el relevo acumuló la pausa correspondiente.

La corrida verifica ejecución, límites de recursos, conservación del inventario agregado, no negatividad, una salida por escala, descomposición de la estadía y reproducibilidad por semilla. Aún falta la verificación controlada contra un cálculo analítico independiente y la comparación de promedios temporales de la ley de Little. Tampoco se ha ejecutado la batería de escenarios con al menos 30 réplicas.

**Validación: comprobar que el modelo es adecuado para el propósito.** La validación conceptual revisará cada proceso y supuesto contra la consigna y el modelo conceptual. La validación de entradas contrastará conteos, servicios, distribuciones de movimientos, variación entre arribos y estacionalidad con los tres años de G08. La validación de resultados requerirá obtener datos nuevos de hora de inicio y fin de atraque, inicio y término de transferencia, zarpada, asignación de grúas, inventario del patio y eventos de camiones. Como el histórico no contiene zarpadas, todavía no es posible validar cuantitativamente la estadía ni la espera de buques.

La ley de Little que figura en un informe previo del repositorio no es validación independiente: allí se calcula `L` como `λ × W`, por lo que la igualdad es una identidad de cálculo. Se debe comparar contra el promedio temporal independiente de buques presentes.

**Resultado de diagnóstico, no validación.** La corrida unitaria de 8.852 escalas produjo una estadía media `W = 864,16 h` y una espera media en rada `Wq = 854,61 h`; la permanencia media en berma fue `Ws = 9,55 h`. Usando esos valores en una aproximación de tres servidores, `ρ = λ × Ws / 3 ≈ 1,073`, lo que señala que, con las reglas actuales de grúas y turnos, la demanda simulada supera la capacidad efectiva. Este resultado de una sola semilla no debe presentarse como estimación validada: requiere revisar las hipótesis de dotación, horas efectivas, el efecto de la espera de grúa y el período histórico con el equipo docente. La referencia a priori usa otro tiempo de servicio y no representa la flota compartida.

## 3. Supuestos y datos pendientes

| Tema | Supuesto de referencia | Estado y forma de tratarlo |
|---|---|---|
| Maniobras | 1,5 h como valor central dentro del rango conjunto 1–2 h | El promedio y la distribución no están observados. Sensibilizar en 1 h, 1,5 h y 2 h. No afirmar que el rango implica una distribución uniforme. |
| Reparto de movimientos | Aproximadamente 50% descarga y 50% carga | El CSV no identifica dirección; se asigna el resto de redondeo a carga. Sensibilizar la mezcla y validar con manifiestos. |
| Ocupación de patio inicial | 1.200 slots, repartidos mitad importación y mitad exportación | No surge del histórico; reemplazar por medición o evaluar varios niveles iniciales y composiciones. |
| Equivalencia de espacio | 1 contenedor equivale a 1 slot | Simplificación de base; el espacio requerido por OOG debe medirse. |
| Camiones | 25% tardíos como escenario estándar; 10% y 15% como políticas ilustrativas | Solo el intervalo 20–30% proviene de la consigna. Los efectos de ampliar ventanas o penalizar no están cuantificados; son sensibilidades y no recomendaciones. |
| Tractores | Capacidad por turno no especificada | Requiere medición o escenario explícito; no asignar capacidad nocturna sin evidencia. |
| Distribuciones | Replay histórico como referencia | Los ajustes paramétricos existentes son exploratorios; recalibrar con bootstrap y conservar dependencia temporal y de carga. |
| Cruceros | 24 escalas en 12 semanas; reserva exclusiva 6 h antes | Implementación de la aproximación de 2 por semana; validar fecha de inicio, reserva y calendario con la cátedra. |
| Estadía observada | No disponible en el dataset entregado | Solicitar marcas de tiempo operativas antes de afirmar validación cuantitativa de W. |

## 4. Fuentes y trazabilidad

1. Cátedra IO51, `IO51-TP2 - Puerto Sur.pdf`, enunciado general, especialmente pp. 1–6.
2. `data/PuertoSur_escalas_G08.csv`, registro histórico de Grupo 08.
3. `docs/TP2_Grupo8_primera_entrega.pdf`, modelo conceptual presentado por el Grupo 08.
4. Cátedra IO51, `assets/IO51_Teoria_Simulacion_Modelo_de_Datos_Ajuste.pdf`.
5. Código del repositorio: análisis de datos, parámetros, simulador y experimentos.
