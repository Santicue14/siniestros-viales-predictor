# Análisis de los siniestros viales de CABA (2019-2025)

Documento de la exploración y la limpieza. El detalle reproducible está en `notebooks/01_eda_limpieza.ipynb` y el archivo limpio en `data/siniestros_hechos_limpio.csv`. El preprocesado sigue en `notebooks/02_preprocesamiento.ipynb` y los tres modelos en `notebooks/03_modelos.ipynb`.

## Qué pide la consigna, y qué no

El trabajo de Inteligencia de negocios (LGTI, UNPAZ, 2026) pide un CSV de al menos 5 MB y un problema de clasificación. La frase de antigüedad está en el estado del arte: hacen falta al menos tres referencias en APA y **solo una puede tener más de 3 años**. Esa regla es de la bibliografía del informe, no del dataset.

Entrega escrita: viernes 6/11/2026, 23:59. El PDF de la consigna menciona la oral el 10/11 a las 18:00 y también el 12/11. Conviene confirmar esa fecha con la cátedra.

El dataset de la cursada, si este mismo archivo se usó como ejemplo en clase, no se puede presentar. Esta versión es la base 2019-2025 publicada por el observatorio de la Ciudad, distinta de los recortes de homicidios que suelen cortar en 2021. Igual hay que chequearlo contra los ejemplos vistos en la materia.

## Por qué esta base

Se usa el CSV de **hechos** del Observatorio de Movilidad y Seguridad Vial de la Ciudad de Buenos Aires. Una fila es un siniestro. Cubre del 1/1/2019 al 31/12/2025, pesa 12.198.322 bytes y el portal lo actualizó el 29/06/2026.

| Recurso | Dónde está |
| --- | --- |
| Ficha | https://data.buenosaires.gob.ar/dataset/victimas-siniestros-viales |
| Hechos (CSV) | https://cdn.buenosaires.gob.ar/datosabiertos/datasets/transporte-y-obras-publicas/victimas-siniestros-viales/siniestros_viales_hechos.csv |
| Notas 2019-2025 (PDF) | https://cdn.buenosaires.gob.ar/datosabiertos/datasets/transporte-y-obras-publicas/victimas-siniestros-viales/NOTAS_SINIESTROS_VIALES_2019-2025.pdf |
| Copia local y fecha de descarga | `data/ORIGEN.txt` (descargado el 26/10/2026) |

Otras fuentes que se miraron y no cierran esta pregunta:

- La ANSV publica anuarios e informes 2023-2026 en PDF. El microdato nacional (SIGISVI) no es abierto.
- El Sistema de Alerta Temprana, en datos.gob.ar, trae muertes viales hasta 2024. No trae los siniestros que solo dejaron heridos.
- El CSV de víctimas de la misma ficha de CABA tiene edad y sexo, pero pesa 4,1 MB y no llega solo al mínimo de 5 MB. Queda para una etapa posterior.
- AUSA publica siniestros de autopistas hasta 2026. Es un universo más chico que el de toda la Ciudad.

La fuente de las notas es policial: lesiones culposas y homicidios culposos. La gravedad grave sale del relevamiento de hospitales de agudos (internación de al menos 24 horas). Los mortales se arman con varias fuentes (SAME, AUSA, hospitales, fiscalías, entre otras) y el criterio es el de los 30 días.

## Definiciones que se adoptan

Tomadas de las notas oficiales:

- **Siniestro vial con víctimas:** hecho de tránsito con al menos un vehículo en movimiento, en una vía de acceso público, con al menos una persona herida o muerta. No entran los hechos solo con daños materiales ni los suicidios.
- **Mortal:** la persona fallece dentro de los 30 días por causas atribuibles al hecho.
- **Grave:** la lesión exigió hospitalización de al menos 24 horas.
- **Leve:** menos de 24 horas de internación, o sin traslado sanitario.
- Si hay varias víctimas, el siniestro se clasifica por la **máxima** gravedad.
- **Víctima** (modo de desplazamiento): quién resultó herido o murió. **Contraparte:** el otro vehículo señalado en la fuente, sin que eso sea una culpabilidad legal.
- `SD` quiere decir sin dato.

## Diccionario de columnas

El CSV original tiene 21 columnas, separadas por `;`. Después de la limpieza se agrega `es_mortal` (22 columnas).

