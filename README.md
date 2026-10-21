# TP2 - Investigación Operativa: Simulación Terminal Portuaria "Puerto Sur"
**Instituto Tecnológico de Buenos Aires (ITBA) — 2° Cuatrimestre 2026**  
**Grupo:** Grupo 08  
**Dataset Oficial:** `PuertoSur_escalas_G08.csv` (8.852 escalas históricas)

Este repositorio contiene la resolución integral, modelado conceptual, implementación computacional en **SimPy**, análisis estadístico comparativo (Tukey HSD, ANOVA, intervalos de confianza al 95%), teoría de colas a priori ($M/M/c$ y $M/G/c$) y recomendaciones estratégicas de negocio para el **Trabajo Práctico N° 2: "Puerto Sur"**.

---

## 📁 Estructura del Repositorio

```text
TP2-IO/
├── plots/
│   ├── fig1_capacidad_demanda.png   <- Curva de nivel de servicio vs. demanda diaria (3 vs 4 grúas)
│   ├── fig2_desglose_estadia.png    <- Desglose de estadía: Tiempo en Berma (Ws) vs Espera en Rada (Wq)
│   ├── fig3_repago_berma.png        <- Período de repago de la 4ª berma vs costo de inmovilización
│   ├── fig4_tukey_hsd.png           <- Test de comparaciones múltiples de Tukey HSD (IC 95%)
│   ├── capacidad_demanda.csv        <- Resultados tabulados del barrido de demanda
│   ├── matriz_bermas_repago.csv     <- Análisis de repago y buques-año evitados
│   ├── resumen_base_vs_4gruas.csv   <- Comparativa de operación base vs 4ª grúa
│   └── tukey_hsd_resultados.csv     <- Matriz estadística formal de Tukey HSD
├── src/
│   ├── simulador.py                 <- Motor central de simulación de eventos discretos en SimPy
│   ├── data_analysis.py             <- Ingesta y análisis exploratorio del dataset G08 (8.852 buques)
│   ├── queue_theory_apriori.py      <- Modelo analítico de colas a priori (Erlang C y Allen-Cunneen)
│   ├── run_baseline.py              <- Simulación de la operación actual (Consignas a y b)
│   ├── run_experiments.py           <- Batería multiescenario completa (Consignas c a g)
│   └── generate_plots.py            <- Generación de figuras analíticas a 300 DPI
├── INFORME_EJECUTIVO_PUERTO_SUR.md  <- Informe final exhaustivo y autocontenido de todo el TP
├── MODELO_CONCEPTUAL_G08.md         <- Documento específico del Modelo Conceptual (7 puntos del buzón)
├── main.py                          <- Script orquestador punta a punta
├── requirements.txt                 <- Dependencias del entorno de Python
└── IO51-TP2 - Puerto Sur.pdf        <- Enunciado oficial de la cátedra
```

---

## 🚀 Instalación y Ejecución Rápida

### 1. Clonar e instalar dependencias
```bash
git clone https://github.com/Santim1897/TP2-IO.git
cd TP2-IO
pip install -r requirements.txt
```

### 2. Ejecutar la suite completa
Para correr el análisis de datos, el modelo de colas, las simulaciones multiescenario y regenerar los gráficos:
```bash
python main.py
```

---

## 📊 Resumen Consolidado de Resultados (Grupo 8)

| Consigna | Tema Clave | Métrica Principal | Conclusión / Recomendación |
| :--- | :--- | :---: | :--- |
| **Consigna b** | Operación Actual vs. Umbral 16h | $W = 24.25$ h, $W_q = 16.32$ h (67.3% espera) | El reclamo de las navieras es real: el 58.1% de buques supera el umbral de 16h. |
| **Consigna c** | 4ª Grúa Pórtico STS y Capacidad | $W$ baja a $16.46$ h; espera en rada cae un 44.5% | **Aprobar la 4ª grúa**. Permite atender la demanda actual dentro del umbral. |
| **Consigna d** | Patio y Ventanas de Camiones | Multas reducen tardíos del 25% al 10% | Implementar penalidades; segregar slots reefer para cosecha frutícola. |
| **Consigna e** | Temporada de Cruceros | Exclusividad añade +12.88 h/buque de carga | **Rechazar reserva exclusiva**. Canon ofrecido (\$60k) es insuficiente frente a pérdidas (\$990k-\$1.98M necesarios). |
| **Consigna f** | Proyecto Industrial (Incertidumbre) | 3 bermas colapsan ($\rho > 1.13$) | La 4ª berma domina bajo todos los criterios (Wald, Savage, Laplace). |
| **Consigna g** | Repago 4ª Berma (USD 12M) | Ahorro: 5.97 años-buque/año (USD 49.0M/año) | **Payback de 0.24 años (~3 meses)**. Decisión unánimemente favorable. |
