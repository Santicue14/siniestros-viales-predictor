---
marp: true
theme: default
paginate: true
size: 16:9
lang: es
style: |
  section { font-size: 24px; }
  h1 { font-size: 40px; }
  h2 { font-size: 30px; }
  img { max-height: 400px; }
  table { font-size: 18px; }
---

# Gravedad de los siniestros viales en CABA
## 2019-2025

Santiago Baldini Cuevas
Inteligencia de negocios 2026 · UNPAZ

El análisis, el código y estas diapositivas se hicieron con el modelo Grok 4.7.

---

## Cómo se recorre el trabajo

1. De dónde sale el archivo y qué notebook lo lee.
2. Qué midió ese código: conteos y tasas.
3. Qué se hizo con cada medida.
4. Qué modelo quedó, mirando los tres niveles.

El número que se elige es el recall macro: el promedio del recall de leve, grave y mortal. El acierto global queda como piso.

---

## De dónde sale cada número

`data/ORIGEN.txt` anota la descarga del 26/10/2026.

El CSV de hechos del Observatorio de Movilidad y Seguridad Vial pesa 12,2 MB. Una fila es un siniestro.

- `notebooks/01_eda_limpieza.ipynb` limpia y escribe los gráficos.
- `notebooks/02_preprocesamiento.ipynb` arma la matriz.
- `notebooks/03_modelos.ipynb` ajusta los modelos y escribe las matrices.

Ficha: data.buenosaires.gob.ar/dataset/victimas-siniestros-viales

---

## La gravedad es una escala

Una fila puede tener leves, graves y mortales a la vez. La etiqueta publicada es el máximo:

1. Si hay una muerte, el hecho es MORTAL.
2. Si no hay muerte y hay un grave, es GRAVE.
3. Si no, es LEVE.

Mortal: muerte dentro de los 30 días. Grave: internación de al menos 24 horas.

62.174 leves, 2.955 graves, 689 mortales. El 1 % es el nivel de arriba de esa escala.

---

## Cómo se resuelve para clasificar

La etiqueta que entra al modelo es el máximo: LEVE, GRAVE o MORTAL.

- No se usa un número 0, 1, 2. Esos escalones no están a la misma distancia: 94,5 %, 4,5 % y 1 %.
- No se usa un corte binario. Juntar leve y grave deja el nivel del medio sin respuesta.
- scikit-learn lee los tres nombres como clases distintas. No impone el orden de la escala. Ese orden queda en cómo se arma la etiqueta.

![h:220](diagramas/05_jerarquia.svg)

Los 31 leves con un conteo de graves se dejan como vinieron. Los conteos y el prefijo HC repiten la escala, y quedan afuera.

---

## Para qué sirve

De un hecho ya ocurrido, con la hora, la comuna, la vía, el modo y la contraparte: ¿fue leve, grave o mortal?

Sirve para ver qué combinaciones concentran cada nivel. La contraparte es el otro vehículo que figura en la fuente.

---

## Tres lecturas, y el diseño que sale de ellas

Ali, Hussain y Haque (2024) piden tratar el desbalance de la gravedad con una técnica explícita.

Hamdan y Sipos (2025) encuentran random forest entre los modelos más usados, y que la vía y el usuario cambian la gravedad.

Butt y Shafique (2025) ubican la utilidad en la gestión: dónde intervenir.

Las fichas APA están en el PDF. Los datos oficiales se citan aparte, como fuente.

---

## Primera medida: casi todo es leve

![w:860](figuras/01_gravedad.png)

62.174 leves, 2.955 graves, 689 mortales. El gráfico es un conteo. Decir siempre «leve» acertaría el 94,5 %.

---

## 2020 baja los hechos

![w:980](figuras/02_fatales_por_anio.png)

A la izquierda, hechos. A la derecha, hechos mortales. En 2020 hay 6.061 hechos, contra 10.155 en 2019. Los mortales se mantienen entre 79 y 110. En 2025 la tasa es 0,77 %.

---

## Moto en cantidad, peatón en tasa

![w:820](figuras/03_modo_desplazamiento.png)

El eje es una tasa. El peatón está en 2,86 % (269 mortales). La moto está en 1,16 % y aporta 285. `SIN_DATO` queda en cero: 10.929 hechos, ninguno mortal.

---

## La autopista concentra la tasa

![w:860](figuras/04_tipo_de_via.png)

1.041 hechos en autopista, tasa 6,72 %. La calle queda en 0,78 %. Otra vez `SIN_DATO` en cero.

---

## La tarde tiene volumen y poca tasa

![w:1000](figuras/05_franja_horaria.png)

A la izquierda, el conteo. A la derecha, la tasa. A las 3, en el entrenamiento, la tasa es 6,37 %. A las 14 es 0,95 %. La media de la hora es 13,64. Cae en la tarde.

---

## El feriado tiene menos hechos por día

![w:1000](figuras/07_calendario.png)

