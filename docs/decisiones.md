# Registro de decisiones

Cada decisión técnica del proyecto, con su motivo. Se actualiza en cada avance.

## Avance 1 · Hito 1 (Explorar) y Hito 2 (Datos) · 10 y 17-nov-2026

| # | Tema | Decisión | Motivo |
|---|---|---|---|
| D1 | Fecha oficial de cada fila | `fecha_reporte` = fecha del **nombre del archivo**; `last_update` se conserva solo como información | `last_update` es la hora de actualización de la fila y viene en varios formatos; el archivo define el corte diario |
| D2 | Unificación de esquemas | snake_case con un solo diccionario de renombres (`latitude→lat`, `longitude→long`, `incidence_rate→incident_rate`…); columnas que no existían ese día quedan nulas | Los 5 esquemas quedan en 17 columnas sin pérdida de filas (verificado: 4.287.473 filas en los CSV = en la tabla) |
| D3 | Linaje | Cada fila guarda `archivo_origen` y `fila_origen` | Permite decir de qué archivo y fila sale cualquier número (nivel excelente de R2) |
| D4 | Imputación | **No se imputa** en la capa limpia; los conteos quedan como decimales porque tienen nulos | *Imputar es inventar* |
| D5 | Capas y dónde viven | Cruda = CSV en el disco de la sesión de Colab (`/content/datos_crudos`, no va a git); limpia = Parquet; analítica = base SQLite. En Colab, limpia y analítica quedan en Drive | Requisito R1; el Parquet (gzip) ocupa 11 veces menos que el CSV unificado y se lee entre 3 y 7 veces más rápido |
| D6 | Persistencia en Colab | Los notebooks 01 a 07 montan Google Drive y guardan en `MyDrive/proyecto-gestion-datos-2026/data` | Cada notebook de Colab corre en una máquina distinta; así cada uno lee lo que dejó el anterior sin repetir la descarga |
| D7 | Motor del DW | **SQLite** (frente a MongoDB/NoSQL), con `to_sql` y `pd.read_sql` como en el taller de la S10 | Datos tabulares con esquema fijo tras unificar; JOIN y GROUP BY para el modelo en estrella; viene con Python. MongoDB conviene con esquemas variables y muchas escrituras (S4) |
| D8 | Homologación de países | Diccionario nombre original → país de la tabla UID (249 → 201); territorios de ultramar informados como país pasan a provincia de su país | Mismo país con varios nombres (`Mainland China`, `Korea, South`…) |
| D9 | Duplicados en territorio × día | Se conserva la **última** fila del archivo | Son repeticiones del mismo reporte (78 filas) |
| D10 | Acumulados que bajan | **Marcar** (`acum_baja` en `fact_covid`), no recalcular la historia | Recalcular sería inventar cómo se repartió la corrección |
| D11 | Archivo defectuoso 23-may-2022 | **Marcar** (`archivo_defectuoso`) y excluirlo de las series país × día | En ese reporte el acumulado baja en 136 países a la vez; explica casi toda la diferencia entre 158 países (reportes) y 84 (series) |
| D12 | Picos por rezago (casos) | Regla: nuevos > 5 × media de los 7 días previos y > 1.000, salvo que la semana previa tenga 4 o más días en 0 (reporte semanal); se **marcan** | Separa rezagos reales (Chile 17-jun-2020, +36 mil) del reporte semanal de 2022 |
| D13 | Nuevos al aparecer un territorio | El primer día de un territorio los nuevos quedan **nulos** | Evita picos falsos cuando Chile pasa de nacional a 16 regiones (20-may-2020) |
| D14 | Entidades especiales | Cruceros, JJ.OO. y Antártica se conservan pero se **excluyen** de rankings y tasas | No tienen población comparable |
| D15 | Coordenadas (0, 0) | Se anulan en `dim_territorio` | No son ubicaciones reales; romperían el mapa |
| D16 | P7 | Banco Mundial: % de población de 65 años o más vs. mortalidad por 100.000 | Elegida por el equipo; ver `docs/propuesta_P7.md` |
| D17 | Perfilado en Colab | `!pip install ydata-profiling` al inicio del 00; si aparece el error de NumPy: *Entorno de ejecución > Reiniciar la sesión y ejecutar todas las celdas* | `ydata-profiling` exige una versión de NumPy anterior a la de Colab; tras reiniciar, la sesión usa la instalada |
| D18 | Nivel del código | Notebooks al estilo del curso: `requests` en bucle, diccionario de renombres, reglas de calidad como lista `R` y `controla_calidad()` (S8), DW con sqlite3 (S10) | El código debe poder explicarlo cualquier integrante ante el Comité |
| D19 | Índice de calidad por país | 100 − % de días con algún problema (acumulado que baja, pico por rezago, fallecidos > casos, diferencia > 1 % con la serie, día sin reporte) | Base de P4; Corea del Norte es el peor (73,8) y Chile tiene 90,2 |

