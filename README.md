# TP2 - Simulación de Eventos Discretos: Terminal Portuaria "Puerto Sur"

**ITBA - 11.51 Investigación Operativa (2026 2° Cuatrimestre)**  
**Grupo:** Grupo 08  
**Dataset Oficial:** `data/PuertoSur_escalas_G08.csv` (8.852 escalas históricas)

Este repositorio contiene el desarrollo del Trabajo Práctico N° 2 de Investigación Operativa: modelado conceptual, análisis de datos de entrada, implementación de un simulador de eventos discretos (DES) en Python con **SimPy**, análisis estadístico riguroso (Tukey HSD, ANOVA, intervalos de confianza al 95%), teoría de colas a priori ($M/M/c$ y $M/G/c$) y recomendaciones estratégicas de negocio para la **Terminal Portuaria Puerto Sur**.

---

## 📂 Estructura del Repositorio

```text
TP2-IO/
├── data/                            <- Datasets históricos (G08 como principal) y parámetros
│   ├── PuertoSur_escalas_G08.csv
│   └── distribuciones_g08.json
├── plots/                           <- Figuras analíticas a 300 DPI y tablas resumen
├── src/                             <- Código fuente modular
│   ├── paths.py                     <- Resolución centralizada de rutas relativas
│   ├── data_analysis.py             <- Ingesta y análisis exploratorio del dataset G08
│   ├── data_analysis_fitter.py      <- Ajuste formal de distribuciones y bondad de ajuste (K-S / Chi²)
│   ├── simulador.py                 <- Motor central de simulación de eventos discretos en SimPy
│   ├── queue_theory_apriori.py      <- Modelo analítico de colas a priori (Erlang C y Allen-Cunneen)
│   ├── run_baseline.py              <- Simulación de la operación actual (Consignas a y b)
│   ├── run_experiments.py           <- Batería multiescenario completa (Consignas c a g)
│   ├── generate_plots.py            <- Generación de figuras analíticas a 300 DPI
│   └── generate_word_report.py      <- Exportación del informe ejecutivo a formato Word
├── docs/                            <- Documentación técnica y diagramas (IDEF0)
├── INFORME_EJECUTIVO_PUERTO_SUR.md  <- Informe final exhaustivo y autocontenido de todo el TP
├── MODELO_CONCEPTUAL_G08.md         <- Documento del Modelo Conceptual
├── AGENTS.md                        <- Reglas maestras del proyecto para modelos de IA
├── requirements.txt                 <- Dependencias del entorno de Python
└── README.md
```

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
