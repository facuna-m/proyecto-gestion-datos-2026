# Sala de crisis COVID-19 · Proyecto semestral Gestión de Datos (IN1232C · 2026-2)

Plataforma de datos con el registro histórico de la pandemia (Johns Hopkins CSSE, 22-ene-2020 a 9-mar-2023): ingesta, calidad, Data Warehouse, fuentes externas, análisis, predicción, alerta temprana y tablero para el Comité Asesor de Preparación Pandémica.

* **Tablero en vivo:** https://sala-crisis-covid-ucsc.streamlit.app
* **Informe técnico:** [`docs/informe_tecnico.pdf`](docs/informe_tecnico.pdf) · **Informe al Comité:** [`docs/informe_comite.pdf`](docs/informe_comite.pdf)

## Equipo y roles

| Integrante | Rol principal | Componentes |
|---|---|---|
| Felipe Acuña | Ingeniería de datos | R1 ingesta y arquitectura · R3 DW e integración |
| Pablo Peña | Calidad y gobierno | R2 calidad · R6 protección de datos |
| Nicolás Alvarado | Análisis y modelos | R4 análisis histórico · R5 minería y predicción |
| Brandon Martínez | Tablero y comunicación | R7 tablero · R8 informe al Comité |

Todos revisan el trabajo de todos: el Comité puede preguntar a cualquiera.

## Resultados principales

* **P1:** Chile es 2.º de Sudamérica en fallecidos por 100.000 (336), detrás de Perú (666). Tuvo 4 olas: la de más casos fue ómicron (2022) y la de más fallecidos, la de 2021.
* **P2:** Magallanes (453) y Metropolitana (423) tienen la mayor mortalidad por 100.000; Biobío es 10.º de 16 (309).
* **P3:** la letalidad aparente de Chile bajó de 2,3 % antes de vacunar a 0,45 % con más del 70 % vacunado (con cautelas: testeo y ómicron).
* **P4:** índice de calidad mediano 99,8; el peor es Corea del Norte (73,8); Chile tiene 90,2. Un archivo defectuoso (23-may-2022) baja el acumulado de 136 países a la vez.
* **P5:** 4 grupos de países por la forma de su pandemia; Chile está con Europa y la mayoría de Sudamérica ("olas sostenidas, ómicron la mayor").
* **P6:** la alerta se encendió 5 días antes de la ola de ómicron, pero los pronósticos con corte el 27-dic-2021 no la vieron venir.
* **P7:** los países más envejecidos tuvieron más mortalidad (Spearman 0,79 en 150 países; ~14 fallecidos más por 100.000 por cada punto % de población de 65+).

## Cómo reproducir todo con un comando (computador)

```bash
git clone https://github.com/facuna-m/proyecto-gestion-datos-2026.git
cd proyecto-gestion-datos-2026
pip install -r requirements.txt
python reproducir.py
```

`reproducir.py` ejecuta los notebooks 00 a 07 en orden: descarga los datos crudos en `data/raw/`, regenera la capa limpia (`data/clean/`) y el DW (`data/dw/`), deja los notebooks ejecutados en `salidas/` y actualiza las copias que usa el tablero. No modifica los notebooks: solo cambia, en memoria, las rutas de Colab por las de esta carpeta. Tarda entre 10 y 30 minutos según la conexión (la primera vez descarga unos 600 MB). Después: `streamlit run dashboard/app.py`.

## Cómo reproducir todo desde cero (Google Colab)

1. Abrir Colab con la cuenta que usará Google Drive y cargar los notebooks: *Archivo → Abrir cuaderno → GitHub*, pegar la URL de este repositorio y elegir el notebook.
2. Ejecutar cada notebook **en orden** con *Entorno de ejecución → Ejecutar todo*. Del 01 en adelante, Colab pide autorizar Google Drive: los datos quedan en `MyDrive/proyecto-gestion-datos-2026/data` y cada notebook lee lo que dejó el anterior.
   1. `00_exploracion` · exploración guiada de enero a junio de 2020 y perfilado automático. Si aparece un error de NumPy al importar `ydata_profiling`: *Entorno de ejecución → Reiniciar la sesión y ejecutar todas las celdas*.
   2. `01_ingesta` · descarga los 1.143 reportes, las series y la tabla UID (capa cruda), unifica los 5 esquemas y guarda la capa limpia en Parquet. Compara CSV y Parquet. ~5 a 8 minutos.
   3. `02_calidad` · homologación de países, 13 reglas de calidad de las 6 dimensiones, cuantificación de problemas e índice de calidad por país.
   4. `03_dw_estrella` · modelo en estrella en SQLite, conciliación y consultas OLAP.
   5. `04_analisis_prediccion` · serie territorio × día, `alerta()`, `pronosticar()` y respuestas P1, P2, P4 y P6. Guarda la serie que usa el tablero. La sección 6 es la prueba en vivo con verificación de fuga de datos.
   6. `05_fuentes_externas` · descarga Banco Mundial y OWID, cruce por ISO3, carga en el DW y respuestas P3 y P7.
   7. `06_segmentacion` · k-means sobre la forma de las curvas (P5).
   8. `07_proteccion_datos` · R6: Ley 19.628 y 21.719, celdas pequeñas y regla de supresión.
