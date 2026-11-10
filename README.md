# Sala de crisis COVID-19 · Proyecto semestral Gestión de Datos (IN1232C · 2026-2)

Plataforma de datos con el registro histórico de la pandemia (Johns Hopkins CSSE, 22-ene-2020 a 9-mar-2023): ingesta, calidad, Data Warehouse, análisis, predicción y tablero para el Comité Asesor de Preparación Pandémica.

## Equipo y roles

| Integrante | Rol principal | Componentes |
|---|---|---|
| Felipe Acuña | Ingeniería de datos | R1 ingesta y arquitectura · R3 DW |
| Pablo Peña | Calidad y gobierno | R2 calidad · R6 protección de datos |
| Nicolás Alvarado | Análisis y modelos | R4 análisis histórico · R5 minería y predicción |
| Brandon Martínez | Tablero y comunicación | R7 tablero · R8 informe al Comité |

Todos revisan el trabajo de todos: el Comité puede preguntar a cualquiera.

## Cómo reproducir (Google Colab)

1. Abrir cada notebook de `notebooks/` en Colab (*Archivo → Abrir cuaderno → GitHub* y pegar la URL de este repositorio).
2. Ejecutar **en orden**, cada uno con *Entorno de ejecución → Ejecutar todo*:
   1. `00_exploracion.ipynb` · exploración guiada ene–jun 2020 (no requiere Drive).
   2. `01_ingesta.ipynb` · descarga los 1.143 reportes, series y tabla UID; unifica los 5 esquemas; escribe la capa limpia en Parquet. Pide autorizar Google Drive (los datos quedan en `MyDrive/proyecto-gestion-datos-2026/data`). ~3–5 min.
   3. `02_calidad.ipynb` · homologación de países y reglas de calidad de las 6 dimensiones.
   4. `03_dw_estrella.ipynb` · modelo en estrella en DuckDB y primeras consultas OLAP.
3. Los datos **no** están en el repositorio (la capa limpia pesa ~110 MB): siempre se regeneran ejecutando los notebooks en orden.

### En un computador (sin Colab)
1. `git clone` de este repositorio y `cd` a la carpeta.
2. `pip install -r requirements.txt`
3. `cd notebooks` y ejecutar los notebooks en orden (por ejemplo `jupyter nbconvert --to notebook --execute --inplace 01_ingesta.ipynb`). Los datos se escriben en `data/` dentro del repositorio.

## Estructura

```
notebooks/      00_exploracion · 01_ingesta · 02_calidad · 03_dw_estrella (en orden, ejecutables)
data/           NO se versiona (se regenera con los notebooks; en Colab queda en Google Drive)
  raw/          capa cruda: CSV originales (01_ingesta)
  clean/        capa limpia: Parquet unificados, series, tabla UID, homologación, calidad (01 y 02)
  dw/           capa analítica: DuckDB + tablas del modelo en estrella en Parquet (03)
docs/           diccionario de datos, decisiones, propuesta P7, informes (pendientes)
reports/        perfil automático (ydata-profiling)
contribuciones.md
```

## Avance por hito

| Hito | Qué se pide | Estado |
|---|---|---|
| 1 · Explorar | Repositorio, roles, `00_exploracion`, P7 propuesta | ✅ Listo |
| 2 · Datos | Ingesta de los 1.143 reportes unificada, capa Parquet, primeras reglas de calidad, modelo en estrella cargado | ✅ Listo (falta integrar fuente externa) |
| 3 · Análisis | P1–P6, pronóstico con backtesting, primera versión del tablero | ⏳ Pendiente |

## Fuentes
* JHU CSSE COVID-19 Data Repository: https://github.com/CSSEGISandData/COVID-19 (archivado el 10-mar-2023).
* Our World in Data, vacunación: https://github.com/owid/covid-19-data (pendiente, P3).
* Banco Mundial API v2: https://api.worldbank.org/v2 (pendiente, P7).
