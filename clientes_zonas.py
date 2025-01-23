import streamlit as st
import pandas as pd
import numpy as np
import requests
import folium
from streamlit_folium import folium_static
import json
from shapely.geometry import Point, Polygon
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import shape
from matplotlib.colors import ListedColormap
import matplotlib.colors as mcolors
import pydeck as pdk
from shapely import wkt
from io import BytesIO
import plotly.express as px
from datetime import datetime, timedelta
import random
from workalendar.america import Argentina

st.set_page_config(page_title="Maestro Clientes Zonas", layout="wide")


cal = Argentina()

dias_mapping = {
    'Monday': 'Lunes',
    'Tuesday': 'Martes',
    'Wednesday': 'Miercoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes',
    "Saturday":"Sabado",
    "Sunday":"Domingo"
}

#-----------MAESTRO ZONAS------------#

with st.expander("Carga de archivos"):

    
    ruta_excel_zonas = st.file_uploader("Maestro Zonas", type="xlsx")
    ruta_excel_clientes= st.file_uploader("Maestro Clientes", type="xlsx")
    ruta_geojson = st.file_uploader("Cargar archivo GeoJSON", type="geojson")
    ruta_performance = st.file_uploader("Reporte Performance Fleet", type="xlsx")

    if ruta_excel_zonas is not None:
    
        df_maestro_zonas = pd.read_excel(ruta_excel_zonas)

    if ruta_excel_clientes is not None:
        
        df_maestro_clientes = pd.read_excel(ruta_excel_clientes,skiprows=2)
        df_maestro_clientes = df_maestro_clientes.dropna(subset=['Idclienteorden',"Ped id"])

    if ruta_geojson is not None:
       
        df_maestro_departamentos = gpd.read_file(ruta_geojson)
        columns_to_select = ['gid', 'objeto', 'fna', 'gna', 'nam', 'in1', 'fdc', 'sag', 'Zona', 'geometry']
        df_maestro_departamentos = df_maestro_departamentos[columns_to_select]

    if ruta_performance is not None: 

        df_performance_fleet = pd.read_excel(ruta_performance,skiprows=2)

        df_performance_fleet['Categoria Vehiculo'] = df_performance_fleet['Categoria Vehiculo'].astype(str)
        df_performance_fleet['NumeroSemana'] = df_performance_fleet['Fechainicio'].dt.isocalendar().week
        df_performance_fleet['DiaDelAño'] = df_performance_fleet['Fechainicio'].dt.dayofyear
        df_performance_fleet['DiaSemana'] = df_performance_fleet['Fechainicio'].dt.day_name()

        df_performance_fleet['Fechacreacionped'] = pd.to_datetime(df_performance_fleet['Fechacreacionped'])
        df_performance_fleet["DiadelAñoPedido"] = df_performance_fleet['Fechacreacionped'].dt.dayofyear
        df_performance_fleet['DiaSemana_Pedido'] = df_performance_fleet['Fechacreacionped'].dt.day_name()

        # Convertir la columna "DiaSemana" al valor numérico de día de la semana (0=Lunes, ..., 6=Domingo)
        df_performance_fleet['DiaNumeroSemana'] = df_performance_fleet['Fechainicio'].dt.weekday

        # Mostrar el DataFrame resultante
        print(df_performance_fleet)

        df_performance_fleet = df_performance_fleet[df_performance_fleet["DiaDelAño"]>=309]

        df_performance_fleet['Canal'] = df_performance_fleet.apply(
            lambda row: "Semi" if "Semi" in row['Categoria Vehiculo'] 
            else ("Retira Cliente" if "Retira Cliente" in row['Tipojornada'] 
                else row['Tipojornada']), 
            axis=1
        )

        df_performance_fleet = df_performance_fleet[df_performance_fleet["Canal"].isin(["CDR Mayorista"])]
        df_performance_fleet = df_performance_fleet[df_performance_fleet["Estadoviaje"] != "Cancelado"]
        df_performance_fleet = df_performance_fleet[df_performance_fleet["Estadoparada"].isin(["Entregado rendido","Insertado en WMS","Entrega Parcial por Cliente","Entrega parcial por iFLOW","Entregado"])]
        df_performance_fleet = df_performance_fleet[~df_performance_fleet["Transporte"].isin(["Retira Cliente", "No sale"])]

        df_performance_fleet = gpd.GeoDataFrame(df_performance_fleet,geometry=gpd.points_from_xy(df_performance_fleet['Longitud'], df_performance_fleet['Latitud']),crs="EPSG:4326")  # Define el sistema de coordenadas (WGS 84))



