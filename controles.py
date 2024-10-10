import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime
from workalendar.america import Argentina
import math
from scipy.stats import norm
from datetime import datetime, timedelta
from io import BytesIO


st.set_page_config(page_title="Controles Logisticos", layout="wide")

cal = Argentina()

with st.expander("Carga de archivos"):

    
    datos_stock = st.file_uploader("Informe Stock con Operacion", type="xlsx")
    datos_reposicionamiento= st.file_uploader("Reporte Movimientos", type="xlsx")
    datos_posicion = st.file_uploader("Posicion - Cliente - Sector - Estado", type="xlsx")
    
    if datos_stock is not None:
        df_stock = pd.read_excel(datos_stock,skiprows=2)
        
        entidades_unicas = ['Todos'] + sorted(df_stock['Entidad'].unique())
        entidad_seleccionados = st.sidebar.multiselect('Entidad:', entidades_unicas, default=["Todos"])
        
        if 'Todos' not in entidad_seleccionados:
            df_stock = df_stock[df_stock['Entidad'].isin(entidad_seleccionados)]

    if datos_reposicionamiento is not None:
        df_reposicionamiento = pd.read_excel(datos_reposicionamiento,skiprows=2)
        
        rubros_unicos = ['Todos'] + sorted(df_reposicionamiento['Rubro'].unique())
        rubros_seleccionados = st.sidebar.multiselect('Rubro:', rubros_unicos, default=["Todos"])

        if 'Todos' not in rubros_seleccionados:
            df_reposicionamiento = df_reposicionamiento[df_reposicionamiento['Rubro'].isin(rubros_seleccionados)]

    if datos_reposicionamiento is not None:
        df_posicion = pd.read_excel(datos_posicion,skiprows=2)

with st.sidebar:

    p = st.slider("Proporción estimada de defectos (%)", 0, 50, 7) / 100.0


# Crear pestañas
tab1, tab2, tab3  = st.tabs(["Control Recepción", "Control Almacenaje", "Control Picking"])



