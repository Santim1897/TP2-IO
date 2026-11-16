# Entrega C: campaña reproducible

El informe oficial de Entrega C es `INFORME_FINAL_ENTREGA_C_GRUPO08.docx`, en la raíz del repositorio. Los documentos previos de Entrega C que están en `docs/` se conservan como archivo histórico (`ParteC_Experimentacion_y_Analisis_Puerto_Sur_G08_COMPLETO.docx`, `ParteC_Puerto_Sur_G08_CORREGIDA.docx` y `ParteC_Puerto_Sur_G08_CORREGIDA_v4.docx`); sus cifras no deben usarse en lugar del informe oficial actualizado.

## Procedencia

La campaña se ejecutó con el simulador y los datos G08 existentes en el commit fuente `da1151976ba8d2bf1394f84623308db16607053c`. El CSV contiene 8.852 escalas. Este commit incorpora los scripts de reproducción, sus resultados y el informe actualizado; no cambia `src/simulador.py` ni el dataset usado para la corrida.

`run_metadata.json` registra las semillas, el calentamiento, el tiempo de ejecución y los SHA-256 del CSV y del simulador. `supplement_metadata.json` identifica de igual manera los análisis complementarios.

## Reproducción

Desde la raíz del repositorio, con las dependencias de `requirements.txt` instaladas, ejecutar:

```powershell
python src/experiments/recompute_campaign_c.py
python src/experiments/recompute_supplementary_c.py
python src/experiments/recompute_cruise_window_c.py
python src/experiments/recompute_anova_tukey_c.py
```

Los scripts escriben las tablas y figuras en esta carpeta. La campaña principal corre 17 alternativas con 30 réplicas por alternativa (510 corridas), usa semillas `202601 + (réplica - 1) × 101` y descarta las primeras 1.440 horas para el calentamiento. El análisis ANOVA/Tukey usa réplicas independientes y su propia secuencia de semillas, documentada en el script.

## Lectura de resultados principales

- 3 grúas en el escenario base: `W = 12,44 h`; `P(W ≤ 16 h) = 76,03 %`.
- 4 grúas en el escenario base: `W = 8,76 h`; `P(W ≤ 16 h) = 91,50 %`.
- En el barrido de demanda, 3 grúas cumplen ambos objetivos hasta el factor probado 0,85; 4 grúas los cumplen en el factor 1,00.
- Las alternativas industriales que no completan las 30 corridas se reportan como censuradas. No se interpreta una estadía estable a partir de esas corridas.

Las cifras completas, sus intervalos y las limitaciones de cada comparación están en el informe oficial y en los CSV de esta carpeta.
