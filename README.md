# TP2 - Simulación de Eventos Discretos: Terminal Portuaria "Puerto Sur"

**ITBA - 11.51 Investigación Operativa (2026 2° Cuatrimestre)**  
**Grupo:** Grupo 08  
**Dataset Oficial:** `data/PuertoSur_escalas_G08.csv` (8.852 escalas históricas)

Este repositorio contiene el modelo conceptual, el análisis del histórico G08, un simulador de eventos discretos (DES) en Python con **SimPy**, referencias analíticas de teoría de colas y el plan de experimentación para la **Terminal Portuaria Puerto Sur**. Las salidas de una corrida individual son diagnósticas; todavía no constituyen resultados estadísticos validados ni recomendaciones de inversión.

---

## 🎯 Estado de Entregas y Documentación Clave

> [!IMPORTANT]
> **PRIMERA ENTREGA: MODELO CONCEPTUAL (RÚBRICA DE 7 PUNTOS)**
> Para la primera entrega se evalúa exclusivamente el modelo conceptual del sistema.  
> 👉 **Tablero de diagnóstico y puntos críticos a corregir:** [docs/DIAGNOSTICO_MODELO_CONCEPTUAL.md](docs/DIAGNOSTICO_MODELO_CONCEPTUAL.md)  
> 👉 **Hoja de ruta y backlog del equipo:** [docs/BACKLOG_AUDITORIA.md](docs/BACKLOG_AUDITORIA.md)
> 👉 **PDF presentado por el Grupo 08:** [docs/TP2_Grupo8_primera_entrega.pdf](docs/TP2_Grupo8_primera_entrega.pdf)
> Los archivos `MODELO_CONCEPTUAL_G08.md` y `MODELO_CONCEPTUAL_G08.docx` son documentos de trabajo distintos del PDF presentado.

---

## 📁 Estructura del Repositorio

```text
TP2-IO/
├── data/                            <- Datasets históricos (G08 como principal) y parámetros
│   ├── PuertoSur_escalas_G08.csv
│   ├── distribuciones_g08.json
│   └── resumen_modelo_datos_g08.json <- Resumen reproducible de entradas y filas
├── plots/                           <- Figuras analíticas y tablas resumen
│   └── estimaciones_filas_g08.csv   <- Resultados de los modelos analíticos a priori
├── src/                             <- Código fuente modular
│   ├── paths.py                     <- Resolución centralizada de rutas relativas
│   ├── data_analysis.py             <- Ingesta y análisis exploratorio del dataset G08
│   ├── data_analysis_fitter.py      <- Ajuste formal de distribuciones y bondad de ajuste (K-S / Chi²)
│   ├── simulador.py                 <- Motor central de simulación de eventos discretos en SimPy
│   ├── queue_theory_apriori.py      <- Modelo analítico de colas a priori (Erlang C y Allen-Cunneen)
│   ├── modelo_datos.py              <- Cuantificación G08 y estimaciones a priori reproducibles
│   ├── run_baseline.py              <- Simulación de la operación actual (Consignas a y b)
│   ├── run_experiments.py           <- Runner exploratorio legado; no implementa 30 réplicas
│   ├── generate_plots.py            <- Generación de figuras analíticas a 300 DPI
│   └── generate_word_report.py      <- Exportación del informe ejecutivo a formato Word
├── docs/                            <- Documentación técnica y diagramas (IDEF0)
├── INFORME_EJECUTIVO_PUERTO_SUR.md  <- Informe final exhaustivo y autocontenido de todo el TP
├── MODELO_CONCEPTUAL_G08.md         <- Documento del Modelo Conceptual
├── AGENTS.md                        <- Reglas maestras del proyecto para modelos de IA
├── requirements.txt                 <- Dependencias del entorno de Python
└── README.md
```

## Segunda entrega: Modelo de Datos y Modelo Operativo

El documento de la segunda entrega está en [`docs/MODELO_DE_DATOS_Y_MODELO_OPERATIVO_G08.docx`](docs/MODELO_DE_DATOS_Y_MODELO_OPERATIVO_G08.docx); su fuente editable está en [`docs/MODELO_DE_DATOS_Y_MODELO_OPERATIVO_G08.md`](docs/MODELO_DE_DATOS_Y_MODELO_OPERATIVO_G08.md).

Para reproducir la cuantificación de G08 y las referencias analíticas de filas, ejecutar desde la raíz:

```bash
python -m src.modelo_datos
```

El comando genera `data/resumen_modelo_datos_g08.json` y `plots/estimaciones_filas_g08.csv`. Para ejecutar el simulador histórico desde la raíz:

```bash
python src/run_baseline.py
```

El simulador fue corregido para adquirir recursos explícitamente, respetar los relevos de turno, conservar el calendario de arribo y controlar el patio con capacidad finita. Una corrida de verificación con semilla 42 completó las 8.852 escalas; su estadía media fue 864,16 h, lo que señala sobrecarga bajo los supuestos actuales y requiere revisión. Ese valor procede de una sola corrida y no debe citarse como resultado validado. El plan estadístico exige al menos 30 réplicas independientes; `src/run_experiments.py` todavía no implementa ese diseño y sus comparaciones no deben usarse para inferencia.

---

## 🚀 Instalación y Puesta en Marcha

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Santim1897/TP2-IO.git
   cd TP2-IO
   ```

2. **Crear y activar entorno virtual:**
   * En Windows:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   * En Linux/macOS:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la suite completa:**
   ```bash
   python main.py
   ```

---

## 👥 Flujo de Trabajo Colaborativo (Git)
* La rama `main` contiene únicamente código validado y estable.
* Cada integrante trabaja en ramas con prefijo según la tarea:
  * `feat/<funcionalidad>`
  * `fix/<correccion>`
  * `docs/<informe>`
* Toda integración se realiza mediante **Pull Request** con revisión de al menos un compañero.
* Consultar `AGENTS.md` para las directivas y supuestos de simulación.