with tab1:

    st.title("Control Recepcion")

        # datos_stock = st.file_uploader("Informe Stock con Operacion", type="xlsx")
        # datos_reposicionamiento= st.file_uploader("Reporte Posicionamiento", type="xlsx")
        # datos_posicion = st.file_uploader("Posicion - Cliente - Sector - Estado", type="xlsx")

        # Procesar y mostrar cada archivo si se ha subido
    if datos_stock is not None:
        # Leer el archivo de stock
        df_stock_recepcion = df_stock.dropna(subset=["Pallet"])
        df_stock_recepcion = df_stock_recepcion[df_stock_recepcion["Pallet"] != 0]
        df_stock_recepcion = df_stock_recepcion[df_stock_recepcion['Nivel'] != 1]
        df_stock_recepcion["Pallet"] = df_stock_recepcion["Pallet"].astype(int)
        # Mostrar el DataFrame resultante
        # st.write("Datos de Stock:")
        # st.write(df_stock["Pallet"])
        # st.write(df_stock)



    if datos_reposicionamiento is not None:
        # Leer el archivo de reposicionamiento
        df_reposicionamiento_recepcion = df_reposicionamiento.dropna(subset=["Pallet"])
        df_reposicionamiento_recepcion = df_reposicionamiento_recepcion[df_reposicionamiento_recepcion["Pallet"] != 0]
        df_reposicionamiento_recepcion = df_reposicionamiento_recepcion[df_reposicionamiento_recepcion["Tipo de Movimiento Alt"]=="EP"]
        df_reposicionamiento_recepcion["Pallet"] = df_reposicionamiento_recepcion["Pallet"].astype(int)

        # Mostrar el DataFrame resultante
        # st.write("Datos de Reposicionamiento:")
        # st.write(df_reposicionamiento["Pallet"])
        # st.write(df_reposicionamiento)

    if datos_posicion is not None:
        pass
        # Leer el archivo de posicion
        # Mostrar el DataFrame resultante
        # st.write("Datos de Posición:")
        # st.write(df_posicion)

    # Mensaje si no se ha subido ningún archivo
    if datos_stock is None and datos_reposicionamiento is None and datos_posicion is None:
        st.write("Por favor, sube al menos un archivo Excel.")





    if datos_stock is not None and datos_reposicionamiento is not None:
        # Realizar el merge de df_stock y df_reposicionamiento según la columna "Pallet"
        df_merged_recepcion = pd.merge(df_stock_recepcion, df_reposicionamiento_recepcion, on="Pallet", how="inner")
        
        try:
            df_merged_recepcion['Fecha (Fin Movimiento)'] = pd.to_datetime(df_merged_recepcion['Fecha (Fin Movimiento)'])
        except:
            df_merged_recepcion['Fecha (Fin Movimiento)'] = pd.to_datetime(df_merged_recepcion['Fecha (Fin Movimiento)'], origin='1899-12-30', unit='D')

        # Calcular los días laborables entre la fecha y hoy, excluyendo fines de semana y feriados
        df_merged_recepcion['Dias_Laborables'] = df_merged_recepcion['Fecha (Fin Movimiento)'].apply(
            lambda x: cal.get_working_days_delta(x.date(), datetime.now().date()) 
        )

        df_merged_recepcion['Universo'] = (df_merged_recepcion['Dias_Laborables'] == 1).astype(int)

        df_filtered = df_merged_recepcion[df_merged_recepcion['Universo'] == 1]

        # Mostrar el DataFrame resultante
        # st.write("Tabla combinada (merge) según la columna 'Pallet':")
        # st.write(df_filtered)


        # Tamaño de la población
        N = len(df_filtered)
        st.write(f"Tamaño de la población (número de filas en df_filtered): {N}")

        # Parámetros para el cálculo del tamaño de muestra
        nivel_confianza = 0.95
        z = norm.ppf(1 - (1 - nivel_confianza) / 2) # Valor de z para el nivel de confianza del 95%
        p = p  # Proporción estimada de defectos (ajústalo según tu estimación)
        e = 0.03  # Margen de error del 3%

        # Función para calcular el tamaño de muestra
        def calcular_tamano_muestra(N, z, e, p):
            numerator = N
            denominator = 1 + ((N * (e ** 2)) / (z ** 2 * p * (1 - p)))
            n = numerator / denominator
            return math.ceil(n)  # Redondea hacia arriba para asegurarte de tener un tamaño de muestra entero

        # Calcular el tamaño de la muestra
        tamano_muestra = calcular_tamano_muestra(N, z, e, p)
        st.write(f"El tamaño de muestra necesario es: {tamano_muestra}")

        # Seleccionar una muestra aleatoria de tamaño n
        df_sample = df_filtered.sample(n=tamano_muestra, random_state=1)

        # Mostrar las columnas solicitadas
        columnas_a_mostrar = [
            'Entidad', 'Articulo', 'Descripcion Articulo', 'Posicion', 'Pallet', 'Lote', 
            'Fecha Ingreso', 'Vencimiento', 'Bultos_x', 'Unidades_x', 'Tipo de Movimiento Alt', 'Rubro'
        ]
        
        
        df_sample = df_sample[columnas_a_mostrar]

        df_sample['Vencimiento'] = pd.to_datetime(df_sample['Vencimiento'], errors='coerce').dt.strftime('%d-%m-%Y')
        df_sample['Fecha Ingreso'] = pd.to_datetime(df_sample['Fecha Ingreso'], errors='coerce').dt.strftime('%d-%m-%Y')
        df_sample = df_sample.rename(columns={'Bultos_x': 'Bultos', 'Unidades_x': 'Unidades'})

        st.write("Muestra aleatoria de df_filtrado:")
        st.write(df_sample)

        def convert_df_to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                writer.close()  # No es necesario el 'save()', cerrando con 'close()' dentro del contexto
            processed_data = output.getvalue()  # Obtener los datos del archivo en formato binario
            return processed_data

        # Crear un archivo Excel de un DataFrame (en este caso df_merged)
        excel_file = convert_df_to_excel(df_sample)

        # Botón para descargar el archivo Excel
        st.download_button(
            label="Download data as Excel Recepcion",
            data=excel_file,
            file_name="df_merged_recepcion.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


    else:
        st.write("Para realizar el merge, carga ambos archivos: 'Informe Stock con Operacion' y 'Reporte Posicionamiento'.")


with tab2:
    
    st.title("Control Almacenaje")




        # datos_stock = st.file_uploader("Informe Stock con Operacion", type="xlsx")
        # datos_reposicionamiento= st.file_uploader("Reporte Posicionamiento", type="xlsx")
        # datos_posicion = st.file_uploader("Posicion - Cliente - Sector - Estado", type="xlsx")

    # Procesar y mostrar cada archivo si se ha subido
    if datos_stock is not None:
        # Leer el archivo de stock
        df_stock_almacenaje = df_stock.dropna(subset=["Pallet"])
        df_stock_almacenaje = df_stock_almacenaje[df_stock_almacenaje["Pallet"] != 0]
        df_stock_almacenaje = df_stock_almacenaje[df_stock_almacenaje['Nivel'] != 1]
        df_stock_almacenaje = df_stock_almacenaje[df_stock_almacenaje['Status Posicion'].isin(["BL", "PC", "PV", "DL"])]
        df_stock_almacenaje["Pallet"] = df_stock_almacenaje["Pallet"].astype(int)
        df_stock_almacenaje = df_stock_almacenaje[["Entidad","Cod.Articulo","Descripcion Articulo","Posicion","Lote","Pallet","Vencimiento","Status Posicion"]]
        # Mostrar el DataFrame resultante
        # st.write("Datos de Stock:")
        # st.write(df_stock["Pallet"])
        # st.write(df_stock)



    if datos_reposicionamiento is not None:
        # Leer el archivo de reposicionamiento
        df_reposicionamiento_almacenaje = df_reposicionamiento.dropna(subset=["Pallet"])
        df_reposicionamiento_almacenaje = df_reposicionamiento_almacenaje[df_reposicionamiento_almacenaje["Pallet"] != 0]
        df_reposicionamiento_almacenaje = df_reposicionamiento_almacenaje[df_reposicionamiento_almacenaje["Tipo de Movimiento Alt"]=="EP"]
        df_reposicionamiento_almacenaje["Pallet"] = df_reposicionamiento_almacenaje["Pallet"].astype(int)

        # Mostrar el DataFrame resultante
        # st.write("Datos de Reposicionamiento:")
        # st.write(df_reposicionamiento["Pallet"])
        # st.write(df_reposicionamiento)


    if datos_posicion is not None:
        # Leer el archivo de posicion
        df_posicion_almacenaje = df_posicion[df_posicion['Depest'].isin(["DL"])]
    
        # Aplicar la función para filtrar las filas donde el valor después del segundo "-" no sea "1A"
        df_posicion_almacenaje['Depposc'] = df_posicion_almacenaje['Depposc'].astype(str)
        def filtrar_despues_segundo_guion_1(valor):
            partes = valor.split(' - ')
            if len(partes) >= 3 and '1' in partes[2]:  # Verificar si en la tercera parte (después del segundo "-") contiene '1'
                return True
            return False

        # Filtrar las filas donde NO se cumpla que el valor después del segundo guion contiene "1"
        df_posicion_almacenaje  = df_posicion_almacenaje[~df_posicion_almacenaje['Depposc'].apply(filtrar_despues_segundo_guion_1)]
        df_posicion_almacenaje = df_posicion_almacenaje.rename(columns={'Entnombre': 'Entidad', 'Depposc': 'Posicion',"Depest":"Status Posicion","Artnom":"Descripcion Articulo"})
        df_posicion_almacenaje = df_posicion_almacenaje.drop(['Depid', 'Depseccod'], axis=1)
        # Mostrar el DataFrame resultante
        # st.write("Datos de Posición:")
        # st.write(df_posicion)

    # Mensaje si no se ha subido ningún archivo
    if datos_stock is None and datos_reposicionamiento is None and datos_posicion is None:
        st.write("Por favor, sube al menos un archivo Excel.")





    if datos_stock is not None and datos_posicion is not None:
        # Realizar el merge de df_stock y df_reposicionamiento según la columna "Pallet"
        


        df_concatenado = pd.concat([df_stock_almacenaje,df_posicion_almacenaje ], axis=0, ignore_index=True)
        df_concatenado['Vencimiento'] = pd.to_datetime(df_concatenado['Vencimiento'], errors='coerce').dt.strftime('%d-%m-%Y')

        # Tamaño de la población
        N = len(df_concatenado)
        st.write(f"Tamaño df_stock (número de filas en df_stock): {N}")

        st.write(df_concatenado)

        def convert_df_to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                writer.close()  # No es necesario el 'save()', cerrando con 'close()' dentro del contexto
            processed_data = output.getvalue()  # Obtener los datos del archivo en formato binario
            return processed_data

        # Crear un archivo Excel de un DataFrame (en este caso df_merged)
        excel_file = convert_df_to_excel(df_concatenado)

        # Botón para descargar el archivo Excel
        st.download_button(
            label="Download data as Excel Almacenaje",
            data=excel_file,
            file_name="df_merged_almacenaje.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.write("Para realizar el merge, carga ambos archivos: 'Informe Stock con Operacion' y 'Reporte Posicionamiento'.")

with tab3:
    
    st.title("Control Picking")


    # Procesar y mostrar cada archivo si se ha subido
    if datos_stock is not None:
        # Leer el archivo de stock
        df_stock_picking = df_stock.dropna(subset=["Pallet"])
        df_stock_picking = df_stock_picking[df_stock_picking["Pallet"] != 0]
        df_stock_picking = df_stock_picking[df_stock_picking['Nivel'] == 1]
        df_stock_picking["Pallet"] = df_stock_picking["Pallet"].astype(int)
        # Mostrar el DataFrame resultante
        # st.write("Datos de Stock:")
        # st.write(df_stock["Pallet"])
        # st.write(df_stock)


    if datos_reposicionamiento is not None:
        # Leer el archivo de reposicionamiento
        df_reposicionamiento_picking = df_reposicionamiento.dropna(subset=["Pallet"])
        df_reposicionamiento_picking = df_reposicionamiento_picking[df_reposicionamiento_picking["Pallet"] != 0]
        df_reposicionamiento_picking = df_reposicionamiento_picking[df_reposicionamiento_picking["Tipo de Movimiento Alt"].isin(["PIU", "PIB"])]
        df_reposicionamiento_picking["Pallet"] = df_reposicionamiento_picking["Pallet"].astype(int)
        df_reposicionamiento_picking['Fecha (Fin Movimiento)'] = pd.to_datetime(df_reposicionamiento_picking['Fecha (Fin Movimiento)'])
        df_reposicionamiento_picking['Dias_Laborables'] = df_reposicionamiento_picking['Fecha (Fin Movimiento)'].apply(lambda x: cal.get_working_days_delta(x.date(), datetime.now().date()))
        df_reposicionamiento_picking['Universo'] = (df_reposicionamiento_picking['Dias_Laborables'] == 1).astype(int)
        df_reposicionamiento_picking = df_reposicionamiento_picking[df_reposicionamiento_picking['Universo'] == 1]



        df_agrupado = df_reposicionamiento_picking.groupby('Posición Destino').agg({'Bultos': 'sum','Unidades': 'sum','ID Art': 'count',"Artículo":"first","Rubro":"first"}).reset_index()

        df_agrupado = df_agrupado.sort_values(by='Bultos', ascending=False)
        df_agrupado['Porcentaje_Acumulado_Bultos'] = df_agrupado['Bultos'].cumsum() / df_agrupado['Bultos'].sum()
        # st.write(df_agrupado)

        # Ordenar por 'ID Art' en orden descendente y calcular porcentaje acumulado para 'ID Art'
        df_agrupado = df_agrupado.sort_values(by='ID Art', ascending=False)
        df_agrupado['Porcentaje_Acumulado_ID_Art'] = df_agrupado['ID Art'].cumsum() / df_agrupado['ID Art'].sum()

        # Filtrar las filas cuyo porcentaje acumulado de 'Bultos' o 'ID Art' esté dentro del 20% más alto
        df_top_20_bultos = df_agrupado[df_agrupado['Porcentaje_Acumulado_Bultos'] <= 0.80]
        df_top_20_id_art = df_agrupado[df_agrupado['Porcentaje_Acumulado_ID_Art'] <= 0.80]

        # Combinar los DataFrames para ver las filas que aparecen en el 20% más alto de ambos casos
        df_reposicionamiento_picking = pd.concat([df_top_20_bultos, df_top_20_id_art]).drop_duplicates()

        # Crear una figura para la curva de Pareto de Bultos e ID Art

        # Mostrar el DataFrame resultante
        # st.write("Datos de Reposicionamiento:")
        # st.write(df_reposicionamiento)
        # st.write(df_reposicionamiento)



    if datos_posicion is not None:
        # Leer el archivo de posicion
        pass
        # Mostrar el DataFrame resultante
        # st.write("Datos de Posición:")
        # st.write(df_posicion)

    # Mensaje si no se ha subido ningún archivo
    if datos_stock is None and datos_reposicionamiento is None and datos_posicion is None:
        st.write("Por favor, sube al menos un archivo Excel.")

    if datos_stock is not None and datos_reposicionamiento is not None:

        df_agrupado = df_agrupado.sort_values(by='Porcentaje_Acumulado_ID_Art', ascending=False)


    if datos_stock is not None and datos_reposicionamiento is not None:
        # Realizar el merge de df_stock y df_reposicionamiento según la columna "Pallet"
        df_merged_picking = pd.merge(df_stock_picking, df_reposicionamiento_picking, left_on='Posicion', right_on='Posición Destino', how='inner')
        df_merged_picking = df_merged_picking[["Artículo","Descripcion Articulo","Pasillo","Columna","Nivel","Sector","Posicion","Bultos_x","Unidades_x","Vencimiento"]]
        df_merged_picking['Vencimiento'] = pd.to_datetime(df_merged_picking['Vencimiento'], errors='coerce').dt.strftime('%d-%m-%Y')
        df_merged_picking = df_merged_picking.rename(columns={'Bultos_x': 'Bultos', 'Unidades_x': 'Unidades'})
        # Tamaño de la población
        N = len(df_stock_picking)
        st.write(f"Tamaño de la población (número de filas en df_merged_picking): {N}")
        N = len(df_merged_picking)
        st.write(f"Tamaño de la muestra (número de filas en df_merged_picking): {N}")

        st.write(df_merged_picking)
        

        def convert_df_to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                writer.close()  # No es necesario el 'save()', cerrando con 'close()' dentro del contexto
            processed_data = output.getvalue()  # Obtener los datos del archivo en formato binario
            return processed_data

        # Crear un archivo Excel de un DataFrame (en este caso df_merged)
        excel_file = convert_df_to_excel(df_merged_picking)

        # Botón para descargar el archivo Excel
        st.download_button(
            label="Download data as Excel Picking",
            data=excel_file,
            file_name="df_merged_picking.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


    else:
        st.write("Para realizar el merge, carga ambos archivos: 'Informe Stock con Operacion' y 'Reporte Posicionamiento'.")
