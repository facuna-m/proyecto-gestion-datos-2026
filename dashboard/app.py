# Sala de crisis COVID-19 · Tablero (R7)
# Ejecutar:  streamlit run dashboard/app.py
import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title='Sala de crisis COVID-19', layout='wide')

CARPETA = os.path.dirname(os.path.abspath(__file__))
UMBRAL_VARIACION = 50   # % de alza semanal de la incidencia
UMBRAL_MINIMO = 20      # casos por 100.000 en 7 días
ARCHIVO_DEFECTUOSO = pd.Timestamp('2022-05-23')


@st.cache_data
def cargar():
    serie = pd.read_parquet(os.path.join(CARPETA, 'serie_territorio.parquet'))
    serie['fecha'] = pd.to_datetime(serie['fecha'])
    calidad = pd.read_parquet(os.path.join(CARPETA, 'calidad_por_pais.parquet'))
    return serie, calidad


serie, calidad = cargar()


# ---------- Mismas funciones que el notebook 04 (solo usan datos hasta la fecha de corte) ----------
def alerta(territorio, fecha):
    fecha = pd.Timestamp(fecha)
    s = serie[(serie['territorio'] == territorio) & (serie['fecha'] <= fecha)]
    nuevos = s['casos_nuevos'].clip(lower=0)
    pob = s['poblacion'].iloc[0]
    inc_actual = nuevos.tail(7).sum() / pob * 100000
    inc_anterior = nuevos.iloc[-14:-7].sum() / pob * 100000
    variacion = (inc_actual / inc_anterior - 1) * 100 if inc_anterior > 0 else np.nan
    activa = (variacion > UMBRAL_VARIACION) and (inc_actual >= UMBRAL_MINIMO)
    return inc_actual, inc_anterior, variacion, activa


def pronosticar(territorio, fecha_corte, horizonte=14):
    fecha_corte = pd.Timestamp(fecha_corte)
    s = serie[(serie['territorio'] == territorio) & (serie['fecha'] <= fecha_corte)]
    mm7 = s['casos_mm7'].dropna()
    base = [mm7.iloc[-1]] * horizonte
    y = np.log(mm7.tail(14).clip(lower=1))
    x = np.arange(len(y))
    pendiente, intercepto = np.polyfit(x, y, 1)
    tendencia = np.exp(intercepto + pendiente * np.arange(len(y), len(y) + horizonte))
    fechas = pd.date_range(fecha_corte + pd.Timedelta(days=1), periods=horizonte)
    return pd.DataFrame({'fecha': fechas, 'media_movil': np.round(base), 'tendencia': np.round(tendencia)})


def suprimir(valor, poblacion):
    # R6 · control de divulgación: celdas pequeñas (1 a 4) en territorios de menos de 100.000 habitantes
    if poblacion < 100000 and 1 <= valor <= 4:
        return '1–4 (suprimido)'
    return f'{valor:,.0f}'.replace(',', '.')


def fmt(x, dec=0):
    return f'{x:,.{dec}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


# ---------- Filtros ----------
st.sidebar.title('Filtros')
territorios = sorted(serie[serie['nivel'] == 'pais']['territorio'].unique())
regiones = sorted(serie[serie['nivel'] == 'region']['territorio'].unique())
opciones = ['Chile'] + regiones + [t for t in territorios if t != 'Chile']
territorio = st.sidebar.selectbox('Territorio (país o región de Chile)', opciones, index=0)

fmin = pd.Timestamp('2020-03-01').date()
fmax = serie['fecha'].max().date()
fecha_corte = pd.Timestamp(st.sidebar.date_input('Fecha de corte', value=pd.Timestamp('2021-12-27').date(),
                                                 min_value=fmin, max_value=fmax))
horizonte = st.sidebar.slider('Horizonte del pronóstico (días)', 7, 28, 14)
mostrar_real = st.sidebar.checkbox('Mostrar lo que realmente pasó después del corte', value=True)
st.sidebar.markdown('---')
st.sidebar.caption(f'Datos: JHU CSSE, reportes diarios del 22-ene-2020 al {fmax:%d-%m-%Y}. '
                   'Proyecto semestral Gestión de Datos UCSC 2026-2.')

s_all = serie[serie['territorio'] == territorio]
s = s_all[s_all['fecha'] <= fecha_corte]
if len(s) < 15:
    st.warning('No hay suficientes datos de este territorio antes de la fecha de corte.')
    st.stop()