3. **Tablero:** abrir https://sala-crisis-covid-ucsc.streamlit.app, o ejecutarlo localmente con `pip install -r dashboard/requirements.txt` y `streamlit run dashboard/app.py`. Si se regeneran los datos, copiar a `dashboard/` los archivos `serie_territorio`, `calidad_por_pais`, `vacunacion` y `segmentacion_paises` de `data/clean/`.

**Usar los datos ya procesados:** la capa limpia está en `data/clean/` y el DW en `data/dw/covid_dw.db.gz` (descomprimir con `gunzip covid_dw.db.gz`).

## Desafío en vivo

En el tablero: elegir el territorio y la fecha de corte. Muestra los KPI a esa fecha, si la alerta estaba activa y el pronóstico de los tres modelos frente a lo que realmente pasó (con MAE y MAPE).
En el notebook 04, sección 6 «Prueba en vivo»: se elige `TERRITORIO` y `FECHA_CORTE` (por defecto Biobío al 5-nov-2021, una semana antes de una ola) y se ejecutan `alerta()` y `pronosticar(territorio, fecha_corte, 14)`. La celda siguiente repite los cálculos sin ningún dato posterior al corte y comprueba que el resultado es idéntico (no hay fuga de datos); la última compara el pronóstico con lo que realmente ocurrió (MAE, MAPE y gráfico).

## Estructura

```
notebooks/
  00_exploracion          Hito 1: exploración guiada y perfilado
  01_ingesta              R1: descarga, unificación de 5 esquemas, capa Parquet, CSV vs Parquet
  02_calidad              R2: homologación, reglas de las 6 dimensiones, índice de calidad
  03_dw_estrella          R3: modelo en estrella en SQLite, conciliación, OLAP
  04_analisis_prediccion  R4/R5: alerta, pronóstico, P1, P2, P4, P6
  05_fuentes_externas     R3: Banco Mundial y OWID por ISO3; P3 y P7
  06_segmentacion         R5: k-means (P5)
  07_proteccion_datos     R6: datos personales, celdas pequeñas, supresión
data/
  clean/                  capa limpia (Parquet); los datos crudos NO se versionan (se descargan con 01 y 05)
  dw/covid_dw.db.gz       capa analítica: DW SQLite comprimido
dashboard/
  app.py                  tablero Streamlit (R7)
  *.parquet               copias livianas de la capa limpia que usa el tablero
  capturas/               capturas de pantalla del tablero
docs/
  informe_tecnico.pdf     informe técnico (arquitectura, calidad, modelo de datos, resultados, limitaciones)
  informe_comite.pdf      informe al Comité (2 páginas, R8)
  diccionario_datos.md    diccionario de la tabla unificada y del DW (R2)
  decisiones.md           registro de decisiones con su motivo
  propuesta_P7.md         propuesta de la pregunta propia (Hito 1)
reports/                  perfil automático de ene–jun 2020 (ydata-profiling)
reproducir.py             regenera todo con un comando fuera de Colab
requirements.txt          librerías de Python del proyecto
contribuciones.md         quién hizo qué y uso de IA generativa
```

## Avance por hito

| Hito | Qué se pide | Estado |
|---|---|---|
| 1 · Explorar | Repositorio, roles, `00_exploracion`, P7 propuesta | ✅ Listo |
| 2 · Datos | Ingesta unificada, capa Parquet, reglas de calidad, modelo en estrella | ✅ Listo |
| 3 · Análisis | P1 a P7, pronóstico con backtesting, alerta, tablero | ✅ Listo (24-nov-2026) |
| Entrega final | Repositorio, informes y tablero | ✅ Listo |

## Fuentes

* JHU CSSE COVID-19 Data Repository: https://github.com/CSSEGISandData/COVID-19 (archivado el 10-mar-2023).
* Banco Mundial, API v2: https://api.worldbank.org/v2 (indicadores `SP.POP.65UP.TO.ZS` y `NY.GDP.PCAP.PP.KD`, año 2019).
* Our World in Data, vacunación: https://github.com/owid/covid-19-data (`public/data/vaccinations/vaccinations.csv`).
