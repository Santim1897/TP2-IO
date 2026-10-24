# Hoja de Ruta y Backlog de Auditoría — TP2 Puerto Sur (Grupo 8)

Este documento centraliza el estado de avance, las tareas completadas y los próximos pasos para que todo el equipo (Bauti, Santi y Beni) esté sincronizado y no se dupliquen esfuerzos de cara a las entregas de la materia.

> [!IMPORTANT]
> **ENTREGA INMEDIATA (25/10/2026): MODELO CONCEPTUAL ÚNICAMENTE**  
> La cátedra exige para este **25 de Octubre** exclusivamente la entrega del **Modelo Conceptual** (los 7 puntos pautados en la página 1 del enunciado).  
> La simulación completa, réplicas y análisis financiero corresponden a la entrega final posterior.  
> 👉 **Diagnóstico detallado y puntos críticos a revisar:** [`docs/DIAGNOSTICO_MODELO_CONCEPTUAL.md`](DIAGNOSTICO_MODELO_CONCEPTUAL.md).

---

## 🚦 Tablero de Estado de Avance

| Fase / Tarea | Estado | Rama en Git | PR en GitHub | Descripción |
| :--- | :---: | :---: | :---: | :--- |
| **0. Reglas y Setup Base** | ✅ **Completado** | `feat/project-rules-setup` | [PR #1](https://github.com/Santim1897/TP2-IO/pull/1) | `AGENTS.md`, `.gitignore`, `requirements.txt`, limpieza de binarios `.pyc`. |
| **1. Portabilidad de Rutas** | ✅ **Completado** | `feat/audit-steps-1-2` | [PR #2](https://github.com/Santim1897/TP2-IO/pull/2) | `src/paths.py` (eliminación de rutas `C:/Users/ASUS/...`). Corrección de maniobra a 1.5h. |
| **2. Input Modeling & K-S** | ✅ **Completado** | `feat/audit-steps-1-2` | [PR #2](https://github.com/Santim1897/TP2-IO/pull/2) | Ajuste Kolmogorov-Smirnov por servicio y `data/distribuciones_g08.json`. |
| **3. Corrección Física de Simulación** | ✅ **Completado** | `feat/simulador-fisica-real` | [PR #3](https://github.com/Santim1897/TP2-IO/pull/3) | Grúas como `PriorityResource` (sin grúas fantasma), reserva preventiva de crucero y balance de patio. |
| **🎯 ENTREGA 25/10: Modelo Conceptual** | 🔄 **En Revisión** | `feat/simulador-fisica-real` | [PR #3](https://github.com/Santim1897/TP2-IO/pull/3) | Auditoría contra rúbrica de 7 puntos. Ver `docs/DIAGNOSTICO_MODELO_CONCEPTUAL.md`. |
| **4. Motor de 30 Réplicas & Tukey** | ⏳ **Entrega Final** | — | — | Intervalos de confianza 95% y Tukey HSD sobre medias de réplicas independientes. |
| **5. Regeneración de Gráficos (300 DPI)** | ⏳ **Entrega Final** | — | — | Regenerar `fig1` a `fig4` y tablas CSV con números validados. |
| **6. Informe Final (IDEF0) y PPT** | ⏳ **Entrega Final** | — | — | Diagrama IDEF0 final, informe ejecutivo consolidado y presentación PowerPoint. |

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

### Fase 3: Corrección Quirúrgica del Simulador ✅
* Refactorizado `src/simulador.py` con contención física real:
  * Grúas STS modeladas como `simpy.PriorityResource(capacity=3)`: buques atracados esperan en cola si las grúas están ocupadas (cero grúas fantasma).
  * Maniobra conjunta de atraque y desatraque con práctico y remolcador calibrada a $U(1, 2)$ ($1.5\text{ h}$ media).
  * Reserva preventiva de berma para temporada de cruceros (0 espera en rada).
  * Balance integral de patio (ingreso de descarga + egreso de exportación).
  * Resultados base de 8.852 escalas: estadía promedio $W = 15.00\text{ h}$, con 32.91% de escalas superando el límite de 16h (puerto saturado).

---

### Fase 4: Motor de Réplicas y Análisis Estadístico Formal ⏳ (Para entrega final)
* Ejecutar 30 réplicas independientes con semillas distintas para el caso base y los escenarios de comparación.
* Calcular Media $\pm$ Intervalo de Confianza al 95% ($\bar{X} \pm t_{\alpha/2} \frac{S}{\sqrt{n}}$).
* Corregir el test de Tukey HSD: calcularlo sobre las medias muestrales de las 30 réplicas (eliminando el sesgo por autocorrelación temporal intra-cola).
* Contrastar contra modelos analíticos de teoría de colas ($M/M/3$ y aproximación de Allen-Cunneen para $M/G/3$).

### Fase 5: Regeneración de Gráficos y Tablas ⏳ (Para entrega final)
* Ejecutar la batería multiescenario completa (incisos b al g) y actualizar:
  * `plots/fig1_capacidad_demanda.png` (3 vs 4 grúas y umbral 16h).
  * `plots/fig2_desglose_estadia.png` (Espera $W_q$ vs Servicio $W_s$).
  * `plots/fig3_repago_berma.png` (Análisis de repago de USD 12M).
  * `plots/fig4_tukey_hsd.png` (Tukey HSD con IC 95% corregido).
  * Tablas CSV complementarias.

### Fase 6: Informe Final, Diagrama IDEF0 Consolidado y Presentación Ejecutiva ⏳ (Para entrega final)
* Diseñar e incorporar el **Diagrama IDEF0** definitivo en `docs/` y en el informe.
* Actualizar el informe ejecutivo (`INFORME_EJECUTIVO_PUERTO_SUR.md` y `.docx`) con los resultados estadísticos definitivos.
* Crear la presentación en diapositivas (`.pptx`) estructurada para la defensa oral del TP.
