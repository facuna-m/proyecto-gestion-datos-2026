# Registro de decisiones

Cada decisión técnica del proyecto, con su motivo. Se actualiza en cada avance.

## Avance 1 · Hito 1 (Explorar) y Hito 2 (Datos) · 10-nov-2026

| # | Tema | Decisión | Motivo |
|---|---|---|---|
| D1 | Fecha oficial de cada fila | `fecha_reporte` = fecha del **nombre del archivo**; `last_update` se conserva solo como información | `last_update` es la hora de actualización de la fila y viene en ≥ 4 formatos; el archivo define el corte diario |
| D2 | Unificación de esquemas | snake_case + renombres `latitude→lat`, `longitude→long`, `incidence_rate→incident_rate`; columnas inexistentes quedan nulas | Los 5 esquemas quedan en 18 columnas sin pérdida de filas (verificado: 4.287.473 filas en CSV = en Parquet) |
| D3 | Linaje | Cada fila guarda `archivo_origen` y `fila_origen` | Permite decir de qué archivo y fila sale cualquier número (nivel excelente de R2) |
| D4 | Imputación | **No se imputa** en la capa limpia: conteos como enteros *nullable* | *Imputar es inventar* |
| D5 | Capas y dónde viven | Cruda = CSV en disco temporal (Colab `/content/data/raw`, no va a git); limpia = Parquet; analítica = DuckDB + Parquet por tabla. **Ninguna capa se versiona en git**: se regeneran con los notebooks | Requisito R1; los datos limpios pesan ~110 MB (sobre el límite de GitHub por archivo); Parquet ocupa ~8× menos y se lee ~17× más rápido que CSV |
| D6 | Persistencia en Colab | Notebooks 01–03 montan Google Drive y guardan en `MyDrive/proyecto-gestion-datos-2026/data` | Cada notebook de Colab corre en una máquina distinta; así 02 y 03 leen lo que dejó 01 sin repetir la descarga |
| D7 | Motor del DW | **DuckDB** (frente a MongoDB/NoSQL) | Carga analítica, columnar, lee Parquet con SQL, embebido (corre en Colab); datos tabulares de solo lectura |
| D8 | Homologación de países | Tabla manual nombre original → país de la tabla UID → ISO3 (249 → 201); territorios de ultramar informados como país pasan a provincia de su país soberano | Mismo país con varios nombres (`Mainland China`, `Korea, South`…); la llave del DW no puede ser el nombre |
| D9 | Duplicados en territorio × día | Se conserva la **última** fila del archivo | Son repeticiones del mismo reporte (78 filas) |
| D10 | Acumulados que bajan | **Marcar** (`flag_acum_baja`), no recalcular la historia | Recalcular sería inventar cómo se repartió la corrección |
| D11 | Archivo defectuoso 23-may-2022 | **Marcar** (`flag_archivo_defectuoso`) | En ese reporte el acumulado baja en 136 países a la vez; explica casi toda la diferencia entre 158 países (reportes) y 84 (series) |
| D12 | Picos por rezagos | Regla: nuevos > 5× promedio de 28 días previos y > 1.000, salvo régimen de reporte semanal; se **marcan** | Separa rezagos reales (Chile 17-jun-2020, +36 mil) del reporte semanal de 2022 |
| D13 | Nuevos al aparecer un territorio | El primer día de un territorio los nuevos quedan **nulos** | Evita picos falsos cuando Chile pasa de nacional a 16 regiones (20-may-2020); los totales nacionales se calculan agregando acumulados |
| D14 | Entidades especiales | Cruceros, JJ.OO. y Antártica se conservan pero se **excluyen** de rankings y tasas | No tienen población comparable |
| D15 | Coordenadas (0, 0) | Se anulan en `dim_territorio` | No son ubicaciones reales; romperían el mapa |
| D16 | P7 | Banco Mundial: % de población ≥ 65 años vs. mortalidad por 100.000 | Elegida por el equipo; ver `docs/propuesta_P7.md` |
| D17 | Perfilado en Colab | `ydata-profiling` se instala en una carpeta aparte (`pip --target /tmp/libs_perfil`) y corre como subproceso | Exige NumPy < 2.4 y `pkg_resources` (setuptools < 81); Colab trae NumPy 2.4. Instalarlo en el kernel obliga a reiniciar el runtime y rompe *Ejecutar todo*. Verificado en Colab el 10-nov-2026 |
