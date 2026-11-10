# Propuesta de P7 (Hito 1)

## Pregunta
**¿Los países con mayor proporción de población de 65 años o más tuvieron mayor mortalidad acumulada por COVID-19 por 100.000 habitantes?**

## Fuente externa
**Banco Mundial (API v2)**, cruce por código **ISO3** con `dim_territorio.iso3_pais`.

| Indicador | Código | Uso |
|---|---|---|
| Población de 65 años o más (% del total) | `SP.POP.65UP.TO.ZS` | Variable explicativa principal |
| PIB per cápita, PPA (US$ constantes) | `NY.GDP.PCAP.PP.KD` | Variable de control (los países más envejecidos suelen ser más ricos y testear más) |
| Camas hospitalarias por 1.000 habitantes | `SH.MED.BEDS.ZS` | Control opcional (capacidad sanitaria) |

Ejemplo de llamada: `https://api.worldbank.org/v2/country/all/indicator/SP.POP.65UP.TO.ZS?format=json&date=2019&per_page=20000` (se usa el año 2019, previo a la pandemia).

## Qué se medirá
* **Variable respuesta:** fallecidos acumulados por 100.000 al 9-mar-2023 (y por ola, si alcanza), desde el DW.
* **Gráfico:** dispersión % 65+ vs. fallecidos por 100.000, coloreado por región del mundo y tamaño por población; Chile destacado.
* **Número:** correlación de Spearman (robusta a valores extremos) y una regresión simple con y sin control por PIB per cápita.
* **Interpretación (2–3 líneas):** con advertencias.

## Cautelas (correlación ≠ causalidad)
* Los países envejecidos suelen ser más ricos, **testean y registran más muertes**: parte de la relación puede ser de **registro**, no de mortalidad real. Se controlará por PIB y se filtrará por el **índice de calidad de R2** (excluir países con datos poco confiables, por ejemplo Corea del Norte).
* Es una comparación **entre países** (falacia ecológica): no dice nada sobre el riesgo de una persona mayor.
* Variables omitidas: vacunación (OWID, ya integrada para P3), restricciones, densidad, comorbilidades.

## Estado
Propuesta para revisión del equipo. La integración de datos se hará en el notebook de DW (dimensión país con indicadores del Banco Mundial).
