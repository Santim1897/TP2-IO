# Diagnóstico y Fiscalización: Modelo Conceptual (Entrega 25/10/2026)

**Materia:** 11.51 / IO51 - Investigación Operativa (ITBA 2C 2026)  
**Grupo:** Grupo 08  
**Documento Auditado:** `MODELO_CONCEPTUAL_G08.md`  
**Objetivo de la Entrega:** Presentación formal y rigurosa del **Modelo Conceptual del Sistema**, conforme a los 7 puntos esperables definidos por la cátedra (Pág. 1 y 6 de `IO51-TP2 - Puerto Sur.pdf`).

---

## 📊 Tablero de Fiscalización contra Rúbrica Oficial de la Cátedra

| # | Punto de la Rúbrica Oficial (ITBA) | Estado Actual en `MODELO_CONCEPTUAL_G08.md` | Diagnóstico Crítico y Acciones Requeridas |
| :-: | :--- | :---: | :--- |
| **i** | **Objetivo** | 🟢 **Aprobado (Sólido)** | Define claramente el objetivo general y los 6 objetivos específicos, vinculados al umbral crítico de **16 horas de estadía** ($W \le 16\text{ h}$) y a las decisiones de capacidad. |
| **ii** | **Variables de decisión y de referencia** | 🟡 **Aprobado con Observación** | Clasificación completa en variables de control ($B, G, \Pi_{gruas}, \Pi_{nocturna}, \Pi_{camiones}, S_{reefer}, Dec_{crucero}, Dec_{berma4}$), exógenas y de salida/KPIs ($W, W_q, W_s, L, L_q, NS_{16}, \rho$). **Acción:** Corregir en la variable exógena el tiempo de maniobra a conjunto ($U(1, 2)$ h total). |
| **iii** | **Plan de análisis y visualización de resultados** | 🟢 **Aprobado (Excelente)** | Contempla período de calentamiento (*warm-up* vía Welch), 30 réplicas independientes con IC al 95%, test de hipótesis (ANOVA y Tukey HSD pareado), y detalle de gráficos (KDE, boxplots, curvas de nivel de servicio). |
| **iv** | **Relación entre variables** | 🟢 **Aprobado (Muy Claro)** | Diagrama causal de influencias en Mermaid con bucles de realimentación: congestión de patio ($>75\%$) ralentizando grúas, interferencia del 85% en doble grúa, y efecto de turnos reducidos en la noche. |
| **v** | **Diagrama IDEF0** | 🔴 **CRÍTICO: No cumple estándar formal** | Posee un esquema ASCII para A-0, pero la descomposición A0 es un diagrama de flujo simple de Mermaid. **No respeta la norma estricta IDEF0** (flechas ICOM: Entradas por la izquierda, Controles por arriba, Salidas por la derecha, Mecanismos por abajo). Es requisito formal explícito de la cátedra. |
| **vi** | **Lógicas del sistema** | 🔴 **CRÍTICO: Error conceptual en maniobras y patio** | **1. Maniobra:** En la sección 6.2 se escribió erróneamente que atraque dura $U(1, 2)$ h y desatraque $U(1, 2)$ h (duplica el tiempo a 3.0h; el enunciado oficial indica "en conjunto entre 1 y 2 horas").<br>**2. Patio:** La sección 6.4 solo modela el ingreso por descarga, omitiendo la salida de contenedores por carga hacia el buque (~50% de movimientos). |
| **vii** | **Elementos del simulador** | 🟢 **Aprobado (Completo)** | Especifica entidades (`Vessel`, `Cruise`, `Truck`), recursos SimPy (`Resource`, `PriorityResource`, `Container`) y monitores estadísticos. |

---

## 🎯 Plan de Acción Inmediato para la Entrega del 25/10

Para garantizar que el documento obtenga la máxima calificación (10/10) en la primera entrega, se deben realizar las siguientes **3 correcciones puntuales**:

1. **Corrección de la Sección 6.2 (Lógica de Maniobras):**
   * Ajustar la redacción matemática para que el tiempo total de práctico y remolcador sea $T_{maniobra} \sim U(1.0, 2.0)$ horas en total ($\text{media} = 1.5\text{ h}$ total por buque), repartido entre entrada ($T_{in} \sim U(0.5, 1.0)\text{ h}$) y salida ($T_{out} \sim U(0.5, 1.0)\text{ h}$).
2. **Formalización del Diagrama IDEF0 (Sección 5):**
   * Estructurar el diagrama A0 siguiendo rigurosamente la convención de flechas ICOM (Inputs, Controls, Outputs, Mechanisms) para las 4 actividades principales:
     * `A1: Recepcionar y fondear buques en rada`
     * `A2: Maniobrar y atracar en berma`
     * `A3: Operar carga/descarga y transferir a patio`
     * `A4: Desatracar y despachar buque`
3. **Completar la Sección 6.4 (Lógica de Patio):**
   * Incorporar el principio de conservación de balance de masa: cada escala ingresa contenedores de descarga al patio y retira contenedores de carga hacia el buque, interactuando con los camiones externos (tiempo medio de permanencia de 72h e impuntualidad del 20-30%).

---

## 👥 Integrantes del Grupo 08
* Bautista Fanelli
* Santiago Montiel
* Benjamín ...
