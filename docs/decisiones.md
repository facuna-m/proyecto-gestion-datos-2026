# Registro de decisiones

Cada decisión técnica del proyecto, con su motivo. Se actualiza en cada avance.

## Avance 1 · Hito 1 (Explorar) y Hito 2 (Datos) · 10-nov-2026

| # | Tema | Decisión | Motivo |
|---|---|---|---|
| D1 | Fecha oficial de cada fila | `fecha_reporte` = fecha del **nombre del archivo**; `last_update` se conserva solo como información | `last_update` es la hora de actualización de la fila y viene en ≥ 4 formatos; el archivo define el corte diario |
| D2 | Unificación de esquemas | snake_case + renombres `latitude→lat`, `longitude→long`, `incidence_rate→incident_rate`; columnas inexistentes quedan nulas | Los 5 esquemas quedan en 18 columnas sin pérdida de filas (verificado: 4.287.473 filas en CSV = en Parquet) |
| D3 | Linaje | Cada fila guarda `archivo_origen` y `fila_origen` | Permite decir de qué archivo y fila sale cualquier número (nivel excelente de R2) |
| D4 | Imputación | **No se imputa** en la capa limpia: conteos como enteros *nullable* | *Imputar es inventar* |
| D5 | Capas y dónde viven | Cruda = CSV en el disco de la sesión de Colab (`/content/datos_crudos`, no va a git); limpia = Parquet en Drive; analítica = base SQLite en Drive | Requisito R1; el Parquet (gzip) ocupa ~10 veces menos que el CSV y se lee ~7 veces más rápido |
| D6 | Persistencia en Colab | Notebooks 01–03 montan Google Drive y guardan en `MyDrive/proyecto-gestion-datos-2026/data` | Cada notebook de Colab corre en una máquina distinta; así 02 y 03 leen lo que dejó 01 sin repetir la descarga |
| D7 | Motor del DW | **SQLite** (frente a MongoDB/NoSQL), con `to_sql` y `pd.read_sql` como en el taller de la S10 | Datos tabulares con esquema fijo tras unificar; JOIN y GROUP BY para el modelo en estrella; viene con Python. MongoDB conviene con esquemas variables y muchas escrituras (S4) |
| D8 | Homologación de países | Tabla manual nombre original → país de la tabla UID → ISO3 (249 → 201); territorios de ultramar informados como país pasan a provincia de su país soberano | Mismo país con varios nombres (`Mainland China`, `Korea, South`…); la llave del DW no puede ser el nombre |
| D9 | Duplicados en territorio × día | Se conserva la **última** fila del archivo | Son repeticiones del mismo reporte (78 filas) |
| D10 | Acumulados que bajan | **Marcar** (`flag_acum_baja`), no recalcular la historia | Recalcular sería inventar cómo se repartió la corrección |
| D11 | Archivo defectuoso 23-may-2022 | **Marcar** (`flag_archivo_defectuoso`) | En ese reporte el acumulado baja en 136 países a la vez; explica casi toda la diferencia entre 158 países (reportes) y 84 (series) |
| D12 | Picos por rezagos | Regla: nuevos > 5× promedio de 28 días previos y > 1.000, salvo régimen de reporte semanal; se **marcan** | Separa rezagos reales (Chile 17-jun-2020, +36 mil) del reporte semanal de 2022 |
| D13 | Nuevos al aparecer un territorio | El primer día de un territorio los nuevos quedan **nulos** | Evita picos falsos cuando Chile pasa de nacional a 16 regiones (20-may-2020); los totales nacionales se calculan agregando acumulados |
| D14 | Entidades especiales | Cruceros, JJ.OO. y Antártica se conservan pero se **excluyen** de rankings y tasas | No tienen población comparable |
| D15 | Coordenadas (0, 0) | Se anulan en `dim_territorio` | No son ubicaciones reales; romperían el mapa |
| D16 | P7 | Banco Mundial: % de población ≥ 65 años vs. mortalidad por 100.000 | Elegida por el equipo; ver `docs/propuesta_P7.md` |
| D17 | Perfilado en Colab | `!pip install ydata-profiling` al inicio del 00; si aparece el error de NumPy: *Entorno de ejecución > Reiniciar la sesión y ejecutar todas las celdas* | `ydata-profiling` exige NumPy < 2.4 y Colab trae 2.4: tras reiniciar, la sesión usa la versión instalada. Verificado en Colab el 17-nov-2026 |
| D18 | Nivel del código | Notebooks reescritos al estilo del curso: `requests` en bucle, diccionario de renombres, reglas de calidad como lista `R` y `controla_calidad()` (S8), DW con sqlite3 (S10) | El código debe poder explicarlo cualquier integrante ante el Comité |
| D19 | Índice de calidad por país | 100 − % de días con algún problema (acumulado que baja, pico por rezago, fallecidos > casos, diferencia > 1 % con la serie, día sin reporte) | Base de P4; Corea del Norte es el peor (73,8) y Chile tiene 90,2 por las diferencias con la serie antes del 17-jun-2020 |