Día de semana: 29,4 hechos por día. Fin de semana: 18,7. Feriado: 16,3. El orden se repite en los siete años.

La tasa mortal queda en 0,96 %, 1,33 % y 1,40 %. En el feriado son 31 muertes en toda la serie.

---

## Qué feriado pesa más

![h:400](figuras/08_feriados_tasa.png)

La línea es el 0,96 % del día de semana. Soberanía: 6 muertes en 112 hechos, 5,36 %. Belgrano: 6 en 129, 4,65 %.

Carnaval no tiene ninguna muerte en 181 hechos. Memoria tampoco, en 126. Navidad es el más quieto: 10,6 hechos por día.

---

## Qué se hizo con esa hora

![w:780](diagramas/02_faltantes.svg)

La media 13,64 no se copia en el hueco: le inventaría una hora de baja tasa. Se guarda `hora_faltante`. El 0 de la escala es el centro, no las 14. Hay 81 horas vacías. Una es un hecho mortal.

---

## Qué se hizo con el 1 %

![h:320](diagramas/03_desbalance.svg)

62.174 leves, 2.955 graves y 689 mortales. La tajada mortal es el 1 %.

---

## El peso conserva las filas

![h:250](diagramas/04_pesos.svg)

Peso en el entrenamiento: leve 0,35, grave 7,42 y mortal 31,85. Igualar los tres niveles al más chico tiraría 63.751 filas.

---

## Cómo quedó armada la matriz

![w:500](diagramas/01_pipeline.svg)

80/20 estratificado por los tres niveles, semilla 42, antes de calcular medias. Prueba: 12.435 leves, 591 graves y 138 mortales. El escalador no se reajusta en la prueba. La matriz tiene 54 columnas.

---

## Cómo se lee la matriz

Filas: lo que pasó. Columnas: lo que dijo el modelo. El orden de las dos es leve, grave, mortal.

La diagonal son los aciertos de cada nivel.

El recall macro es el promedio de los tres recall. Ese promedio elige el modelo. El acierto no.

---

## El piso, en la misma prueba

![w:520](figuras/06_matriz_siempre_leve.png)

Acierto 94,5 %. Encuentra los 12.435 leves y 0 graves y 0 muertes. Este es el modelo que gana si se mira el acierto.

---

## Los tres modelos

| Modelo | Acierto | Recall macro | Recall grave | Recall mortal |
| --- | ---: | ---: | ---: | ---: |
| Siempre leve | 94,5 % | 33,3 % | 0 % | 0 % |
| Logística | 59,2 % | 61,7 % | 50,3 % | 75,4 % |
| Árbol, profundidad 5 | 65,7 % | 57,3 % | 19,3 % | 84,8 % |
| Forest, 200 árboles | 54,8 % | 62,1 % | 46,7 % | 84,8 % |

Peso de clase y semilla 42 en los tres. El árbol pide 20 filas por hoja. El forest, 10.

---

## Logística

![w:500](figuras/06_matriz_regresion_logistica.png)

Encuentra 297 de 591 graves y 104 de 138 muertes. Llama leves a 12 muertes. Recall macro 61,7 %.

---

## El árbol empata las muertes y se cae en el grave

![w:500](figuras/06_matriz_arbol.png)

Encuentra 117 de 138 muertes, igual que el forest, y solo 114 de 591 graves. Recall del grave 19,3 %. Recall macro 57,3 %.

---

## El elegido: random forest

![w:500](figuras/06_matriz_random_forest.png)

Recall macro 62,1 %, el más alto. Encuentra 117 de 138 muertes y 276 de 591 graves. De las 21 muertes que no nombra como mortales, 15 quedan como graves y 6 como leves.

---

## Tres conclusiones

1. El piso acierta el 94,5 % y no encuentra ni un grave ni una muerte. El acierto premia ese resultado.
2. El random forest sostiene los tres niveles: recall 54,8 % en leve, 46,7 % en grave y 84,8 % en mortal.
3. Parte del error se mueve al nivel de al lado. La precisión de grave y de mortal sigue siendo baja.

---

## Tres dificultades

1. El desbalance. Sin el peso, el ajuste se va a los 49.739 leves del entrenamiento.
2. `SIN_DATO` en modo, vía y comuna no aparece entre los mortales. Puede estar leyendo el sumario.
3. La hora es circular y 2020 tiene poca movilidad. Hay además 31 leves con un conteo de graves, dejados como vinieron.

---

## Tres líneas futuras

1. Cruzar edad y sexo desde el CSV de víctimas.
2. Probar el total de víctimas, y repetir la prueba sin él.
3. Codificar la hora con seno y coseno, y evaluar 2024-2025 entrenando hasta 2023.

---

## Cierre

Santiago Baldini Cuevas
Inteligencia de negocios · UNPAZ · 2026

El análisis de los datos, el código de las notebooks y esta presentación se hicieron con el modelo de IA Grok 4.7.

El documento escrito, con las secciones de la consigna, está en `docs/informe.pdf`.