#-----------MAESTRO DEPARTAMENTOS------------#



tab1,tab2,tab3,tab4 = st.tabs(["Frecuenciar Zonas","Frecuenciar Departamentos", "Frecuenciar Maestro Clientes","Analisis Zonas"])


with tab1:

    st.title("Frecuenciar Zonas")

    if ruta_excel_zonas is not None:

        df_maestro_zonas = st.data_editor(df_maestro_zonas)


with tab2:

    st.title("Frecuenciar Departamentos")

    if ruta_geojson is not None:

        def convert_gdf_to_geojson(gdf):
            output = BytesIO()
            gdf.to_file(output, driver="GeoJSON")
            output.seek(0)  # Reposicionar el puntero al inicio del archivo
            return output.getvalue()  # Retornar los datos del archivo en formato binario

        
        df_maestro_departamentos['geometry'] = df_maestro_departamentos['geometry'].apply(lambda x: x.wkt)

        edited_df = st.data_editor(df_maestro_departamentos)

        edited_df = edited_df.merge(df_maestro_zonas, on="Zona", how="left")

        edited_df['geometry'] = edited_df['geometry'].apply(wkt.loads)

        edited_gdf = gpd.GeoDataFrame(edited_df, geometry='geometry', crs="EPSG:4326")

        edited_gdf_filtered = edited_gdf.drop(columns=["Frecuencia 1", "Frecuencia 2"])

        # Crear un archivo GeoJSON a partir del GeoDataFrame (en este caso edited_gdf)
        geojson_file_departamentos = convert_gdf_to_geojson(edited_gdf_filtered)

        # Botón para descargar el archivo GeoJSON
        st.download_button(
            label="Download data as GeoJSON Departamentos",
            data=geojson_file_departamentos,
            file_name="edited_data.geojson",
            mime="application/geo+json"
        )

        edited_gdf_zona = edited_gdf.dissolve(by="Zona").reset_index()

        # Crear un archivo GeoJSON a partir del GeoDataFrame (en este caso edited_gdf)
        geojson_file = convert_gdf_to_geojson(edited_gdf_zona)

        # Botón para descargar el archivo GeoJSON
        st.download_button(
            label="Download data as GeoJSON",
            data=geojson_file,
            file_name="edited_data.geojson",
            mime="application/geo+json"
        )
        