hoy = s.iloc[-1]
pob = hoy['poblacion']

st.title(f'Sala de crisis COVID-19 · {territorio}')
st.caption(f'Datos hasta la fecha de corte: **{fecha_corte:%d-%m-%Y}** (el tablero no usa nada posterior, '
           'salvo la línea de "lo que realmente pasó", que se puede ocultar).')

# ---------- KPI ----------
inc_actual, inc_anterior, variacion, activa = alerta(territorio, fecha_corte)
casos_semana = s['casos_nuevos'].clip(lower=0).tail(7).sum()
fall_semana = s['fallecidos_nuevos'].clip(lower=0).tail(7).sum()
letalidad = hoy['fallecidos_acum'] / hoy['casos_acum'] * 100 if hoy['casos_acum'] > 0 else np.nan

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric('Casos acumulados', fmt(hoy['casos_acum']), f'{suprimir(casos_semana, pob)} últimos 7 días')
k2.metric('Fallecidos acumulados', fmt(hoy['fallecidos_acum']), f'{suprimir(fall_semana, pob)} últimos 7 días',
          delta_color='inverse')
k3.metric('Incidencia 7 días / 100.000', fmt(inc_actual, 1),
          f'{fmt(variacion, 0)} % vs semana anterior' if not np.isnan(variacion) else 's/d', delta_color='inverse')
k4.metric('Fallecidos / 100.000', fmt(hoy['fallecidos_acum'] / pob * 100000, 1))
k5.metric('Letalidad aparente', f'{fmt(letalidad, 2)} %')

# ---------- Alerta ----------
regla = (f'Regla: la alerta se activa si la incidencia de 7 días sube más de **{UMBRAL_VARIACION} %** en una semana '
         f'**y** supera **{UMBRAL_MINIMO} por 100.000**.')
if activa:
    st.error(f'🚨 ALERTA TEMPRANA ACTIVA al {fecha_corte:%d-%m-%Y}: incidencia {fmt(inc_actual, 1)} por 100.000, '
             f'alza de {fmt(variacion, 0)} % en una semana. ' + regla)
else:
    st.success(f'Sin alerta al {fecha_corte:%d-%m-%Y}: incidencia {fmt(inc_actual, 1)} por 100.000, '
               f'variación {fmt(variacion, 0) if not np.isnan(variacion) else "s/d"} %. ' + regla)

# ---------- Tendencia + pronóstico ----------
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader('Casos nuevos diarios (media móvil 7 días) y pronóstico')
    p = pronosticar(territorio, fecha_corte, horizonte)
    desde = fecha_corte - pd.Timedelta(days=180)
    fig = go.Figure()
    h = s[s['fecha'] >= desde]
    fig.add_trace(go.Scatter(x=h['fecha'], y=h['casos_mm7'], name='Histórico (MM7)', line=dict(color='#1f4e79')))
    fig.add_trace(go.Scatter(x=p['fecha'], y=p['media_movil'], name='Pronóstico: media móvil',
                             line=dict(dash='dash', color='#e69f00')))
    fig.add_trace(go.Scatter(x=p['fecha'], y=p['tendencia'], name='Pronóstico: tendencia',
                             line=dict(dash='dash', color='#cc3311')))
    errores = None
    if mostrar_real:
        real = s_all[(s_all['fecha'] > fecha_corte) & (s_all['fecha'] <= p['fecha'].max())]
        fig.add_trace(go.Scatter(x=real['fecha'], y=real['casos_mm7'], name='Lo que realmente pasó',
                                 line=dict(color='gray', width=2)))
        comp = p.merge(real[['fecha', 'casos_mm7']], on='fecha', how='inner')
        if len(comp) > 0:
            errores = {}
            for m in ['media_movil', 'tendencia']:
                e = (comp[m] - comp['casos_mm7']).abs()
                errores[m] = (e.mean(), (e / comp['casos_mm7'].clip(lower=1)).mean() * 100)
    fig.add_vline(x=fecha_corte, line_width=1, line_dash='dot', line_color='gray')
    if desde <= ARCHIVO_DEFECTUOSO <= fecha_corte + pd.Timedelta(days=horizonte):
        fig.add_vline(x=ARCHIVO_DEFECTUOSO, line_width=1, line_color='orange')
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation='h', y=-0.15))
    st.plotly_chart(fig, width='stretch')
    if errores:
        st.caption(f'Error del pronóstico frente a lo ocurrido · media móvil: MAE {fmt(errores["media_movil"][0])}, '
                   f'MAPE {fmt(errores["media_movil"][1], 1)} % · tendencia: MAE {fmt(errores["tendencia"][0])}, '
                   f'MAPE {fmt(errores["tendencia"][1], 1)} %')

