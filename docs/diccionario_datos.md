# Diccionario de datos

## 1 · Tabla unificada `covid_diario` (capa limpia)

**Archivo:** `data/clean/covid_diario.parquet` · **Generado por:** `notebooks/01_ingesta.ipynb`
**Grano:** una fila = un territorio (país, provincia/región/estado o condado) en un reporte diario de JHU CSSE.
**Volumen:** 4.287.473 filas · 17 columnas · 1.143 reportes (22-ene-2020 a 9-mar-2023).
**Fuente:** github.com/CSSEGISandData/COVID-19, carpeta `csse_covid_19_data/csse_covid_19_daily_reports/`.

| Columna | Significado | Tipo | Dominio observado | Origen (nombre en el CSV) | Existe desde | % no nulo |
|---|---|---|---|---|---|---|
| `fecha_reporte` | Fecha del corte diario. **Es la fecha oficial de la fila** (grano del DW) | fecha | 2020-01-22 a 2023-03-09 | Nombre del archivo `MM-DD-YYYY.csv` | 22-ene-2020 | 100 |
| `fips` | Código FIPS del condado o estado de EE.UU. | decimal | 60 a 99999 | `FIPS` | 22-mar-2020 (esquema 3) | 81,6 |
| `admin2` | Condado (solo EE.UU.) | texto | 1.960 valores | `Admin2` | 22-mar-2020 (esquema 3) | 81,8 |
| `province_state` | Provincia, región o estado. Nulo = fila de nivel país | texto | 755 valores | `Province/State` (esquemas 1–2), `Province_State` (3–5) | 22-ene-2020 | 95,4 |
| `country_region` | País o entidad **tal como lo escribe JHU** (sin homologar) | texto | 249 valores (201 países tras homologar en 02) | `Country/Region` (1–2), `Country_Region` (3–5) | 22-ene-2020 | 100 |
| `combined_key` | Nombre completo del territorio ("Biobio, Chile") | texto | 4.164 valores | `Combined_Key` | 22-mar-2020 (esquema 3) | 99,8 |
| `lat` | Latitud del territorio | decimal | −71,95 a 72,0 | `Latitude` (2), `Lat` (3–5) | 1-mar-2020 (esquema 2) | 97,7 |
| `long` | Longitud del territorio | decimal | −178,1 a 178,1 | `Longitude` (2), `Long_` (3–5) | 1-mar-2020 (esquema 2) | 97,7 |
| `confirmed` | Casos confirmados **acumulados** | decimal (por los nulos) | −302.844 a 38.618.509 ⚠ negativos | `Confirmed` | 22-ene-2020 | 100 |
| `deaths` | Fallecidos **acumulados** | decimal | −178 a 186.138 ⚠ negativos | `Deaths` | 22-ene-2020 | 100 |
| `recovered` | Recuperados acumulados. **Deja de actualizarse en ago-2021**: no usar después | decimal | ⚠ con negativos | `Recovered` | 22-ene-2020 | 34,0 |
| `active` | Casos activos = confirmados − fallecidos − recuperados. Pierde sentido sin `recovered` | decimal | 0 a 5.658.278 | `Active` | 22-mar-2020 (esquema 3) | 33,8 |
| `incident_rate` | Casos acumulados por 100.000 habitantes, calculado por JHU | decimal | 0 a 2,16 M ⚠ valores imposibles | `Incidence_Rate` (4), `Incident_Rate` (5) | 29-may-2020 (esquema 4) | 92,6 |
| `case_fatality_ratio` | Fallecidos ÷ confirmados × 100 (letalidad aparente), calculado por JHU | decimal | 0 a 29.600 ⚠ > 100 % | `Case-Fatality_Ratio` (4), `Case_Fatality_Ratio` (5) | 29-may-2020 (esquema 4) | 93,6 |
| `last_update` | Fecha y hora en que JHU actualizó la fila (no es la fecha del dato) | fecha-hora | 2020-01-22 a 2023-03-10 | `Last Update` (1–2), `Last_Update` (3–5), varios formatos | 22-ene-2020 | 100 |
| `archivo_origen` | Archivo CSV de donde salió la fila (**linaje**) | texto | 1.143 valores | Calculado (01) | — | 100 |
| `fila_origen` | N.º de fila de datos dentro del CSV, desde 1 (**linaje**) | entero | 1 a 4.016 | Calculado (01) | — | 100 |

**Notas**
* Los nulos de `fips`, `admin2`, `combined_key`, `lat/long`, `incident_rate` y `case_fatality_ratio` antes de su fecha de inicio son **estructurales** (la columna no existía), no faltantes.
* Los conteos quedan como decimales porque tienen nulos; **no se imputan** (*imputar es inventar*). Las decisiones sobre negativos, picos y duplicados están en `notebooks/02_calidad.ipynb` y en `docs/decisiones.md`.

