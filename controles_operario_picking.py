import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime


# App title
st.title("Escaneo y Control de Picking")

# URL de la hoja de Google Sheets
sheet_url = 'https://docs.google.com/spreadsheets/d/1J0YmuXlCFx_lg5DKGS_o_09nhkJaGVh7PLrjsyV2Nsc/edit?gid=0#gid=0'

# Extraer el ID de la hoja y obtener el enlace al CSV
sheet_id = sheet_url.split("/d/")[1].split("/")[0]
data_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv'


# Cachear los datos cargados desde Google Sheets
@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    df["Posicion"] = df["Posicion"].str.rstrip()
    df['Ordenar_primero'] = df['Posicion'].str.split(' - ').str[0].str[2:4]
    df['Ordenar_segundo'] = df['Posicion'].str.split(' - ').str[1].astype(int)
    df = df.sort_values(by=['Ordenar_primero', 'Ordenar_segundo']).drop(columns=['Ordenar_primero', 'Ordenar_segundo'])
    return df


# Cargar los datos
df = load_data(data_url)

# Guardar en session_state para modificar
if "df" not in st.session_state:
    st.session_state.df = df.copy()

# Inicializar estados si no existen
if "current_row" not in st.session_state:
    st.session_state.current_row = 0

if "HoraInicio" not in st.session_state:
    st.session_state.HoraInicio = {}

if "input_key" not in st.session_state:
    st.session_state.input_key = 0

if "escaneada_posicion" not in st.session_state:
    st.session_state.escaneada_posicion = ""


# Función para mostrar la información de cada fila
def mostrar_carta(data_row, posicion):
    # Mostrar tarjeta con datos
    card_html = f"""
    <div style="border:1px solid #ddd; border-radius:8px; padding:16px; margin:16px 0; box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);">
        <div style="padding:10px;">
            <h3 style="margin:0; font-size:1.5em;">Detalle de Posición: {data_row["Posicion"]}</h3>
        </div>
        <div style="padding:16px;">
            <p><strong>Artículo:</strong> {data_row["Descripcion Articulo"]}</p>
            <p><strong>Entidad:</strong> {data_row["Entidad"]}</p>
            <h3 style="margin:0; font-size:1.5em;">UxB: {data_row["Un.x Bulto"]}</h3>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

    # Verificar posición escaneada
    if posicion == data_row["Posicion"]:
        # Guardar hora de inicio
        if posicion not in st.session_state.HoraInicio:
            hora_inicio = datetime.now()
            st.session_state.HoraInicio[posicion] = hora_inicio.strftime("%d-%m-%Y %H:%M:%S")

        st.write(f"Hora de inicio: {st.session_state.HoraInicio[posicion]}")
        # Procesar información de picking
        articulo = st.number_input(f"Escanea el artículo para la posición {data_row['Posicion']}", min_value=0, value=None)
        cantidad_bultos = st.number_input("Confirma cantidad de bultos", min_value=0, value=0)

        # Actualizar DataFrame
        st.session_state.df.loc[st.session_state.df["Posicion"] == posicion, "Articulo Escaneado"] = articulo
        st.session_state.df.loc[st.session_state.df["Posicion"] == posicion, "Bultos Contados"] = cantidad_bultos
        st.session_state.df.loc[st.session_state.df["Posicion"] == posicion, "HoraInicio"] = st.session_state.HoraInicio[posicion]

        if st.button("Tarea Terminada"):
            # Finalizar tarea
            st.session_state.df.loc[st.session_state.df["Posicion"] == posicion, "HoraFin"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            st.session_state.current_row += 1
            st.experimental_rerun()
    else:
        st.warning("La posición ingresada no coincide con la posición actual.")


# Procesar filas
if st.session_state.current_row < len(st.session_state.df):
    current_row_data = st.session_state.df.iloc[st.session_state.current_row]
    posicion = st.text_input(
        "Escanea la posición",
        value=st.session_state.escaneada_posicion,
        key=f"input_{st.session_state.input_key}",
    )
    mostrar_carta(current_row_data, posicion)
else:
    st.success("Todas las posiciones han sido procesadas.")