| Columna | Qué es |
| --- | --- |
| `id_siniestro` | Identificador. El prefijo `HC` es homicidio culposo y `LC` es lesión culposa. |
| `numero_total_de_victimas` | Cantidad de víctimas del hecho. |
| `numero_victimas_leve_siniestro` | Víctimas leves. |
| `numero_victimas_grave_siniestro` | Víctimas graves. |
| `numero_victimas_mortal_siniestro` | Víctimas mortales. |
| `fecha_siniestro` | Fecha del hecho. |
| `anio_siniestro`, `mes_siniestro`, `dia_siniestro` | Partes de la fecha. |
| `hora_siniestro` | Hora `HH:MM:SS`. |
| `rango_horario` | Hora entera, de 0 a 23. |
| `direccion_normalizada_siniestro` | Dirección normalizada. |
| `comuna_siniestro` | Comuna 1 a 15. |
| `tipo_de_via_siniestro` | Avenida, calle, autopista, Av. Gral. Paz. |
| `geocodificacion_plana` | Punto en coordenadas planas de la Ciudad. |
| `longitud_siniestro`, `latitud_siniestro` | Coordenadas WGS84. |
| `participantes_siniestro` | Modo de la víctima y contraparte, unidos con un guion. |
| `modo_desplazamiento_victima` | Auto, moto, peatón, bicicleta, transporte público, etc. |
| `contraparte_siniestro` | El otro participante. Incluye `OBJETO FIJO` y `MULTIPLE`. |
| `gravedad_siniestro` | `LEVE`, `GRAVE` o `MORTAL`. |
| `es_mortal` | 1 si la gravedad es `MORTAL`, 0 si es `LEVE` o `GRAVE`. La crea esta etapa. |

## Variable objetivo

La pregunta del trabajo es si el siniestro fue leve, grave o mortal. La etiqueta es `gravedad_siniestro`.

`es_mortal` queda en el archivo limpio como el corte de arriba de esa escala: 1 si es `MORTAL` y 0 si es `LEVE` o `GRAVE`. El clasificador no la usa.

Sobre 65.818 hechos hay **62.174 leves (94,5 %)**, **2.955 graves (4,5 %)** y **689 mortales (1,0 %)**. Predecir siempre «leve» acertaría el 94,5 % y no encontraría ningún grave ni ninguna muerte. El número que importa es el recall de los tres niveles, no el acierto global.

Los 31 hechos publicados como `LEVE` que igual tienen un conteo de víctimas graves siguen como `LEVE`. No se reescribió la etiqueta oficial.

## Calidad del archivo original

65.818 filas, 21 columnas, ningún id duplicado ni vacío. El prefijo parte el archivo en 65.129 `LC` y 689 `HC`, y esa partición coincide exactamente con mortal / no mortal.

No hay celdas nulas de pandas. Lo que falta está vacío o dice `SD`.

| Columna | Vacíos | `SD` | `#¡REF!` |
| --- | ---: | ---: | ---: |
| Total de víctimas | 0 | 3.276 | 0 |
| Hora y rango horario | 77 | 4 | 0 |
| Dirección | 12.900 | 729 | 0 |
| Comuna | 3.017 | 535 | 0 |
| Tipo de vía | 12.227 | 315 | 0 |
| Geocodificación plana | 2.367 | 7 | 0 |
| Latitud y longitud | 2.378 | 652 | 1 |
| Modo de la víctima | 0 | 10.928 | 1 |
| Contraparte | 0 | 14.066 | 1 |

El `#¡REF!` es una sola fila, `LC-2025-0771825` (leve). El error de Excel está en el modo, la contraparte, los participantes y las dos coordenadas.

Otros problemas:

- 9.406 fechas no traen el mes o el día con dos dígitos (`2025-9-9` junto a `2019-01-01`). El rango real, ya parseado, va del 1/1/2019 al 31/12/2025. 2025 está completo, con hechos en los doce meses.
- `HC-2025-0908572` tiene fecha 28/11/2025 y día 29.
- La comuna viene como `Comuna 1`, `COMUNA 1` o `1`.
- 149 contrapartes están en minúscula (`auto`, `moto`, `camion`, `taxi`, `movil`, `peaton`) y arrastran el mismo problema a `participantes_siniestro`.
- 3.276 totales de víctimas dicen `SD`. Todos son de 2025 y, en los tres conteos, suman 1.
- Dos totales no cierran con la suma de las partes: `LC-2025-0111680` dice 4 y tiene 5 leves; `HC-2025-0639058` dice 2 y tiene 1 mortal.
- 31 hechos están etiquetados `LEVE` aunque el conteo de graves es mayor que cero: 23 de 2020 y 8 de 2024. Según las notas, debería ganar la gravedad máxima. Se deja constancia y no se cambia la etiqueta.
- 135 direcciones tienen un `?` donde faltó una letra (en general la eñe). No se reescriben: corregirlas sería adivinar el nombre de la calle.
- `CAMIONETA` aparece 74 veces como contraparte. Las notas meten camionetas y pick-ups dentro de `UTILITARIO`. No se unificó.

