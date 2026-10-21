# TP2 - Simulación de Eventos Discretos: Terminal Portuaria "Puerto Sur"

**ITBA - 11.51 Investigación Operativa (2026 2° Cuatrimestre)**  
**Grupo Asignado:** Grupo 8

---

## 📌 Descripción del Proyecto
Este repositorio contiene el desarrollo del Trabajo Práctico N° 2 de Investigación Operativa, consistente en el modelado conceptual, análisis de datos de entrada, implementación de un simulador de eventos discretos (DES) en Python/SimPy y experimentación estadística para la **Terminal Portuaria Puerto Sur**.

Los objetivos principales incluyen:
- Ajuste estadístico de arribos y portes de buques a partir de 3 años de datos históricos (`data/PuertoSur_escalas_G08.csv`).
- Evaluación de la estadía promedio respecto al umbral crítico de **16 horas**.
- Capacidad máxima del puerto y evaluación de una 4ta grúa STS.
- Impacto de la congestión del patio de 3.000 slots y ventanas horarias de camiones.
- Factibilidad de la incorporación de temporada de cruceros con reserva exclusiva de berma.
- Evaluación de proyectos de inversión bajo incertidumbre (proyecto industrial y 4ta berma de USD 12M).

---

## 📂 Estructura del Repositorio
```text
├── data/                    # Datasets históricos (G08 como principal)
├── src/
│   ├── data_analysis/       # Carga, EDA y ajuste de distribuciones empíricas
│   ├── simulation/          # Núcleo del simulador en SimPy (recursos, procesos y entidades)
│   └── experiments/         # Scripts para correr los escenarios e incisos (a - g)
├── notebooks/               # Visualizaciones interactivas y gráficos
├── docs/                    # Informe final y diagramas conceptuales (IDEF0)
├── AGENTS.md                # Reglas maestras del proyecto para modelos de IA
├── requirements.txt         # Dependencias del proyecto
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

---

## 👥 Flujo de Trabajo Colaborativo (Git)
* La rama `main` contiene únicamente código validado y estable.
* Cada integrante trabaja en ramas con prefijo según la tarea:
  * `feat/<funcionalidad>`
  * `fix/<correccion>`
  * `docs/<informe>`
* Toda integración se realiza mediante **Pull Request** con revisión de al menos un compañero.
* Consultar `AGENTS.md` para las directivas y supuestos de simulación.
