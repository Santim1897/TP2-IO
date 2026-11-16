# Entrega C — resumen de resultados vigente

La versión entregable y completa es el Word `INFORME_FINAL_ENTREGA_C_GRUPO08.docx`, ubicado en la raíz del repositorio. Este Markdown resume las cifras de esa versión. Los documentos previos de Entrega C conservados en `docs/` son históricos; el Word de la raíz es la única versión oficial para entregar.

## Corrida y procedencia

Se volvió a ejecutar la campaña con el simulador `src/simulador.py` y el dataset `data/PuertoSur_escalas_G08.csv` del commit fuente `da1151976ba8d2bf1394f84623308db16607053c`. La campaña principal cubre 17 alternativas y 30 réplicas por alternativa, con 60 días de calentamiento. Los scripts y todos los resultados quedan en `src/experiments/` y `plots/entrega_c_reproducible/`.

## Resultados destacados

| Escenario | Estadía media W | Buques con W ≤ 16 h |
|---|---:|---:|
| Base, 3 grúas | 12,44 h (IC 95 %: 12,42–12,47) | 76,03 % |
| Base, 4 grúas | 8,76 h (IC 95 %: 8,75–8,78) | 91,50 % |

La comparación pareada estima una reducción de `W` de 3,68 h al pasar de tres a cuatro grúas (IC 95 %: 3,65–3,71; `p < 0,001`). El objetivo conjunto del modelo se cumple con cuatro grúas en el escenario base. Para tres grúas, el mayor factor de demanda probado que cumple ambos umbrales fue 0,85.

La alternativa de cuatro bermas con tres grúas reduce `W` en 2,88 h frente a tres bermas (IC 95 %: 2,85–2,91; `p < 0,001`). En los escenarios industriales censurados no se informa una `W` de equilibrio como si fuera válida. La evaluación de cruceros se limita a la ventana simulada de 90 días; sus resultados no se extrapolan al año completo.

## Reproducción

Ver [`plots/entrega_c_reproducible/README.md`](plots/entrega_c_reproducible/README.md) para el orden de ejecución, semillas, hashes de procedencia y archivos de salida.
