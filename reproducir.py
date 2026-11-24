"""
Reproduce todo el proyecto con un solo comando, fuera de Colab.

    pip install -r requirements.txt
    python reproducir.py

Ejecuta en orden los mismos notebooks 00 a 07 que se usan en Colab y deja:

    data/raw/       capa cruda: CSV y JSON descargados (no se versiona)
    data/clean/     capa limpia: Parquet
    data/dw/        capa analítica: covid_dw.db y su copia comprimida covid_dw.db.gz
    salidas/        los notebooks ejecutados, con todos sus resultados
    reports/        el perfil automático de enero a junio de 2020
    dashboard/      las copias de la capa limpia que usa el tablero

Los notebooks de notebooks/ no se modifican: el script cambia, solo en memoria,
las rutas de Colab (Google Drive y /content) por las de esta carpeta.
La primera vez descarga unos 600 MB; en total tarda entre 10 y 30 minutos según la conexión.
"""
import gzip
import shutil
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

RAIZ = Path(__file__).resolve().parent
TRABAJO = RAIZ / 'trabajo'      # hace de /content, el disco temporal de la sesión de Colab
SALIDAS = RAIZ / 'salidas'      # notebooks ejecutados

NOTEBOOKS = [
    '00_exploracion',
    '01_ingesta',
    '02_calidad',
    '03_dw_estrella',
    '04_analisis_prediccion',
    '05_fuentes_externas',
    '06_segmentacion',
    '07_proteccion_datos',
]

# Rutas de Colab -> rutas de esta carpeta (de la más específica a la más general)
CAMBIOS = [
    ("from google.colab import drive\ndrive.mount('/content/drive')",
     "# Fuera de Colab no se monta Google Drive"),
    ('/content/drive/MyDrive/proyecto-gestion-datos-2026', RAIZ.as_posix()),
    ('/content/datos_crudos', (RAIZ / 'data' / 'raw').as_posix()),
    ("CARPETA = 'datos_crudos'", f"CARPETA = '{(RAIZ / 'data' / 'raw' / 'daily_reports').as_posix()}'"),
    ('/content/', TRABAJO.as_posix() + '/'),
    ('!pip install', '# Ya instalado con requirements.txt: pip install'),
]

# Archivos de la capa limpia que lee el tablero
PARA_TABLERO = ['serie_territorio', 'calidad_por_pais', 'vacunacion', 'segmentacion_paises']


def adaptar(nb):
    for celda in nb.cells:
        if celda.cell_type == 'code':
            for colab, local in CAMBIOS:
                celda.source = celda.source.replace(colab, local)
    return nb


def ejecutar(nombre):
    nb = nbformat.read(RAIZ / 'notebooks' / f'{nombre}.ipynb', as_version=4)
    adaptar(nb)
    cliente = NotebookClient(nb, timeout=None, kernel_name='python3',
                             resources={'metadata': {'path': TRABAJO.as_posix()}})
    try:
        cliente.execute()
    finally:
        nbformat.write(nb, SALIDAS / f'{nombre}.ipynb')


def main():
    for carpeta in [TRABAJO, SALIDAS, RAIZ / 'data' / 'raw', RAIZ / 'data' / 'clean', RAIZ / 'data' / 'dw']:
        carpeta.mkdir(parents=True, exist_ok=True)

    inicio_total = time.time()
    for nombre in NOTEBOOKS:
        print(f'Ejecutando {nombre} ...', flush=True)
        inicio = time.time()
        try:
            ejecutar(nombre)
        except CellExecutionError as error:
            print(f'\nERROR en {nombre}. El notebook con el error quedó en salidas/{nombre}.ipynb\n')
            print(str(error)[-3000:])
            sys.exit(1)
        print(f'  listo en {(time.time() - inicio) / 60:.1f} min', flush=True)

    # Capa analítica comprimida (es la que se versiona en GitHub)
    dw = RAIZ / 'data' / 'dw' / 'covid_dw.db'
    with open(dw, 'rb') as origen, gzip.open(RAIZ / 'data' / 'dw' / 'covid_dw.db.gz', 'wb') as destino:
        shutil.copyfileobj(origen, destino)

    # Copias para el tablero y perfil automático
    for archivo in PARA_TABLERO:
        shutil.copy(RAIZ / 'data' / 'clean' / f'{archivo}.parquet', RAIZ / 'dashboard' / f'{archivo}.parquet')
    perfil = TRABAJO / 'perfil_ene_jun_2020.html'
    if perfil.exists():
        (RAIZ / 'reports').mkdir(exist_ok=True)
        shutil.copy(perfil, RAIZ / 'reports' / perfil.name)

    shutil.rmtree(TRABAJO, ignore_errors=True)
    print(f'\nTodo listo en {(time.time() - inicio_total) / 60:.1f} min.')
    print('Notebooks ejecutados en salidas/; capa limpia en data/clean/; DW en data/dw/.')
    print('Tablero: streamlit run dashboard/app.py')


if __name__ == '__main__':
    main()
