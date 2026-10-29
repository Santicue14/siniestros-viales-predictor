# Clasificación de la gravedad de los siniestros viales en CABA, 2019-2025

Trabajo de Inteligencia de negocios (LGTI, UNPAZ, 2026). Santiago Baldini Cuevas. Docente: Ernesto Aguaysol.

La pregunta es si un siniestro vial ya ocurrido en la Ciudad de Buenos Aires fue leve, grave o mortal. La serie es la de hechos del Observatorio de Movilidad y Seguridad Vial, del 1 de enero de 2019 al 31 de diciembre de 2025: 65.818 filas. El modelo elegido es un random forest.

## Por dónde empezar

El informe escrito está en estos dos archivos:

- [docs/BaldiniCuevas_Santiago_BI.docx](docs/BaldiniCuevas_Santiago_BI.docx). Es el documento para leer y editar: carátula, abstract, estado del arte, ejecución, conclusiones, problemas y líneas futuras.
- [docs/Clasificación de Siniestros Viales CABA 2019-2025.pdf](<docs/Clasificación de Siniestros Viales CABA 2019-2025.pdf>). Es la versión en PDF del mismo trabajo, 17 páginas.

La consigna de la cátedra está en `UNPAZ - LGTI - Inteligencia de negocios - Trabajo Teórico Práctico.pdf`.

## Recorrido

1. **De dónde salen los datos.** `data/ORIGEN.txt` dice cuál es el archivo original y qué es derivado. El original, que no se modifica, es `data/siniestros_viales_hechos.csv`. Las definiciones de leve, grave y mortal están en `data/NOTAS_SINIESTROS_VIALES_2019-2025.pdf`.
2. **Limpieza y exploración.** `notebooks/01_eda_limpieza.ipynb` unifica textos, deja el faltante como `SIN_DATO` y escribe `data/siniestros_hechos_limpio.csv`, con las mismas 65.818 filas. El relato de esa etapa está en `docs/analisis-datos.md`. Los gráficos de gravedad, año, modo, tipo de vía y hora quedan en `docs/figuras/01_` a `05_`.
3. **Feriados.** `notebooks/_calendario.py` marca cada fecha como día de semana, fin de semana o feriado nacional y arma `docs/figuras/07_calendario.png` y `docs/figuras/08_feriados_tasa.png`. Los JSON y CSV de feriados en `data/` son tablas auxiliares, no otra base de siniestros.
4. **Preprocesado.** `notebooks/02_preprocesamiento.ipynb` parte en entrenamiento y prueba, escala mes, día y hora, y arma las dummies. El hueco de hora no se imputa: `src/escala_hora.py` lo deja en el centro de la escala y agrega un indicador. La salida queda en `data/preprocesado/` (`pipeline.joblib`, `pesos_clase.json`, `columnas_finales.txt`). La matriz final tiene 54 columnas.
5. **Modelos.** `notebooks/03_modelos.ipynb` compara un piso que siempre dice leve, una regresión logística, un árbol y un random forest. Elige por recall macro. El ganador de la serie completa es el random forest. Las matrices están en `docs/figuras/06_matriz_*.png`. El resumen numérico está en `data/preprocesado/modelos.json`.
6. **Estructura del bosque.** En esa misma notebook, la sección «Estructura del modelo elegido» dibuja cómo está armado el random forest. El gráfico lo escribe `notebooks/_estructura_bosque.py` en `docs/diagramas/06_bosque.png`.
7. **Recortes de años.** El final de la notebook 03 repite el mismo esquema en 2022-2025 y en 2025 solo. Esas corridas no reemplazan el modelo guardado. Las figuras son `docs/figuras/09_` y `10_`.
8. **Diagramas del informe.** `docs/diagramas/` tiene el pipeline, los faltantes, el desbalance, los pesos de clase y la jerarquía leve-grave-mortal. Los `.mmd` se pasan a SVG con `docs/diagramas/render.mjs`.

## Cómo correrlo

Hace falta Python 3.12. Desde la raíz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

Después, en orden: `notebooks/01_eda_limpieza.ipynb`, `notebooks/02_preprocesamiento.ipynb`, `notebooks/03_modelos.ipynb`. El kernel tiene que ver la raíz del proyecto, porque el preprocesado importa `src.escala_hora`. Las notebooks ya agregan esa ruta si se abren desde la carpeta del proyecto.

`requirements.txt` fija pandas 3.1.0, matplotlib 3.11.2 y scikit-learn 1.9.1.