## 2 · Data Warehouse `covid_dw.db` (capa analítica, SQLite)

**Archivo:** `data/dw/covid_dw.db.gz` (descomprimir con `gunzip`) · **Generado por:** `03_dw_estrella` (estrella), `05_fuentes_externas` (`dim_pais`, `fact_vacunacion`) y `06_segmentacion` (`segmentacion_paises`).

### `fact_covid` · 4.287.395 filas · grano: territorio × día
| Columna | Significado |
|---|---|
| `fecha_key` | Llave a `dim_fecha` (AAAAMMDD) |
| `territorio_key` | Llave a `dim_territorio` |
| `casos_acum`, `fallecidos_acum` | Acumulados informados ese día (`confirmed`, `deaths`) |
| `casos_nuevos`, `fallecidos_nuevos` | Diferencia con el día anterior del mismo territorio; el primer día del territorio queda vacío |
| `acum_baja` | 1 si el acumulado de casos o fallecidos bajó ese día (corrección) |
| `archivo_defectuoso` | 1 si la fila viene del reporte del 23-may-2022 (acumulado baja en 136 países) |
| `archivo_origen`, `fila_origen` | Linaje: archivo y fila del CSV original |

### `dim_fecha` · 1.143 filas
`fecha_key` (AAAAMMDD), `fecha`, `anio`, `trimestre`, `mes`, `nombre_mes`, `semana` (ISO), `dia_semana` (0 = lunes), `es_fin_semana`.

### `dim_territorio` · 4.497 filas
| Columna | Significado |
|---|---|
| `territorio_key` | Llave sustituta del DW |
| `uid` | Identificador de la tabla UID de JHU (vacío en los 176 territorios que no están en ella) |
| `pais`, `region`, `condado` | Jerarquía país → región o estado → condado (nombres homologados) |
| `nivel` | `pais`, `region` o `condado` |
| `iso3`, `iso3_pais` | Código ISO3 del territorio y de su país (llave para las fuentes externas) |
| `lat`, `long` | Coordenadas (las (0, 0) quedan vacías) |
| `poblacion` | Población según la tabla UID |
| `en_tabla_uid` | 1 si el territorio está en la tabla UID |

### `dim_pais` · 197 filas (Banco Mundial + calidad)
| Columna | Significado | Fuente |
|---|---|---|
| `pais`, `iso3`, `poblacion` | País del DW | `dim_territorio` |
| `region_bm`, `grupo_ingreso` | Región y grupo de ingreso (Bajo, Medio bajo, Medio alto, Alto) | Banco Mundial |
| `pob_65_pct` | % de la población con 65 años o más, 2019 (`SP.POP.65UP.TO.ZS`) | Banco Mundial |
| `pib_pc_ppa` | PIB per cápita PPA, US$ internacionales constantes, 2019 (`NY.GDP.PCAP.PP.KD`) | Banco Mundial |
| `indice_calidad` | Índice de calidad del país (0 a 100) | `02_calidad` |
| `en_bm`, `en_owid` | 1 si el país cruza por ISO3 con cada fuente | `05_fuentes_externas` |

### `fact_vacunacion` · 133.346 filas · grano: país × día
`fecha_key`, `pais`, `pct_una_dosis` (% de la población con al menos una dosis), `pct_esquema_completo` (% con esquema completo). Fuente: Our World in Data (`vaccinations.csv`); si falta un día se mantiene el último valor conocido.

### `segmentacion_paises` · 156 filas
`pais`, `grupo` (1 a 4) de la segmentación k-means de P5 (`06_segmentacion`).

## 3 · Otras tablas de la capa limpia (`data/clean/`)
| Archivo | Contenido | Notebook |
|---|---|---|
| `uid.parquet` | Tabla UID de JHU (población, coordenadas e ISO3 de 4.321 territorios) | 01 |
| `serie_confirmados_global.parquet` | Serie de confirmados de JHU en formato largo (para comparar con los reportes) | 01 |
| `homologacion_paises.parquet` | Nombre original del país → país homologado | 02 |
| `calidad_reglas.parquet` | Resultado de las 13 reglas de calidad (filas, %, umbral, estado) | 02 |
| `calidad_por_pais.parquet` | Problemas por país e índice de calidad | 02 |
| `serie_territorio.parquet` | Serie país × día y región de Chile × día (acumulados, nuevos, media móvil, incidencia de 7 días) que usan el notebook 04 y el tablero | 04 |
| `dim_pais.parquet`, `vacunacion.parquet` | Copias de `dim_pais` y `fact_vacunacion` | 05 |
| `segmentacion_paises.parquet` | Copia de `segmentacion_paises` | 06 |