El faltante no se reparte igual entre mortales y el resto. En modo de la víctima, tipo de vía y comuna, **ningún hecho mortal está vacío**. En la contraparte faltan 10 mortales. En la hora falta 1 mortal. En la dirección y en la latitud faltan 3 mortales.

| Columna | Faltantes entre mortales | Faltantes entre no mortales |
| --- | ---: | ---: |
| Modo de la víctima | 0 | 10.929 |
| Contraparte | 10 | 14.057 |
| Tipo de vía | 0 | 12.542 |
| Comuna | 0 | 3.552 |
| Hora | 1 | 80 |
| Dirección | 3 | 13.626 |
| Latitud | 3 | 3.028 |

## Reglas de limpieza

No se descartó ninguna fila. Siguen siendo 65.818.

- Se recortan espacios, tabulaciones y espacios duros.
- Tipo de vía, modo, contraparte, participantes y gravedad pasan a mayúsculas. Vacío, `SD` y `#¡REF!` pasan a `SIN_DATO`. Un valor como `SD-AUTO` se conserva, porque una de las dos partes está informada.
- La comuna queda en `Comuna 1` … `Comuna 15`, o `SIN_DATO`.
- Si el total de víctimas es `SD` y las tres partes suman un número, se completa con esa suma. Fueron 3.276 filas, todas con total 1.
- Los dos totales que no cierran se dejan como vinieron.
- La fecha queda en `AAAA-MM-DD`. En `HC-2025-0908572` manda la fecha completa y el día pasa de 29 a 28.
- Hora vacía, `SD` o `#¡REF!` queda como nulo en `rango_horario` (81 filas) y como `SIN_DATO` en el texto de la hora. Latitud y longitud quedan en nulo en los mismos casos (3.031 filas).
- Se agrega `es_mortal`. La gravedad original sigue en el archivo.

Filas alcanzadas por al menos una de esas reglas: **36.579**. Filas que ya venían prolijas: **29.239**. El desglose no suma 36.579 porque una fila puede entrar en más de un ítem:

- Comuna reescrita: 14.824
- Fecha pasada a `AAAA-MM-DD`: 9.406
- Total `SD` reconstruido: 3.276
- Espacios o tabulaciones recortados: 5
- Día corregido: 1

El CSV limpio pesa 12.810.312 bytes, sigue en `;` y en UTF-8 con BOM, para que abra bien en Excel. Supera los 5 MB de la consigna.

## Qué muestra el EDA

### La clase mortal es muy chica

![Distribución de la gravedad](figuras/01_gravedad.png)

De 65.818 hechos, 62.174 son leves (94,5 %), 2.955 graves (4,5 %) y 689 mortales (1,0 %). El gráfico está en esa escala a propósito: graves y mortales casi no se ven al lado de los leves.

### 2020 baja el volumen, no los muertos

![Hechos y hechos mortales por año](figuras/02_fatales_por_anio.png)

| Año | Hechos | Mortales | Tasa |
| --- | ---: | ---: | ---: |
| 2019 | 10.155 | 103 | 1,01 % |
| 2020 | 6.061 | 79 | 1,30 % |
| 2021 | 7.818 | 96 | 1,23 % |
| 2022 | 9.536 | 107 | 1,12 % |
| 2023 | 9.927 | 104 | 1,05 % |
| 2024 | 10.569 | 110 | 1,04 % |
| 2025 | 11.752 | 90 | 0,77 % |

En 2020 hay unos 4.000 hechos menos que en 2019. Encaja con la caída de movilidad de la pandemia y hay que tenerlo en cuenta si más adelante se usa la serie completa. Los mortales, en cambio, se mantienen entre 79 y 110 por año. 2025 es el año con más hechos y con la tasa más baja.

### Moto en cantidad, peatón en tasa

![Tasa mortal según el modo de la víctima](figuras/03_modo_desplazamiento.png)