## Avance 2 · Hito 3 (Análisis) y entrega final · 24-nov-2026

| # | Tema | Decisión | Motivo |
|---|---|---|---|
| D20 | Serie para análisis | País × día y región de Chile × día desde los **acumulados** del DW (sin el archivo del 23-may-2022); nuevos = diferencia diaria; los negativos cuentan como 0 en la media móvil de 7 días | Totales nacionales consistentes aunque cambie la granularidad; no se inventa el reparto de las correcciones |
| D21 | Olas | Ola = incidencia de 7 días > 100 por 100.000 durante 14 días o más (bajas de menos de 14 días no cortan la ola) | Definición simple y reproducible; da 4 olas en Chile |
| D22 | Alerta temprana | Alza de la incidencia de 7 días > **30 %** frente a la semana anterior **y** ≥ **40 por 100.000**; umbral elegido en una calibración de 15 combinaciones con el criterio "todas las olas detectadas con el menor número de falsas alarmas" | Detecta las 4 olas de Chile (15, 3, 5 y 0 días de anticipación) con 3 falsas alarmas; con 50 % se pierden las olas que suben lento |
| D23 | Pronóstico | Tres modelos sobre la media móvil de 7 días (media móvil, tendencia log-lineal de 14 días, crecimiento semanal limitado a [0,5; 2]); evaluación con MAE y MAPE en 6 fechas de corte | Ningún modelo gana siempre; el de crecimiento semanal tiene el menor error promedio (MAPE 14,1 %) |
| D24 | Sin datos posteriores al corte | `alerta()` y `pronosticar()` filtran `fecha <= fecha_corte` antes de calcular; el tablero aplica las mismas funciones | Lo exige el desafío en vivo |
| D25 | Fuentes externas | Banco Mundial (API v2, año 2019: % 65+, PIB per cápita PPA, grupo de ingreso) y OWID (vacunación); cruce por ISO3 con corrección del código de Kosovo (XKS → XKX / OWID_KOS) | Dos fuentes integradas (nivel excelente de R3); 2019 es el último año previo a la pandemia |
| D26 | Vacunación faltante | Si un día falta el % de vacunados, se mantiene el **último valor conocido**; no se interpola | El % es acumulado: mantenerlo no inventa crecimiento |
| D27 | Nuevas tablas del DW | `dim_pais` (197 países con Banco Mundial e índice de calidad), `fact_vacunacion` (país × día) y `segmentacion_paises`, con conciliación | Las preguntas P3, P5 y P7 se responden desde el DW |
| D28 | Cargas de rezago en fallecidos | Días con fallecidos > 5 × media de los 7 días previos y > 500 se excluyen al comparar olas (P1) y meses (P3) | El 21-mar-2022 Chile sumó de una vez 11.447 fallecidos: no son muertes de ese día ni de ómicron |
| D29 | P3 | Letalidad mensual = fallecidos del mes ÷ casos del mes; meses con menos de 1.000 casos se excluyen; etapas por % con esquema completo (< 10 %, ≥ 70 %) | Razones estables y comparables; se advierte que testeo y variante también cambian |
| D30 | P7 | Países de 1 millón de habitantes o más, con datos del Banco Mundial e índice de calidad ≥ 80; Spearman y regresión con y sin control por log(PIB per cápita) | Excluye datos imposibles (Corea del Norte) y separa edad de riqueza |
| D31 | Segmentación (P5) | Curvas de incidencia semanal normalizadas por su máximo; k-means (k elegido por silueta = 4); países de 1 millón o más e índice ≥ 80 | Compara la forma de la pandemia, no el volumen de testeo |
| D32 | Control de divulgación (R6) | Conteos de 1 a 4 en territorios de menos de 100.000 habitantes se publican como "1–4" en el tablero; para condados se recomienda 5.000 y supresión complementaria | 5.000 oculta solo el 0,34 % de los fallecidos de EE.UU.; 100.000 ocultaría el 16 % |
| D33 | Tablero | Streamlit publicado en Streamlit Community Cloud desde `dashboard/app.py`; lee copias livianas de la capa limpia guardadas en `dashboard/` | Gratis, se actualiza solo con cada cambio en GitHub y no depende de Colab |
| D34 | `data/` en el repositorio | Se versionan la capa limpia (Parquet) y el DW **comprimido** (`covid_dw.db.gz`); los datos crudos no | El enunciado lo pide; GitHub no acepta archivos de más de 100 MB y el DW pesa ~190 MB sin comprimir |
