import streamlit as st
import pandas as pd
import base64
from pathlib import Path
from typing import Optional
from io import BytesIO

import streamlit as st
import streamlit.components.v1 as components

# Tell streamlit that there is a component called camera_input_live,
# and that the code to display that component is in the "frontend" folder

frontend_dir = (Path(__file__).parent / "frontend").absolute()
_component_func = components.declare_component(
    "qrcode_scanner", path=str(frontend_dir)
)


def qrcode_scanner(key: Optional[str] = None) -> Optional[BytesIO]:
    """
    Add a descriptive docstring
    """
    data: Optional[str] = _component_func(key=key)

    if data is None:
        return None
    

    # raw_data = b64_data.split(",")[1]  # Strip the data: type prefix

    # component_value = BytesIO(base64.b64decode(raw_data))
    component_value = data

    return component_value

# Carga de archivo dentro del expansor
with st.expander("Carga de archivos"):
    datos_stock = st.file_uploader("Informe Stock con Operacion", type="xlsx")

# Función para mostrar la información en formato de carta
def mostrar_carta(data_row):
    card_html = f"""
    <div style="border:1px solid #ddd; border-radius:8px; padding:16px; margin:16px 0; box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);">
        <div  padding:10px; border-radius:6px 6px 0 0;">
            <h3 style="margin:0; font-size:1.5em;">Detalle de Posición: {data_row["Posicion"]}</h3>
        </div>
        <div style="padding:16px;">
            <p><strong>Artículo:</strong> {data_row["Descripcion Articulo"]}</p>
            <p><strong>Pallet:</strong> {data_row["Pallet"]}</p>
            <p><strong>Cantidad:</strong> {data_row["Bultos"]}</p>
            <p><strong>Fecha de Ingreso:</strong> {data_row["Fecha Ingreso"]}</p>
            <p><strong>Fecha de Vencimiento:</strong> {data_row["Vencimiento"]}</p>
        </div>
        <div  padding:10px; border-radius:0 0 6px 6px; text-align:right;">
            <small>Última actualización: {data_row["Fecha Ingreso"]}</small>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# Lógica para procesar el archivo una vez cargado
if datos_stock is not None:
    # Cargar el Excel
    df = pd.read_excel(datos_stock)

    st.write(df)

    # Ingresar el valor de búsqueda en la columna "Posicion"
    

    posicion_buscada = st.text_input("Ingrese la posición a buscar:")


    text = qrcode_scanner()

    if text is not None:
        st.write(text)


    # Filtrar la fila que coincide con la posición buscada
    if posicion_buscada:
        resultado = df[df["Posicion"] == posicion_buscada]

        # Mostrar los datos en formato carta si se encuentra el resultado
        if not resultado.empty:
            mostrar_carta(resultado.iloc[0])  # Solo muestra la primera coincidencia
        else:
            st.write("No se encontró ninguna fila con esa posición.")