| Modo | Hechos | Mortales | Tasa |
| --- | ---: | ---: | ---: |
| Moto | 24.555 | 285 | 1,16 % |
| Peatón | 9.415 | 269 | 2,86 % |
| Auto | 7.073 | 56 | 0,79 % |
| Bicicleta | 7.091 | 54 | 0,76 % |
| Utilitario | 697 | 8 | 1,15 % |
| Transporte público | 3.633 | 6 | 0,17 % |
| Camión | 250 | 4 | 1,60 % |
| Móvil | 531 | 3 | 0,56 % |
| Mixto | 498 | 2 | 0,40 % |
| Taxi | 810 | 1 | 0,12 % |
| Monopatín | 207 | 1 | 0,48 % |
| Sin dato | 10.929 | 0 | 0 % |
| Otro | 129 | 0 | 0 % |

La moto aporta la mayor cantidad de hechos mortales. El peatón, con menos hechos, tiene una tasa más alta. El transporte público y el taxi casi no aparecen entre los mortales. Los 10.929 sin modo son todos no mortales.

### La autopista concentra riesgo, la calle concentra volumen

![Tasa mortal según el tipo de vía](figuras/04_tipo_de_via.png)

| Tipo de vía | Hechos | Mortales | Tasa |
| --- | ---: | ---: | ---: |
| Avenida | 30.525 | 419 | 1,37 % |
| Calle | 18.794 | 146 | 0,78 % |
| Sin dato | 12.542 | 0 | 0 % |
| Av. Gral. Paz | 2.916 | 54 | 1,85 % |
| Autopista | 1.041 | 70 | 6,72 % |

La autopista tiene pocos hechos y una tasa varias veces mayor que la calle. La avenida reúne la mayoría de los mortales en números absolutos (419). Los 12.542 sin tipo de vía, otra vez, no incluyen ningún mortal.

### De madrugada hay pocos siniestros y una tasa más alta

![Hechos y tasa mortal según la hora](figuras/05_franja_horaria.png)

La hora 17 es la de mayor volumen (4.748 hechos) y la tasa de la tarde queda cerca del 0,6 %. Entre las 3 y las 5 la cantidad baja y la tasa sube: 5,71 % a las 3, 5,07 % a las 4 y 4,11 % a las 5. Hay 81 hechos sin hora; uno es mortal.

### Feriado, fin de semana y día de semana

![Hechos por día y tasa mortal según el calendario](figuras/07_calendario.png)

La lista de feriados nacionales está en `data/feriados_nacionales_2019-2025.csv`. De 2021 a 2025 sale de `https://api.argentinadatos.com/v1/feriados/{año}`, el mismo recurso que `curl -L https://api.argentinadatos.com/v1/feriados/2026`. 2019 y 2020 devuelven 404: el repositorio de la API publica feriados desde 2021. Esos dos años se reconstruyen con la regla de traslado (martes y miércoles al lunes anterior, jueves y viernes al lunes siguiente), contrastada contra las fechas de 2021-2025, más los tres puentes turísticos de cada año. 2026 no tiene filas en el archivo de hechos.

Un feriado que cae sábado o domingo se cuenta como feriado. El fin de semana del gráfico es sábado o domingo que no es feriado. El día de semana es lunes a viernes que no es feriado. Así las tres barras cubren todos los días del año.

| Tipo de día | Días | Hechos | Hechos por día | Mortales | Tasa |
| --- | ---: | ---: | ---: | ---: | ---: |
| Día de semana | 1.719 | 50.481 | 29,4 | 484 | 0,96 % |
| Fin de semana | 702 | 13.119 | 18,7 | 174 | 1,33 % |
| Feriado | 136 | 2.218 | 16,3 | 31 | 1,40 % |

Ese orden de volumen se repite en los siete años: el día de semana arriba, el feriado abajo. 2020 baja las tres series (19,2, 11,6 y 9,0 hechos por día) y no lo cambia. El feriado no concentra más siniestros. Concentra menos.

La tasa mortal va en el otro sentido de 2019 a 2024: el fin de semana queda por encima del día de semana, y el feriado suele quedar más arriba todavía. El feriado suma 31 muertes en toda la serie, entre 2 y 6 por año. En 2020 son 5 muertes en 171 hechos (2,92 %) y en 2024 son 2 en 364 (0,55 %). Con tan pocos casos, un año no alcanza para decir que el feriado sea más letal. El fin de semana sí sostiene la diferencia hasta 2024 (174 muertes). En 2025 la tasa del fin de semana baja a 0,63 % y la del día de semana queda en 0,79 %.

La tabla año por año está en `data/calendario_por_anio.csv`. El armado está en `notebooks/_calendario.py`.

### Qué feriado pesa más

![Tasa mortal y hechos por día de cada feriado](figuras/08_feriados_tasa.png)