with col2:
    st.subheader('Ranking a la fecha')
    nivel_rank = st.radio('Comparar', ['Países', 'Regiones de Chile'], horizontal=True)
    nivel = 'pais' if nivel_rank == 'Países' else 'region'
    r = serie[(serie['nivel'] == nivel) & (serie['fecha'] == serie[serie['fecha'] <= fecha_corte]['fecha'].max())]
    if nivel == 'pais':
        r = r[r['poblacion'] >= 1000000]
    r = r[['territorio', 'incidencia_7d']].dropna().sort_values('incidencia_7d', ascending=False).head(10)
    r['territorio'] = r['territorio'].str.replace('Chile · ', '')
    r['incidencia_7d'] = r['incidencia_7d'].round(1)
    r.columns = ['Territorio', 'Incidencia 7 días / 100.000']
    r.index = range(1, len(r) + 1)
    st.dataframe(r, width='stretch', height=390)
    if nivel == 'pais':
        st.caption('Solo países con 1 millón de habitantes o más.')

# ---------- Mapa ----------
st.subheader(f'Mapa de incidencia de 7 días por 100.000 al {fecha_corte:%d-%m-%Y}')
tipo_mapa = st.radio('Mapa', ['Mundo', 'Regiones de Chile'], horizontal=True)
ult = serie[serie['fecha'] == serie[serie['fecha'] <= fecha_corte]['fecha'].max()].dropna(subset=['lat', 'long'])
if tipo_mapa == 'Mundo':
    m = ult[ult['nivel'] == 'pais']
    fig_m = px.scatter_geo(m, lat='lat', lon='long', size=m['incidencia_7d'].clip(lower=0).fillna(0),
                           color='incidencia_7d', hover_name='territorio', color_continuous_scale='Reds',
                           projection='natural earth', size_max=35,
                           labels={'incidencia_7d': 'Incidencia 7d/100k'})
else:
    m = ult[ult['nivel'] == 'region'].copy()
    m['region'] = m['territorio'].str.replace('Chile · ', '')
    fig_m = px.scatter_geo(m, lat='lat', lon='long', size=m['incidencia_7d'].clip(lower=0).fillna(0),
                           color='incidencia_7d', hover_name='region', color_continuous_scale='Reds',
                           size_max=40, labels={'incidencia_7d': 'Incidencia 7d/100k'})
    fig_m.update_geos(fitbounds='locations', showcountries=True)
fig_m.update_layout(height=480, margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig_m, width='stretch')

# ---------- Calidad y advertencias ----------
st.subheader('Advertencias de calidad e interpretación')
pais = hoy['pais']
fila = calidad[calidad['pais'] == pais]
if len(fila) > 0:
    q = fila.iloc[0]
    st.markdown(f'- **Índice de calidad de {pais}: {fmt(q["indice_calidad"], 1)} / 100** '
                f'(mediana mundial {fmt(calidad["indice_calidad"].median(), 1)}). Días con acumulado que baja: '
                f'{int(q["dias_acum_baja"])} · picos por rezago: {int(q["picos_rezago"])} · fallecidos > casos: '
                f'{int(q["dias_fallec_mayor"])} · días que difieren de la serie: {int(q["dias_difiere_serie"])}.')
st.markdown('- El reporte del **23-may-2022** es defectuoso (el acumulado baja en 136 países): se excluyó del cálculo.\n'
            '- Si el acumulado baja (corrección), ese día cuenta como 0 en la media móvil: no se inventa el reparto.\n'
            '- La **letalidad aparente** depende de cuánto testea cada país: comparar países exige cautela.\n'
            '- En 2022 muchos países informan una vez por semana: mirar la media móvil, no el dato diario.\n'
            '- Control de divulgación (R6): en territorios de menos de 100.000 habitantes, los conteos de 1 a 4 '
            'se muestran como "1–4".')