with tab3:

    st.title("Frecuenciar Maestro Clientes")

    if ruta_geojson is not None:


        df_maestro_clientes = gpd.GeoDataFrame(df_maestro_clientes,geometry=gpd.points_from_xy(df_maestro_clientes['Longitud'], df_maestro_clientes['Latitud']),crs="EPSG:4326")  # Define el sistema de coordenadas (WGS 84))
        
        gdf_resultado = gpd.sjoin(df_maestro_clientes, edited_gdf_zona, how="left", predicate="intersects")

        gdf_resultado['geometry'] = gdf_resultado['geometry'].apply(lambda x: x.wkt)
        
        st.dataframe(gdf_resultado)

        def convert_df_to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                writer.close()  # No es necesario el 'save()', cerrando con 'close()' dentro del contexto
            processed_data = output.getvalue()  # Obtener los datos del archivo en formato binario
            return processed_data

        # Crear un archivo Excel de un DataFrame (en este caso df_merged)
        excel_file = convert_df_to_excel(gdf_resultado)

        # Botón para descargar el archivo Excel
        st.download_button(
            label="Download data as Excel Clientes",
            data=excel_file,
            file_name="gdf_resultado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        gdf_resultado['geometry'] = gdf_resultado['geometry'].apply(wkt.loads)

        gdf_resultado = gpd.GeoDataFrame(gdf_resultado, geometry='geometry', crs="EPSG:4326")

        gdf_resultado['Planta_Ped_id'] = gdf_resultado['Planta'].astype(str) + "" + gdf_resultado['Ped id'].astype(str)




with tab4: 

    st.title("Analisis Zonas CDR Mayorista")

    if ruta_geojson is not None:

        

        df_merged = gpd.sjoin(df_performance_fleet, edited_gdf_zona, how="left", predicate="intersects")

        

        dias_semana_map = {"Lunes": 0, "Martes": 1, "Miercoles": 2, "Jueves": 3, "Viernes": 4, "Sabado": 5, "Domingo": 6}

        df_merged = df_merged.dropna(subset=["Frecuencia 1", "Frecuencia 2"])

        df_merged["Frecuencia 1 Num"] = df_merged["Frecuencia 1"].map(dias_semana_map)
        df_merged["Frecuencia 2 Num"] = df_merged["Frecuencia 2"].map(dias_semana_map)

        # Convertir la columna 'Fechacreacionped' a datetime
        df_merged["Fechacreacionped"] = pd.to_datetime(df_merged["Fechacreacionped"])

        # Función para calcular la próxima fecha laborable
        def proxima_fecha_laborable(fecha):
            fecha += timedelta(days=1)
            # Avanzar al siguiente día si no es laborable
            while not cal.is_working_day(fecha):
                fecha += timedelta(days=1)
            return fecha

        # Aplicar la función al DataFrame
        df_merged["FechaProximaLaborable"] = df_merged["Fechacreacionped"].apply(proxima_fecha_laborable)

        # Calcular el día del año de la fecha de entrega
        df_merged["DiadelAñoEntrega"] = df_merged["FechaProximaLaborable"].dt.dayofyear

        # Eliminar la columna auxiliar si no es necesaria
            
        def calcular_dia_frecuencia(row):

            dia_entrega = row["DiadelAñoEntrega"]
            dia_semana_entrega = (dia_entrega % 7) - 1  # Día de la semana de "DiadelAñoEntrega"
            
            # Calcular diferencias en días para cada frecuencia
            dif1 = (row["Frecuencia 1 Num"] - dia_semana_entrega) % 7 #2
            dif2 = (row["Frecuencia 2 Num"] - dia_semana_entrega) % 7 #4
            
            # Tomar la menor diferencia y ajustar el día del año
            min_dif = min(dif1, dif2)

            return dia_entrega + min_dif

        # Aplicar la función al DataFrame
        df_merged["DiadelAñoFrecuencia"] = df_merged.apply(calcular_dia_frecuencia, axis=1)

        # df_merged["DiaDelAño_Frecuencia"] = df_merged.apply(calcular_dia_del_año_frecuencia, axis=1)

        anio_base = 2024
        df_merged["FechaInicio_Frecuencia"] = df_merged["DiadelAñoFrecuencia"].apply(lambda x: datetime(anio_base, 1, 1) + timedelta(days=x - 1))
        df_merged["DiaSemana_Frecuencia"] = df_merged["FechaInicio_Frecuencia"].dt.day_name()

        df_merged["FechaInicio_Entrega"] = df_merged["DiadelAñoEntrega"].apply(lambda x: datetime(anio_base, 1, 1) + timedelta(days=x - 1))
        df_merged["DiaSemana_Entrega"] = df_merged["FechaInicio_Entrega"].dt.day_name()


        df_heatmap = df_merged.groupby("Nombreboca").agg({"Zona":"first","geometry": "first","NumeroSemana":"nunique","DiaDelAño": "nunique"}).reset_index()
        df_heatmap = df_heatmap.set_geometry("geometry")

        geojson_data = edited_gdf.__geo_interface__

        # Configuración del mapa
        view_state = pdk.ViewState(
            latitude=df_heatmap.geometry.y.mean(),  # Centro en el promedio de latitudes
            longitude=df_heatmap.geometry.x.mean(),  # Centro en el promedio de longitudes
            zoom=12,  # Nivel de zoom
            pitch=50  # Ángulo del mapa
        )

        column_layer = pdk.Layer(
            "ColumnLayer",
            data=df_heatmap,
            get_position="geometry.coordinates",
            get_elevation="DiaDelAño",
            elevation_scale=100,
            radius=50,
            get_fill_color=[0, 100,50, 140],
            pickable=True,
            auto_highlight=True,
        )

        # Obtener valores únicos de "Zona" desde el GeoJSON
        zonas = sorted({feature["properties"]["Zona"] for feature in geojson_data["features"]})

        # Crear una paleta de colores usando Matplotlib
        colormap = plt.get_cmap("tab20")  # Cambia "viridis" por la paleta que prefieras
        norm = plt.Normalize(vmin=0, vmax=len(zonas) - 1)  # Normalización para el número de zonas
        colors = [list(np.array(colormap(norm(i))) * 255)[:3] + [140] for i in range(len(zonas))]

        # Asignar colores a cada zona
        color_map = dict(zip(zonas, colors))

        # Asignar colores al GeoJSON directamente en las propiedades
        for feature in geojson_data["features"]:
            feature["properties"]["color"] = color_map[feature["properties"]["Zona"]]

        # Crear la capa de polígonos
        polygon_layer = pdk.Layer(
            "GeoJsonLayer",             # Tipo de capa GeoJSON
            geojson_data,               # Datos GeoJSON
            pickable=True,              # Habilitar interacción
            stroked=True,               # Mostrar bordes
            filled=True,                # Rellenar los polígonos
            extruded=False,             # No usar altura 3D
            line_width_min_pixels=2,    # Grosor del borde
            get_fill_color="properties.color",  # Colorear según "Zona"
            get_line_color=[255, 255, 255],  # Color del borde
        )

        # heatmap_layer = pdk.Layer(
        #     "HeatmapLayer",
        #     data=df_heatmap,  # Datos del GeoDataFrame con puntos
        #     get_position="geometry.coordinates",  # Extraer coordenadas de los puntos
        #     get_weight="DiaDelAño",  # Usar la columna 'Repeticiones' como peso
        #     radiusPixels=60,  # Radio de influencia de cada punto
        # )
        # Crear el mapa con el HeatmapLayer incluido
        mapa = pdk.Deck(
            layers=[polygon_layer,column_layer],
            initial_view_state=view_state,
            tooltip={"text": "Polígono: {Zona}\nParadas: {DiaDelAño}\nNombreboca: {Nombreboca}\nDepartamento: {nam}"}
        )

        # Mostrar el mapa en Streamlit
        st.pydeck_chart(mapa)


        df_heatmap['geometry'] = df_heatmap['geometry'].apply(lambda x: x.wkt)



        paradas_dia = df_merged.groupby(["DiaDelAño","Fechainicio"]).agg({"Nombreboca":"nunique"}).reset_index()


        # Crear el gráfico de barras
        fig = px.bar(
            paradas_dia,
            x='Fechainicio',
            y='Nombreboca',
            title='Cantidad de Paradas por Fecha',
            labels={'Fecha': 'Fecha', 'Cantidad de Paradas': 'Cantidad de Paradas'},
            text='Nombreboca'  # Muestra los valores encima de las barras
        )

        # Personalizar el diseño
        fig.update_traces(marker_color='blue', textposition='outside')
        fig.update_layout(
            xaxis_title='Fecha',
            yaxis_title='Nombreboca',
            title_x=0.5  # Centrar el título
        )

        # Mostrar el gráfico
        st.plotly_chart(fig)

        paradas_dia_nombre = df_merged.groupby(["NumeroSemana","DiaSemana"]).agg({"Nombreboca":"nunique"}).reset_index()
        paradas_dia_nombre = paradas_dia_nombre.groupby("DiaSemana").agg({"Nombreboca":"mean"}).reset_index()
        st.write(paradas_dia_nombre)

        paradas_dia_nombre = df_merged.groupby(["NumeroSemana","DiaSemana","Zona","Frecuencia 1","Frecuencia 2"]).agg({"Nombreboca":"nunique"}).reset_index()
        paradas_dia_nombre = paradas_dia_nombre.groupby(["Zona","Frecuencia 1","Frecuencia 2"]).agg({"Nombreboca":"sum"}).reset_index()
        st.write(paradas_dia_nombre)

        paradas_dia_2 = df_merged.groupby(["DiadelAñoFrecuencia", "FechaInicio_Frecuencia", "Zona"]).agg({"Nombreboca": "nunique"}).reset_index()

        # Crear el gráfico de barras apiladas
        fig_2 = px.bar(
            paradas_dia_2,
            x='FechaInicio_Frecuencia',
            y='Nombreboca',
            color='Zona',  # Apilar las columnas según los valores de la columna 'Zona'
            title='Cantidad de Paradas por Fecha (Apiladas por Zona)',
            labels={'FechaInicio_Frecuencia': 'Fecha', 'Nombreboca': 'Cantidad de Paradas', 'Zona': 'Zona'},
            text='Nombreboca'  # Muestra los valores encima de las barras
        )

        # Personalizar el diseño
        fig_2.update_traces(textposition='outside')
        fig_2.update_layout(
            xaxis_title='Fecha',
            yaxis_title='Cantidad de Paradas',
            title_x=0.5,  # Centrar el título
            barmode='stack'  # Configurar las barras como apiladas
        )

        # Mostrar el gráfico
        st.plotly_chart(fig_2)


        df_merged['geometry'] = df_merged['geometry'].apply(lambda x: x.wkt)
        df_merged['DiaSemana_Pedido'] = df_merged['DiaSemana_Pedido'].replace(dias_mapping)
        df_merged['DiaSemana_Entrega'] = df_merged['DiaSemana_Entrega'].replace(dias_mapping)
        df_merged['DiaSemana_Frecuencia'] = df_merged['DiaSemana_Frecuencia'].replace(dias_mapping)

        df_merged["Cumple"] = df_merged.apply(lambda row: "SI" if row["DiaSemana_Entrega"] == row["DiaSemana_Frecuencia"] else "NO",axis=1)


        st.dataframe(df_merged[["Ped Cliente","Fechacreacionped","DiaSemana_Pedido","DiadelAñoPedido","DiadelAñoEntrega","DiaSemana_Entrega","Frecuencia 1","Frecuencia 1 Num","Frecuencia 2","Frecuencia 2 Num","DiadelAñoFrecuencia","FechaInicio_Frecuencia","DiaSemana_Frecuencia"]])

        # Contar las ocurrencias de "SI" y "NO"
        df_concatenado_estados = df_merged["Cumple"].value_counts().reset_index()
        df_concatenado_estados.columns = ['Cumple', 'Cantidad']

        # Mostrar los datos en Streamlit
        st.write(df_concatenado_estados)

        # Crear un gráfico de barras usando Plotly
        fig_2 = px.bar(
            df_concatenado_estados, 
            x='Cumple', 
            y='Cantidad', 
            title="Frecuencia de Cumplimiento",
            labels={'Cumple': 'Cumple', 'Cantidad': 'Cantidad'},
            text='Cantidad'  # Mostrar los valores sobre las barras
        )

        # Personalizar el diseño del gráfico (opcional)
        fig_2.update_traces(textposition='outside')  # Mostrar el texto fuera de las barras
        fig_2.update_layout(
            xaxis_title="Cumple",
            yaxis_title="Cantidad",
            title_x=0.5  # Centrar el título
        )

        # Mostrar el gráfico en Streamlit
        st.plotly_chart(fig_2)


















# ruta_geojson = r"C:\Users\sscalabrini\Desktop\Mapas MILONGA\Simulación CDR Mayorista\Datos\maestro_zonas_departamentos.geojson"
# df_maestro_departamentos = gpd.read_file(ruta_geojson)
# df_maestro_departamentos = df_maestro_departamentos.iloc[:, :-3].join(df_maestro_departamentos.iloc[:, -1])

# df_maestro_departamentos = df_maestro_departamentos.merge(df_maestro_zonas, on="Zona", how="left")
# df_maestro_departamentos['geometry'] = df_maestro_departamentos['geometry'].apply(lambda x: x.wkt)

# edited_df = st.data_editor(df_maestro_departamentos)

# edited_df['geometry'] = edited_df['geometry'].apply(wkt.loads)

# edited_gdf_zona = gpd.GeoDataFrame(edited_df, geometry='geometry', crs="EPSG:4326")


# if st.button("Guardar cambios en GeoJSON"):
#     edited_gdf.to_file(ruta_geojson, driver="GeoJSON")
#     st.success(f"Archivo guardado exitosamente en: {ruta_geojson}")


# #-----------CONSOLIDACIÓN DE DEPARTAMENTOS EN ZONAS ------------#


# df_zonas = edited_gdf.dissolve(by="Zona").reset_index()


# dias_mapping = {
#     'Lunes': 'Monday',
#     'Martes': 'Tuesday',
#     'Miercoles': 'Wednesday',
#     'Jueves': 'Thursday',
#     'Viernes': 'Friday',
#     "Sabado":"Saturday"
# }

# dia_pesos = {
#     'Monday': 1,
#     'Tuesday': 2,
#     'Wednesday': 3,
#     'Thursday': 4,
#     'Friday': 5,
#     "Saturday":6
# }

# dias_orden = pd.CategoricalDtype(categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',"Saturday"], ordered=True)

# # # Reemplazar los valores en ambas columnas
# df_zonas['Frecuencia 1'] = df_zonas['Frecuencia 1'].replace(dias_mapping)
# df_zonas['Frecuencia 2'] = df_zonas['Frecuencia 2'].replace(dias_mapping)


# #-----------PARADAS FLEET------------#

# # Ruta del archivo CSV
# ruta_csv = r"C:\Users\sscalabrini\Desktop\Mapas MILONGA\Simulación CDR Mayorista\Datos\Detalle de viajes fleet 3 - Performance.xlsx"
# df = pd.read_excel(ruta_csv,skiprows=2)

# df['Categoria Vehiculo'] = df['Categoria Vehiculo'].astype(str)
# df['NumeroSemana'] = df['Fechainicio'].dt.isocalendar().week
# df['DiaSemana'] = df['Fechainicio'].dt.day_name()



# df['Canal'] = df.apply(
#     lambda row: "Semi" if "Semi" in row['Categoria Vehiculo'] 
#     else ("Retira Cliente" if "Retira Cliente" in row['Tipojornada'] 
#           else row['Tipojornada']), 
#     axis=1
# )

# df = df[df["Canal"].isin(["CDR Mayorista"])]
# df = df[df["Estadoviaje"] != "Cancelado"]
# df = df[df["Estadoparada"].isin(["Entregado rendido","Insertado en WMS","Entrega Parcial por Cliente","Entrega parcial por iFLOW","Entregado"])]
# df = df[~df["Transporte"].isin(["Retira Cliente", "No sale"])]



# #--------------PESOS POR FECHA Y CANAL----------------------#

# resultado = df.groupby(['Canal', 'Fechainicio'])['Parada Peso'].sum().reset_index()
# resultado = resultado.groupby("Canal")["Parada Peso"].mean().reset_index()

# #--------------CANTIDAD DE FRECUENCIAS POR BOCA Y POR SEMANA REALES----------#

# frecuencias = df.groupby(['NumeroSemana', 'Nombreboca',"Canal"])['DiaSemana'].nunique().reset_index()


# conteos = frecuencias['DiaSemana'].value_counts()






# #--------------JOIN DE PARADAS CON MAPAS POLIGONOS-----------------#

# gdf_points = gpd.GeoDataFrame(
#     df,
#     geometry=gpd.points_from_xy(df['Longitud'], df['Latitud']),
#     crs="EPSG:4326"  # Define el sistema de coordenadas (WGS 84)
# )

# gdf_resultado = gpd.sjoin(gdf_points, df_zonas, how="left", predicate="intersects")



# # gdf_resultado['geometry'] = gdf_resultado['geometry'].apply(lambda geom: geom.wkt if geom else None)

# gdf_resultado['DiaSemanaPeso'] = gdf_resultado['DiaSemana'].map(dia_pesos)
# gdf_resultado['Frecuencia1Peso'] = gdf_resultado['Frecuencia 1'].map(dia_pesos)
# gdf_resultado['Frecuencia2Peso'] = gdf_resultado['Frecuencia 2'].map(dia_pesos)

# # Calcular las distancias a "Dia Semana"
# gdf_resultado['DistanciaF1'] = abs(gdf_resultado['DiaSemanaPeso'] - gdf_resultado['Frecuencia1Peso'])
# gdf_resultado['DistanciaF2'] = abs(gdf_resultado['DiaSemanaPeso'] - gdf_resultado['Frecuencia2Peso'])

# # Elegir el valor más cercano
# gdf_resultado['DiaSemanaCorrejido'] = gdf_resultado.apply(
#     lambda row: row['Frecuencia 1'] if row['DistanciaF1'] <= row['DistanciaF2'] else row['Frecuencia 2'],
#     axis=1
# )

# # Eliminar columnas auxiliares si no se necesitan

# # Mostrar el DataFrame en Streamlit
# # st.dataframe(gdf_resultado)

# gdf_resultado['DiaSemanaCorrejido'] = gdf_resultado['DiaSemanaCorrejido'].astype(dias_orden)
# gdf_resultado['Fecha'] = gdf_resultado['NumeroSemana'].astype(str) + "-" + gdf_resultado['DiaSemanaCorrejido'].astype(str)



# #------------RESULTADOS POR DIA Y SEMANA EN VIAJES Y PESO ------------# 

# gdf_resumen = gdf_resultado.groupby(['NumeroSemana', 'DiaSemanaCorrejido',"Fecha"]).agg({"Viaje":"nunique","Parada Peso":"sum","Nombreboca":"nunique"}).reset_index()
# gdf_resumen = gdf_resumen[gdf_resumen["Parada Peso"] != 0]
# gdf_resumen['Parada Peso'] = (gdf_resumen['Parada Peso'] // 1000).astype(int)
# # gdf_resumen = gdf_resumen.groupby("Fecha").agg({"Viaje":"nunique"}).reset_index()

# st.dataframe(gdf_resumen)



# df['DiaSemana'] = df['DiaSemana'].astype(dias_orden)
# df = df.groupby(['NumeroSemana', 'DiaSemana']).agg({"Viaje":"nunique","Parada Peso":"sum","Nombreboca":"nunique"}).reset_index()
# df['Fecha'] = df['NumeroSemana'].astype(str) + "-" + df['DiaSemana'].astype(str)
# df = df[df["Parada Peso"] != 0]
# df['Parada Peso'] = (df['Parada Peso'] // 1000).astype(int)

# st.dataframe(df)


# #-------------RESUMEN PESOS POR ZONA------------#

# gdf_paradas = gdf_resultado.drop_duplicates(subset=["Viaje", "Nombreboca"], keep="first").groupby(["Zona","Frecuencia 1","Frecuencia 2"]).agg({"Fecha":"nunique","Nombreboca":"count"})
# gdf_peso = gdf_resultado.groupby(["Zona","Frecuencia 1","Frecuencia 2"]).agg({"Parada Peso":"sum","Fecha":"nunique"})





# #---------------DIAS MAS FRECUENTES PARA CADA ZONA----------#

# top_dias = (
#     gdf_resultado.groupby(["Zona","Frecuencia 1","Frecuencia 2"])["DiaSemana"]
#     .apply(lambda x: x.value_counts().head(2).index.tolist())
#     .reset_index(name="Top_DiaSemana")
# )

# st.dataframe(top_dias)



# import plotly.express as px

# # Crear el gráfico de barras
# fig = px.bar(
#     gdf_resumen,
#     x='Fecha',
#     y='Nombreboca',
#     title='Cantidad de Paradas por Fecha',
#     labels={'Fecha': 'Fecha', 'Cantidad de Paradas': 'Cantidad de Paradas'},
#     text='Nombreboca'  # Muestra los valores encima de las barras
# )

# promedio = gdf_resumen['Nombreboca'].mean()

# fig.add_shape(
#     type="line",
#     x0=gdf_resumen['Fecha'].min(),  # Fecha inicial
#     x1=gdf_resumen['Fecha'].max(),  # Fecha final
#     y0=promedio,
#     y1=promedio,
#     line=dict(color="red", width=2, dash="dash"),  # Línea roja punteada
# )

# # Agregar anotación con el valor del promedio
# fig.add_annotation(
#     x=gdf_resumen['Fecha'].max(),  # Posición cerca del final del eje x
#     y=promedio*1.10,
#     text=f"Promedio: {promedio:.2f}",
#     showarrow=False,
#     font=dict(color="red", size=12),
#     align="right",
# )

# # Personalizar el diseño
# fig.update_traces(marker_color='blue', textposition='outside')
# fig.update_layout(
#     xaxis_title='Fecha',
#     yaxis_title='Nombreboca',
#     title_x=0.5  # Centrar el título
# )

# # Mostrar el gráfico
# st.plotly_chart(fig)


# # Crear el gráfico de barras
# fig = px.bar(
#     df,
#     x='Fecha',
#     y='Nombreboca',
#     title='Cantidad de Paradas',
#     labels={'Fecha': 'Fecha', 'Cantidad de Paradas': 'Cantidad de Paradas'},
#     text='Nombreboca'  # Muestra los valores encima de las barras
# )


# fig.add_shape(
#     type="line",
#     x0=gdf_resumen['Fecha'].min(),  # Fecha inicial
#     x1=gdf_resumen['Fecha'].max(),  # Fecha final
#     y0=promedio,
#     y1=promedio,
#     line=dict(color="red", width=2, dash="dash"),  # Línea roja punteada
# )

# # Agregar anotación con el valor del promedio
# fig.add_annotation(
#     x=df['Fecha'].max(),  # Posición cerca del final del eje x
#     y=promedio*1.10,
#     text=f"Promedio: {promedio:.2f}",
#     showarrow=False,
#     font=dict(color="red", size=12),
#     align="right",
# )

# # Personalizar el diseño
# fig.update_traces(marker_color='blue', textposition='outside')
# fig.update_layout(
#     xaxis_title='Fecha',
#     yaxis_title='Nombreboca',
#     title_x=0.5  # Centrar el título
# )

# st.plotly_chart(fig)





# gdf_resultado['Parada Peso'] = pd.to_numeric(gdf_resultado['Parada Peso'], errors='coerce')


# #-------SUMA DE CANTIDAD DE PARADAS-----------#


# gdf_resultado = gdf_resultado.drop_duplicates(subset=["Viaje", "Nombreboca"], keep="first").groupby("Nombreboca").agg({"geometry": "first","Nombreboca": "size"}).rename(columns={"Nombreboca": "Repeticiones"}).reset_index()
# gdf_resultado = gdf_resultado.set_geometry("geometry")

# # st.dataframe(gdf_resultado)


# geojson_data = edited_gdf.__geo_interface__


# # Configuración del mapa
# view_state = pdk.ViewState(
#     latitude=gdf_resultado.geometry.y.mean(),  # Centro en el promedio de latitudes
#     longitude=gdf_resultado.geometry.x.mean(),  # Centro en el promedio de longitudes
#     zoom=12,  # Nivel de zoom
#     pitch=50  # Ángulo del mapa
# )


# # Crear la capa de polígonos
# polygon_layer = pdk.Layer(
#     "GeoJsonLayer",             # Tipo de capa GeoJSON
#     geojson_data,               # Datos GeoJSON
#     pickable=True,              # Habilitar interacción
#     stroked=True,               # Mostrar bordes
#     filled=True,                # Rellenar los polígonos
#     extruded=False,             # No usar altura 3D
#     line_width_min_pixels=2,    # Grosor del borde
#     get_fill_color=[0, 128, 255, 140],  # Color de relleno (RGBA)
#     get_line_color=[255, 255, 255]      # Color del borde
# )

# column_layer = pdk.Layer(
#     "ColumnLayer",
#     data=gdf_resultado,
#     get_position="geometry.coordinates",
#     get_elevation="Repeticiones",
#     elevation_scale=100,
#     radius=50,
#     get_fill_color=[0, 100,50, 140],
#     pickable=True,
#     auto_highlight=True,
# )

# # Crear el mapa
# mapa = pdk.Deck(
#     layers=[polygon_layer,column_layer],
#     initial_view_state=view_state,
#     tooltip={"text": "Polígono: {Zona}\nParadas: {Repeticiones}\nNombreboca: {Nombreboca}"}  # Personaliza las etiquetas (ajusta a tu GeoJSON)
# )

# # Mostrar el mapa en Streamlit
# st.pydeck_chart(mapa)