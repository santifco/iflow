import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.set_page_config(page_title="Visualizador de Depósito", layout="wide")
st.title("📦 Visualizador de Posiciones del Depósito")

st.markdown("""
Este visualizador te permite:
- Cargar un archivo Excel con columnas 'Descripcion Articulo', 'Pasillo' y 'Columna'
- Asignar artículos a esas posiciones
- Visualizar las posiciones en forma de **grilla**
""")

# --- Subida de archivo de posiciones ---
st.header("1. Carga de Posiciones y Artículos")
archivo = st.file_uploader("Carga un archivo Excel con las columnas: 'Descripcion Articulo', 'Pasillo', 'Columna'", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)

    if 'Descripcion Articulo' not in df.columns or 'Pasillo' not in df.columns or 'Columna' not in df.columns:
        st.error("El archivo debe tener las columnas 'Descripcion Articulo', 'Pasillo' y 'Columna'")
    else:
        st.success("Archivo cargado correctamente")

        df['Col'] = df['Pasillo'].astype(str)
        df['Fila'] = df['Columna'].astype(int)
        df['Articulo'] = df['Descripcion Articulo']

        columnas = sorted(df['Col'].unique())
        filas = sorted(df['Fila'].unique())

        grilla = pd.DataFrame("", index=filas, columns=columnas)

        for _, fila in df.iterrows():
            grilla.at[fila['Fila'], fila['Col']] = fila['Articulo']

        st.header("2. Visualización de la Grilla")

        duplicados = df['Articulo'].value_counts()
        duplicados = duplicados[duplicados > 1].index.tolist()

        def highlight_duplicates(val):
            if val in duplicados:
                return 'background-color: lightgreen'
            return ''

        grilla_estilizada = grilla.style.applymap(highlight_duplicates)
        st.write("Grilla con artículos duplicados destacados en verde:")
        st.write(grilla_estilizada)



        st.header("4. Artículos con más de una posición asignada")
        conteo_articulos = df['Articulo'].value_counts().reset_index()
        conteo_articulos.columns = ['Artículo', 'Cantidad de Posiciones']
        articulos_duplicados = conteo_articulos[conteo_articulos['Cantidad de Posiciones'] > 1]
        st.dataframe(articulos_duplicados, use_container_width=True)

        st.header("5. Asignar una posición más a artículos existentes")
        modo = st.radio("Selecciona el modo de ingreso de artículos a duplicar:", ["Selección manual", "Subir archivo Excel"])

        if modo == "Selección manual":
            articulos_existentes = df['Articulo'].unique().tolist()
            articulos_seleccionados = st.multiselect("Selecciona los artículos a duplicar", articulos_existentes)
        else:
            archivo_articulos = st.file_uploader("Carga un Excel con una columna 'Articulo'", type=["xlsx"], key="excel_articulos")
            if archivo_articulos:
                df_excel = pd.read_excel(archivo_articulos)
                if 'Articulo' in df_excel.columns:
                    articulos_seleccionados = df_excel['Articulo'].dropna().unique().tolist()
                    st.success("Artículos cargados desde Excel")
                    st.write(articulos_seleccionados)
                else:
                    st.error("El archivo debe contener una columna llamada 'Articulo'")
            else:
                articulos_seleccionados = []

        if st.button("Duplicar posiciones"):
            for art in articulos_seleccionados:
                ubicaciones = [(f, c) for f in grilla.index for c in grilla.columns if grilla.at[f, c] == art]
                for fila_actual, col_actual in ubicaciones:
                    col_idx = columnas.index(col_actual)
                    fila_idx = filas.index(fila_actual)

                    if fila_idx + 1 < len(filas):
                        nueva_fila_idx = fila_idx + 1
                        nueva_col_idx = col_idx
                    else:
                        nueva_fila_idx = 0
                        nueva_col_idx = (col_idx + 1) % len(columnas)

                    nueva_fila = filas[nueva_fila_idx]
                    nueva_col = columnas[nueva_col_idx]

                    desplazamientos = []
                    f_idx = nueva_fila_idx
                    c_idx = nueva_col_idx
                    while True:
                        f = filas[f_idx]
                        c = columnas[c_idx]
                        desplazamientos.append((f, c))
                        if grilla.at[f, c] == "":
                            break
                        f_idx += 1
                        if f_idx >= len(filas):
                            f_idx = 0
                            c_idx += 1
                            if c_idx >= len(columnas):
                                st.error("No hay más espacio para desplazar artículos")
                                break

                    for i in range(len(desplazamientos)-1, 0, -1):
                        f_origen, c_origen = desplazamientos[i-1]
                        f_destino, c_destino = desplazamientos[i]
                        grilla.at[f_destino, c_destino] = grilla.at[f_origen, c_origen]

                    grilla.at[nueva_fila, nueva_col] = art

            todos_los_articulos = grilla.values.flatten()
            conteo_total = pd.Series(todos_los_articulos)
            conteo_total = conteo_total[conteo_total != ""]
            duplicados = conteo_total.value_counts()
            duplicados = duplicados[duplicados > 1].index.tolist()

            def highlight_updated(val):
                if val in duplicados:
                    return 'background-color: lightgreen'
                return ''

            grilla_estilizada = grilla.style.applymap(highlight_updated)
            st.write("Grilla actualizada con duplicados destacados en verde:")
        st.write(grilla_estilizada)


else:
    st.info("Por favor, carga un archivo Excel para comenzar.")