Cada barra junta las siete fechas de ese feriado (Carnaval, catorce, porque son dos días por año). La línea punteada es la tasa del día de semana, 0,96 %. En rojo, el feriado que la supera. El 2 de abril de 2021 fue Viernes Santo y Día de Malvinas a la vez: la API lo publica como Viernes Santo y el día entra una sola vez. Tuvo 15 hechos y ninguna muerte.

| Feriado | Días | Hechos | Por día | Muertes | Tasa |
| --- | ---: | ---: | ---: | ---: | ---: |
| Soberanía Nacional | 7 | 112 | 16,0 | 6 | 5,36 % |
| Belgrano | 7 | 129 | 18,4 | 6 | 4,65 % |
| Navidad | 7 | 74 | 10,6 | 2 | 2,70 % |
| Viernes Santo | 7 | 94 | 13,4 | 2 | 2,13 % |
| Inmaculada | 7 | 146 | 20,9 | 3 | 2,05 % |
| Revolución de Mayo | 7 | 108 | 15,4 | 2 | 1,85 % |
| Independencia | 7 | 133 | 19,0 | 2 | 1,50 % |
| Año Nuevo | 7 | 87 | 12,4 | 1 | 1,15 % |
| Carnaval | 14 | 181 | 12,9 | 0 | 0 % |
| Memoria, Verdad y Justicia | 7 | 126 | 18,0 | 0 | 0 % |
| Puente turístico | 23 | 415 | 18,0 | 3 | 0,72 % |

Soberanía tiene una muerte en seis de los siete años, no un solo año extremo. Belgrano tiene dos muertes en 2019, 2021 y 2022, y ninguna en los otros cuatro. Las dos muertes de Navidad son de 2020, el año de menos movilidad. Carnaval, con 181 hechos en catorce días, no tiene ninguna muerte. Memoria tampoco, en 126 hechos. El puente turístico, que es el grupo más largo, queda por debajo de la tasa del día de semana.

La tabla completa, con Güemes, San Martín, Malvinas, Diversidad cultural y los feriados de un solo año, está en `data/feriados_por_nombre.csv`.

### Comunas

Después de unificar el formato, la comuna 8 tiene la tasa más alta (64 mortales en 3.088 hechos, 2,07 %) y la comuna 4 la mayor cantidad (75). La comuna 1 es la de más hechos (7.241) y 74 mortales. `SIN_DATO` suma 3.552 hechos y ningún mortal. La tabla completa sale de la notebook.

## Qué no puede entrar en un modelo

Estas columnas se guardan en el CSV limpio para poder auditarlas. No sirven como entrada:

- `gravedad_siniestro` es la etiqueta.
- `numero_victimas_mortal_siniestro`, `numero_victimas_grave_siniestro` y `numero_victimas_leve_siniestro` alcanzan para reconstruirla.
- El prefijo de `id_siniestro` también es la etiqueta: en este archivo, `HC` es mortal y `LC` no lo es, sin excepciones.

`numero_total_de_victimas` no determina solo si el hecho fue mortal. Conviene probarlo como variable y también dejarlo afuera, porque puede dominar al resto.

`SIN_DATO` en el modo, el tipo de vía y la comuna no aparece entre los mortales. Si entra como categoría, el modelo puede estar leyendo qué tan completo quedó el sumario, no las circunstancias del siniestro. Los registros `HC` están mejor completos que los `LC`.

Candidatas razonables para una primera versión, todas del hecho y no de la etiqueta: mes, día, hora, comuna, tipo de vía, modo de la víctima y contraparte. `participantes_siniestro` repite el modo y la contraparte. La dirección y las coordenadas sirven para ubicar el hecho; como categoría de texto, la dirección tiene demasiados valores distintos.

## Decisiones que quedan abiertas

- Usar 2019-2025 completo. Recortar a 2023-2025 dejaría unos 300 mortales. El bache de 2020 hay que comentarlo, no esconderlo.
- No reescribir los 31 leves que tienen conteo de graves, hasta decidir si se confía más en la etiqueta o en los conteos.
- No pasar `CAMIONETA` a `UTILITARIO` sin revisarlo.
- No imputar el modo, la vía ni la comuna cuando dicen `SIN_DATO`.
- Edad y sexo están en el CSV de víctimas (varias filas por hecho). Cruzarlos es una línea posterior, no un requisito de esta limpieza.

## Dónde sigue

La matriz y el peso de clase están en `notebooks/02_preprocesamiento.ipynb`. Las matrices de confusión y el reporte de clasificación están en `notebooks/03_modelos.ipynb`. El informe de la materia es `docs/informe.pdf`.
