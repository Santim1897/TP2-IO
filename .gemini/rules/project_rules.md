# Reglas del Proyecto TP2 Simulación (Puerto Sur - ITBA IO 11.51)

1. **Contexto:** Trabajo Práctico N° 2 de Simulación para la cátedra de Investigación Operativa (ITBA). Grupo 8 asignado (`data/PuertoSur_escalas_G08.csv`).
2. **Documento Maestro:** Consultar siempre `AGENTS.md` y `IO51-TP2 - Puerto Sur.pdf` para conocer todos los parámetros del sistema (3 bermas, 3 grúas STS, patio de 3000 slots, turnos, umbral de 16h, cruceros, etc.).
3. **Pila Tecnológica:** Python 3 con SimPy para la simulación de eventos discretos, SciPy/Statsmodels para análisis estadístico (tests de bondad de ajuste, Tukey, IC 95%).
4. **Buenas Prácticas:**
   - Todo proceso estocástico debe ser reproducible mediante semilla (`seed`).
   - Mínimo 30 réplicas independientes por experimento.
   - Conservar modularidad entre análisis de datos (`src/data_analysis`), modelo del simulador (`src/simulation`) y experimentos de los incisos (`src/experiments`).
   - Respetar el flujo de Git colaborativo: ramas `feat/...` y PRs.
