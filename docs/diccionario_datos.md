# Diccionario de datos · tabla unificada `daily_reports` (versión preliminar · Hito 2)

**Archivo:** `data/clean/daily_reports.parquet` · **Generado por:** `notebooks/01_ingesta.ipynb`
**Grano:** una fila = un territorio (país, provincia/región/estado o condado) en un reporte diario de JHU CSSE.
**Volumen:** 4.287.473 filas · 18 columnas · 1.143 reportes (22-ene-2020 a 9-mar-2023).
**Fuente:** github.com/CSSEGISandData/COVID-19, carpeta `csse_covid_19_data/csse_covid_19_daily_reports/`.

| Columna | Significado | Tipo | Dominio observado | Origen (nombre en el CSV) | Existe desde | % no nulo |
|---|---|---|---|---|---|---|
| `fecha_reporte` | Fecha del corte diario. **Es la fecha oficial de la fila** (grano del DW) | fecha | 2020-01-22 a 2023-03-09 | Nombre del archivo `MM-DD-YYYY.csv` | 22-ene-2020 | 100 |
| `fips` | Código FIPS del condado/estado de EE.UU. | entero | 60 a 99999 | `FIPS` | 22-mar-2020 (etapa 3) | 81,6 |
| `admin2` | Condado (solo EE.UU.) | texto | 1.960 valores | `Admin2` | 22-mar-2020 (etapa 3) | 81,8 |
| `province_state` | Provincia, región o estado. Nulo = fila de nivel país | texto | 756 valores | `Province/State` (etapas 1–2), `Province_State` (3–5) | 22-ene-2020 | 95,4 |
| `country_region` | País o entidad **tal como lo escribe JHU** (sin homologar) | texto | 249 valores (201 tras homologar) | `Country/Region` (1–2), `Country_Region` (3–5) | 22-ene-2020 | 100 |
| `combined_key` | Nombre completo del territorio ("Biobio, Chile") | texto | 4.164 valores | `Combined_Key` | 22-mar-2020 (etapa 3) | 99,8 |
| `lat` | Latitud del territorio | decimal | −71,9 a 72,0 | `Latitude` (2), `Lat` (3–5) | 1-mar-2020 (etapa 2) | 97,7 |
| `long` | Longitud del territorio | decimal | −178,1 a 178,1 | `Longitude` (2), `Long_` (3–5) | 1-mar-2020 (etapa 2) | 97,7 |
| `confirmed` | Casos confirmados **acumulados** | entero | −302.844 a 38.618.509 ⚠ negativos | `Confirmed` | 22-ene-2020 | 100 |
| `deaths` | Fallecidos **acumulados** | entero | −178 a 186.138 ⚠ negativos | `Deaths` | 22-ene-2020 | 100 |
| `recovered` | Recuperados acumulados. **Deja de actualizarse en ago-2021**: no usar después | entero | ⚠ con negativos | `Recovered` | 22-ene-2020 | 34,0 |
| `active` | Casos activos = confirmados − fallecidos − recuperados. Pierde sentido sin `recovered` | entero | 0 a 5.658.278 | `Active` | 22-mar-2020 (etapa 3) | 33,8 |
| `incident_rate` | Casos acumulados por 100.000 habitantes, calculado por JHU | decimal | 0 a 2,16 M ⚠ valores imposibles | `Incidence_Rate` (4), `Incident_Rate` (5) | 29-may-2020 (etapa 4) | 92,6 |
| `case_fatality_ratio` | Fallecidos ÷ confirmados × 100 (letalidad aparente), calculado por JHU | decimal | 0 a 29.600 ⚠ > 100 % | `Case-Fatality_Ratio` (4), `Case_Fatality_Ratio` (5) | 29-may-2020 (etapa 4) | 93,6 |
| `last_update` | Fecha y hora en que JHU actualizó la fila (no es la fecha del dato) | fecha-hora | 2020-01-22 a 2023-03-10 | `Last Update` (1–2), `Last_Update` (3–5), ≥ 4 formatos | 22-ene-2020 | 100 |
| `etapa_esquema` | Etapa del esquema del archivo de origen (1 a 5) | entero | 1–5 | Calculado (01_ingesta) | — | 100 |
| `archivo_origen` | Archivo CSV de donde salió la fila (**linaje**) | texto | 1.143 valores | Calculado | — | 100 |
| `fila_origen` | N.º de fila de datos dentro del CSV, desde 1 (**linaje**) | entero | 1 a 4.016 | Calculado | — | 100 |

## Notas
* Los nulos de `fips`, `admin2`, `combined_key`, `lat/long`, `incident_rate` y `case_fatality_ratio` antes de su fecha de inicio son **estructurales** (la columna no existía), no faltantes.
* Los conteos no se imputan en la capa limpia (*imputar es inventar*). Las decisiones sobre negativos, picos y duplicados están en `notebooks/02_calidad.ipynb` y en `docs/decisiones.md`.
* Pendiente para la versión final: columnas derivadas del DW (`casos_nuevos`, `fallecidos_nuevos`, banderas de calidad) y tablas `dim_territorio` / `dim_fecha`.
