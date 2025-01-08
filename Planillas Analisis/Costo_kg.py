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
import plotly.express as px

st.set_page_config(layout="wide")


#-----------PARADAS FLEET------------#

# Ruta del archivo CSV
ruta_csv = r"C:\Users\sscalabrini\Desktop\Maestros Micro\Detalle de viajes fleet 3 - Performance2.xlsx"
df = pd.read_excel(ruta_csv,skiprows=2)
df = df[df["Estadoviaje"] != "Cancelado"]
df = df[df["Estadoparada"].isin(["Entregado rendido","Insertado en WMS","Entrega Parcial por Cliente","Entrega parcial por iFLOW","Entregado"])]
df = df[~df["Transporte"].isin(["Retira Cliente", "No sale"])]

#-----------Tabla Dinamica------------#

# df = df.groupby(["Parada"]).agg({"Categoria Vehiculo": "first","Estadoparada":"first","Estadoviaje":"first","Tipojornada":"first","Provincia":"first","Dador":"first",
#                                  "Parada Peso": "sum",
#                                  "Km Plan":"first", 
#                                  "Costo Parada": "sum"}).reset_index()

df["Costo/kg"] = df["Costo Parada"]/df["Parada Peso"]

# # Crear un filtro para "Tipojornada"
# tipojornada_filter = st.multiselect(
#     "Filtrar por Tipojornada:",
#     options=df["Tipojornada"].unique(),
#     default=df["Tipojornada"].unique()  # Por defecto, selecciona todos
# )

# # Filtrar el DataFrame basado en la selección
# df = df[df["Tipojornada"].isin(tipojornada_filter)]
# df = df[df["Km Plan"]<250]

# # Crear gráfico de dispersión
# fig = px.scatter(
#     df,
#     x="Costo/kg",
#     y="Parada Peso",
#     title="Relación entre Costo/kg y Parada Peso",
#     labels={"Costo/kg": "Costo por kg", "Parada Peso": "Peso por parada"},
#     hover_data=["Parada", "Categoria Vehiculo"],  # Información adicional al pasar el cursor
#     range_x=[0,500],  # Establecer límites para el eje X
#     range_y=[0,500],
#     size_max=0.2,
#     color="Km Plan"   
# )

# fig.update_traces(marker=dict(size=3))  # Tamaño constante de los puntos, aquí 3 píxeles
# # Mostrar el gráfico en Streamlit
# st.plotly_chart(fig)

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Cargar los datos (puedes reemplazar esto con tu DataFrame real)
st.title("Regresión Lineal: Análisis de Influencia en 'Costo/kg'")
# df = st.session_state.df  # Usa el DataFrame de la sesión de Streamlit
df = df[(df["Costo/kg"] < 500) & (df["Parada Peso"] < 500)]

# Selección de variables independientes
st.write("Selecciona las variables que podrían influir en 'Costo/kg':")
variables_independientes = st.multiselect(
    "Variables independientes",
    options=[col for col in df.columns if col != "Costo/kg"],  # Excluye la variable dependiente
    default=["Viaje Paradas","Viaje Pedidos","Parada Peso","Km Plan"]
)

# Verificar selección de variables
if not variables_independientes:
    st.warning("Por favor, selecciona al menos una variable independiente.")
else:
    categoricas = df[variables_independientes].select_dtypes(include=["object"]).columns
    numericas = df[variables_independientes].select_dtypes(include=[np.number]).columns

    st.write(categoricas)

    # Aplicar codificación one-hot a las variables categóricas
    df_encoded = pd.get_dummies(df, columns=categoricas, drop_first=True)

    # Separar las variables independientes y dependientes
    X = df_encoded[[col for col in df_encoded.columns if col != "Costo/kg"]].fillna(0)
    y = df_encoded["Costo/kg"]
    # División del conjunto de datos en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Crear y entrenar el modelo de regresión lineal
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Predicciones
    y_pred = model.predict(X_test)

    # Evaluación del modelo
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    st.write("### Métricas del Modelo:")
    st.write(f"- **Error Cuadrático Medio (MSE):** {mse:.2f}")
    st.write(f"- **R² Score:** {r2:.2f}")

    # Mostrar los coeficientes de la regresión
    coef_df = pd.DataFrame({
        "Variable": X.columns,
        "Coeficiente": model.coef_
    }).sort_values(by="Coeficiente", ascending=False)

    st.write("### Coeficientes de la Regresión:")
    st.dataframe(coef_df)

    # Visualización del modelo
    st.write("### Predicción vs Real:")
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, alpha=0.7)
    plt.plot([y.min(), y.max()], [y.min(), y.max()], color="red", linestyle="--", linewidth=2)
    plt.xlabel("Valores Reales")
    plt.ylabel("Predicciones")
    plt.title("Regresión Lineal: Predicción vs Real")
    st.pyplot(plt)