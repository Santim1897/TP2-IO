# Hoja de Ruta y Backlog de Auditoría — TP2 Puerto Sur (Grupo 8)

Este documento centraliza el estado de avance, las tareas completadas y los próximos pasos para que todo el equipo (Bauti, Santi y Beni) esté sincronizado y no se dupliquen esfuerzos de cara a la entrega del **25/10/2026**.

---

## 🚦 Tablero de Estado de Avance

| Fase / Tarea | Estado | Responsable / Rama | PR en GitHub | Descripción |
| :--- | :---: | :---: | :---: | :--- |
| **0. Reglas y Setup Base** | ✅ **Completado** | `feat/project-rules-setup` | [PR #1](https://github.com/Santim1897/TP2-IO/pull/1) | `AGENTS.md`, `.gitignore`, `requirements.txt`, limpieza de binarios `.pyc`. |
| **1. Portabilidad de Rutas** | ✅ **Completado** | `feat/audit-steps-1-2` | [PR #2](https://github.com/Santim1897/TP2-IO/pull/2) | `src/paths.py` (eliminación de rutas `C:/Users/ASUS/...`). Corrección de maniobra a 1.5h. |
| **2. Input Modeling & K-S** | ✅ **Completado** | `feat/audit-steps-1-2` | [PR #2](https://github.com/Santim1897/TP2-IO/pull/2) | Ajuste Kolmogorov-Smirnov por servicio y `data/distribuciones_g08.json`. |
| **3. Corrección Física de Simulación** | 🔄 **En Progreso** | `feat/simulador-fisica-real` | Pendiente | Grúas como recurso SimPy real (sin grúas fantasma), reserva preventiva de crucero y balance de patio. |
| **4. Motor de 30 Réplicas & Tukey** | ⏳ **Pendiente** | — | — | Intervalos de confianza 95% y Tukey HSD sobre medias de réplicas independientes. |
| **5. Regeneración de Gráficos (300 DPI)** | ⏳ **Pendiente** | — | — | Regenerar `fig1` a `fig4` y tablas CSV con números validados. |
| **6. Informe Final (IDEF0) y PPT** | ⏳ **Pendiente** | — | — | Diagrama IDEF0, actualización de informe y presentación ejecutiva PowerPoint. |

---

## 📌 Detalle de Fases y Especificaciones

### Fase 0: Reglas Institucionales y Entorno ✅
* Se formalizaron en `AGENTS.md` todos los supuestos operativos del puerto (tasas de grúas STS: 28 Dry, 21 Reefer, 12 OOG; interferencia del 85%; turnos rotativos; patio de 3.000 slots).
* Entorno de Python configurado con `simpy`, `statsmodels`, `scipy`, `pandas` y `python-docx`.

### Fase 1: Portabilidad y Corrección de Rutas ✅
* Se reemplazaron todas las rutas absolutas hacia carpetas personales por rutas dinámicas con `pathlib.Path` a través de `src/paths.py`. El proyecto ahora corre en Windows, Linux y Mac sin tocar código.
* Se corrigió la maniobra conjunta a $1.5\text{ h}$ total en vez de $3.0\text{ h}$ duplicadas.

### Fase 2: Input Modeling y Ajuste de Distribuciones ✅
* Ajuste de distribuciones continuas para tiempos entre arribos ($\Delta t$):
  * **Austral Feeder (43.8%):** Exponencial ($D = 0.0314, \mu = 6.78\text{ h}$).
  * **Andes Container Line (37.6%):** Lognormal ($D = 0.0419, \mu = 7.90\text{ h}$).
  * **TransPatagonia Line (18.7%):** Exponencial ($D = 0.0344, \mu = 15.90\text{ h}$).
* Se comprobó el pico estacional de fruta (+50% en Reefer) en los meses 10, 11 y 12.
* Parámetros serializados en `data/distribuciones_g08.json`.

---

### Fase 3: Corrección Quirúrgica del Simulador 🔄 (EN CURSO)
* **Objetivo:** Refactorizar `src/simulador.py` para cumplir fielmente las restricciones físicas del puerto:
  1. **Grúas como Recursos SimPy (`simpy.Resource(capacity=3)`):** Eliminar el contador entero `gruas_en_uso`. Si no hay grúas libres, los buques atracados deben esperar en cola por grúa en vez de invocar grúas que no existen físicamente.
  2. **Dinámica de Turnos:** Que el turno nocturno limite efectivamente a 1 grúa activa + 1 en standby (alistamiento 15-20m) sobre el recurso SimPy, y que los buques en atención reduzcan su ritmo si el turno cambia.
  3. **Reserva Preventiva para Cruceros:** Implementar un mecanismo de bloqueo previo de berma para garantizar que el crucero atraque sin espera en su ventana matutina ($\pm 3\text{h}$).
  4. **Balance Integral de Patio:** Cada escala descarga ~50% de contenedores (entran al patio) y carga ~50% de contenedores (salen del patio hacia el buque).

---

### Fase 4: Motor de Réplicas y Análisis Estadístico Formal ⏳
* Ejecutar 30 réplicas independientes con semillas distintas para el caso base y los escenarios de comparación.
* Calcular Media $\pm$ Intervalo de Confianza al 95% ($\bar{X} \pm t_{\alpha/2} \frac{S}{\sqrt{n}}$).
* Corregir el test de Tukey HSD: calcularlo sobre las medias muestrales de las 30 réplicas (eliminando el sesgo por autocorrelación temporal intra-cola).
* Contrastar contra modelos analíticos de teoría de colas ($M/M/3$ y aproximación de Allen-Cunneen para $M/G/3$).

---

### Fase 5: Regeneración de Gráficos y Tablas ⏳
* Ejecutar la batería multiescenario completa (incisos b al g) y actualizar:
  * `plots/fig1_capacidad_demanda.png` (3 vs 4 grúas y umbral 16h).
  * `plots/fig2_desglose_estadia.png` (Espera $W_q$ vs Servicio $W_s$).
  * `plots/fig3_repago_berma.png` (Análisis de repago de USD 12M).
  * `plots/fig4_tukey_hsd.png` (Tukey HSD con IC 95% corregido).
  * Tablas CSV complementarias.

---

### Fase 6: Informe Final, Diagrama IDEF0 y Presentación Ejecutiva ⏳
* Diseñar e incorporar el **Diagrama IDEF0** en `docs/` y en el informe.
* Actualizar el informe ejecutivo (`INFORME_EJECUTIVO_PUERTO_SUR.md` y `.docx`) con los resultados estadísticos definitivos.
* Crear la presentación en diapositivas (`.pptx`) estructurada para la defensa oral del TP.
