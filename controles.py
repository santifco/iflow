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
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from pathlib import Path
from google.oauth2 import service_account

st.set_page_config(page_title="Controles Logisticos", layout="wide")

# credentials_info = st.secrets["gcp_service_account"]

credentials_info = {
    "type": "service_account",
    "project_id": "inbound-pattern-429101-c5",
    "private_key_id": "9dcc01743c917fb186294a8c6d228d4c2fb005bc",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDPvpK+357PGmvc
6jxJTHyKfpUs/2861MGvfClaGMjEw9G8YmeeeH8PAkc/rZxaHpl2zcmpUQfTauxs
0mhbOD42jxRflbdi00yvHVkBBtYdzfvtGwepEUsP26yqOySm6PiVI/XKHWdct61B
28l/VW+mjXDVPiDiMATQRTJi4tYTgC5eSjhnkT4efY7gUMHmO2057cI+jmRob1WV
PEEWLGt76R4IGnH/FtoW2B6lPoOb7KefRx2WgHfTu+zsXvqmbGbgRLSlheG4Zb6g
h0dZXcyojx5vGgJT3ty4o5XgpA6n9EH2uURDXUBYQ9KE8mcNDM9VK6KQEYeBmIJr
QOvMftM1AgMBAAECggEAAn4NSNdS4/vtzVvknLk+SUTmmuklQvARPtBfK1zqZSza
cQ1XARha/p3r7ReQCpAFyJinRharmulIrFJJjmmF4HdUnycjIxxNUyH5GJLgJpM1
cY1Ad6PNkKZSsKH41iVDCGk3N8mk4tH5rynGKKViwreabZX5sEuQdiEIlRXchgLN
ransgsarOU/8+RI2W5JRt7wPAO56WsZc+zeOIyLS7RScibfdi8wMQYZF7PsPB5EG
6ps50hxHWZ18lgLgJO5iK6YZkINHwW8AWDaxonxTgn4eYT8iUDMol8D5i2AXM5x1
JnRzhLKnNUdzug4RB7XrcCOsjoDOU2dW1VbXTNkyxQKBgQD4WbO23ktbkl64dmdA
ZKhRSRcBfbUf8/+Olp8Dt/PTb53Rjvsm3XK5EUK6t9oMGgL131UuOcKysV1RCyzT
I5jjiY5Q3Ws2L0N2IFfxSBI7Di2hxSWLaXgETsMUV0MBfv1TH/8E+3tEtoj26lZY
A0GVOrGprEJVNcL3X3T83R3mNwKBgQDWJK8icbaJujm9HfXi9ODcG7YpPYKRcqJa
LZclOiccRHIUN4SzouIfB6kp63k96W5Yzm6GeRgaiB/LQNPNTDFO4Q7Zrm7wci9o
kzRUHWJcgKl7r8Q+TYXBPJVn0dZe65G5O/d+7cmQn+MUp0Gi5cnYu9eaeKHoJGY0
P6vCKhab8wKBgC2cK8k14hkbNJIkDKpi0ha7maIIeC86HIEPYHzKV9lI8m7+F1n3
6Y3bganRAhae4FRPg9FNglhXApBTwRO1wepn5N8tCveUjosvPXduiQqXfAHttwt3
fzcrT+B4djHcJKITij5cATOJYnYWa20WjADgGqjSngwQJ5JO0alu4oLZAoGAD138
j203mzSY9iBTR+EozcLTVKxMVWGzkuMYqJw+uEGVKiw9wqJatb1X/2EdhzrcJ1VR
Cydfem/wUCarzFy+YRm3dhmVbn3TNx7xL2QYbejxwKWBYLMxeQd+9T9SsecXwwIx
pZMs1ssSgaXrCOSSkpIQS86CV+VczD0Rd1KL4s8CgYEAhfI92S/3eL6eOkm7yHL1
4331R/gomiO4QehLpyUZfirpqxNO/8BL6f25Jp5cC3dJeNu4xEbbMIMpEpT9C+ZJ
4WWYzDCC43HB8AbA8SgMDz7Vaa6h9zHJolLLrcsDMtiD4JT7VeV4UluWXIaRbg6p
XYwWQL2d6uGePDriQHXIUmY=
-----END PRIVATE KEY-----""",
    "client_email": "google-sheets-api@inbound-pattern-429101-c5.iam.gserviceaccount.com",
    "client_id": "107649396128661753097",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/google-sheets-api%40inbound-pattern-429101-c5.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

valores_validos_secos = [
    "BA", "BB", "BC", "BD", "BE", "BF", "BG", "BH",
    "BI", "BJ", "BK", "BL", "BM", "BN", "BO", "BP",
    "BQ", "BR", "BS", "BT", "BU", "BV"
]

valores_validos_congelados = [
    "AK", "AL", "AJ", "AI", "AH", "AG", "AF", "AD",
    "AE", "AC", "AB", "AA"
]

valores_validos_refrigerado = [
    "RC", "RE", "RD", "RC", "RB","RA",
]

valores_validos_controlada = ["CI","CH","CG","CF"]

valores_validos_supercongelados=["FR","SR"]

def asignar_usuarios(primera_columna_lista, df_concatenado):
    """
    Asigna equitativamente los valores de primera_columna_lista a la columna 'Usuario' en df_concatenado,
    distribuyendo los valores restantes desde los últimos usuarios de la lista.

    Parámetros:
    - primera_columna_lista: Lista de valores de usuario.
    - df_concatenado: DataFrame al que se le asignarán los usuarios.

    Retorna:
    - DataFrame con la nueva columna 'Usuario'.
    """
    num_usuarios = len(primera_columna_lista)
    num_filas = len(df_concatenado)

    if num_usuarios == 0 or num_filas == 0:
        raise ValueError("La lista de usuarios o el DataFrame están vacíos.")

    # Si solo hay un usuario, asignarlo a todas las filas
    if num_usuarios == 1:
        df_concatenado["Usuario"] = primera_columna_lista[0]
        return df_concatenado

    # Calcular cuántas filas debe tener cada usuario
    filas_por_usuario = num_filas // num_usuarios
    usuarios_asignados = []

    # Asignar usuarios equitativamente
    for usuario in primera_columna_lista:
        usuarios_asignados.extend([usuario] * filas_por_usuario)

    # Distribuir filas restantes comenzando por los últimos usuarios de la lista
    restantes = num_filas % num_usuarios
    if restantes > 0:
        usuarios_asignados.extend(primera_columna_lista[:restantes])

    # Asegurar que la cantidad de usuarios asignados coincida con la cantidad de filas
    df_concatenado["Usuario"] = usuarios_asignados[:num_filas]

    return df_concatenado

#

                # Definir función para agregar datos en la última fila disponible
def agregar_a_google_sheets(df, sheet_id):
    try:
        # Autenticar cliente de Google Sheets
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = service_account.Credentials.from_service_account_info(credentials_info, scopes=scopes)
        client = gspread.authorize(creds)

        # Abrir la hoja de Google usando el ID
        sheet_id = client.open_by_key(sheet_id).sheet1

        # Llenar valores NaN con "0"
        df = df.fillna("0")

        # Convertir el DataFrame a lista de listas
        df_values = df.values.tolist()

        # Agregar filas al final de la hoja
        sheet_id.append_rows(df_values, value_input_option="RAW")

        return True

    except Exception as e:
        st.error(f"Error al actualizar Google Sheets: {e}")
        return False

# URL de la hoja de Google Sheets
sheet_url = 'https://docs.google.com/spreadsheets/d/1x2z8puH9uRbWuhhddVtEdy8w6QoqxB__3RiHiib9KYk/edit?gid=0#gid=0'
sheet_id = sheet_url.split("/d/")[1].split("/")[0]
data_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv'

def load_data(url):
    df = pd.read_csv(url)
    return df

# Cargar los datos
df = load_data(data_url)
primera_columna_lista = df.iloc[:, 0].tolist()

cal = Argentina()

with st.expander("Carga de archivos"):

    
    datos_stock = st.file_uploader("Informe Stock con Operacion", type="xlsx")
    datos_reposicionamiento= st.file_uploader("Reporte Movimientos", type="xlsx")
    datos_posicion = st.file_uploader("Posicion - Cliente - Sector - Estado", type="xlsx")
    
    if datos_stock is not None:

        # Filtrar los valores existentes y asignar "SECO" en la nueva columna

        df_stock = pd.read_excel(datos_stock,skiprows=2)

        df_stock['Temperatura'] = df_stock['Posicion'].apply(
            lambda x: "SECO" if any(valor in x for valor in valores_validos_secos) else
                    "REFRIGERADO" if any(valor in x for valor in valores_validos_refrigerado) else
                    "CONGELADO" if any(valor in x for valor in valores_validos_congelados) else
                    "CONTROLADA" if any(valor in x for valor in valores_validos_controlada) else
                    "SUPER CONGELADOS" if any(valor in x for valor in valores_validos_supercongelados) else
                    "NO TIENE"
        )

        df_stock = df_stock[df_stock["Temperatura"] != "NO TIENE"]
        df_stock['Entidad'] = df_stock['Entidad'].str.rstrip()


    if datos_reposicionamiento is not None:
        
        df_reposicionamiento = pd.read_excel(datos_reposicionamiento,skiprows=2)
        df_reposicionamiento['Operación de Artículo'] = df_reposicionamiento['Operación de Artículo'].str.rstrip()
        

    if datos_posicion is not None:
        
        df_posicion = pd.read_excel(datos_posicion,skiprows=2)

                    # Aplicar la función para filtrar las filas donde el valor después del segundo "-" no sea "1A"
        df_posicion['Depposc'] = df_posicion['Depposc'].astype(str)
        def filtrar_despues_segundo_guion_1(valor):
            partes = valor.split(' - ')
            if len(partes) >= 3 and '1' in partes[2]:  # Verificar si en la tercera parte (después del segundo "-") contiene '1'
                return True
            return False

        # Filtrar las filas donde NO se cumpla que el valor después del segundo guion contiene "1"
        df_posicion  = df_posicion[~df_posicion['Depposc'].apply(filtrar_despues_segundo_guion_1)]
        df_posicion = df_posicion.rename(columns={'Entnombre': 'Entidad', 'Depposc': 'Posicion',"Depest":"Status Posicion","Artnom":"Descripcion Articulo"})
        df_posicion = df_posicion.dropna(subset=["Posicion"])

        df_posicion['Temperatura'] = df_posicion['Posicion'].apply(
            lambda x: "SECO" if any(valor in x for valor in valores_validos_secos) else
                    "REFRIGERADO" if any(valor in x for valor in valores_validos_refrigerado) else
                    "CONGELADO" if any(valor in x for valor in valores_validos_congelados) else
                    "NO TIENE"
        )




with st.sidebar:

    if datos_posicion is not None:

        rubros_unicos = ['Todos'] + sorted(df_stock['Temperatura'].unique())
        rubros_seleccionados = st.sidebar.multiselect('Temperatura:', rubros_unicos, default=["Todos"])

        entidades_unicas = ['Todos'] + sorted(df_stock['Entidad'].unique())
        entidad_seleccionados = st.sidebar.multiselect('Entidad:', entidades_unicas, default=["Todos"])

    p = st.slider("Proporción estimada de defectos (%)", 0, 50, 7) / 100.0
    duracion_turno = st.slider("Selecciona la duración del turno", 1, 8, 2)
    opciones = ["Control Almacenaje", "Control Parciales", "Control Recepción", "Control Picking","Control Total","Resultados"]
    seleccion = st.multiselect("Selecciona uno o más tipos de control:", opciones[0:-1],default=opciones[0])
    usuarios = st.multiselect("Selecciona uno o más usuarios:", primera_columna_lista,default=primera_columna_lista[0])

if datos_posicion is not None:

    if 'Todos' not in rubros_seleccionados:
        df_stock = df_stock[df_stock['Temperatura'].isin(rubros_seleccionados)]

    if 'Todos' not in entidad_seleccionados:
        df_stock = df_stock[df_stock['Entidad'].isin(entidad_seleccionados)]

    if 'Todos' not in entidad_seleccionados:
        df_reposicionamiento = df_reposicionamiento[df_reposicionamiento['Operación de Artículo'].isin(entidad_seleccionados)]

    if 'Todos' not in entidad_seleccionados:
        df_posicion = df_posicion[df_posicion['Entidad'].isin(entidad_seleccionados)]

    if 'Todos' not in rubros_seleccionados:
        df_posicion = df_posicion[df_posicion['Temperatura'].isin(rubros_seleccionados)]


# Crear pestañas
tab1, tab2, tab3,tab4,tab5,tab6  = st.tabs(opciones)

# duracion_turno = 7.5
productividad_recepcion = 30
productividad_almacenaje = 60
productividad_picking = 18
productividad_parciales = 22
op = len(usuarios)
horas_disponibles = op * duracion_turno


if "Control Almacenaje" in seleccion: 

    with tab1:

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
            df_stock_almacenaje = df_stock_almacenaje[df_stock_almacenaje['Status Posicion'].isin(["BL", "PC", "PV"])]
            df_stock_almacenaje["Pallet"] = df_stock_almacenaje["Pallet"].astype(int)
            df_stock_almacenaje = df_stock_almacenaje[["Entidad","Temperatura","Cod.Articulo","Descripcion Articulo","Posicion","Lote","Pallet","Vencimiento","Status Posicion","Bultos","Unidades","Un.x Bulto"]]
            # Mostrar el DataFrame resultante
            # st.write("Datos de Stock:")
            # st.write(df_stock["Pallet"])
            # st.write(df_stock)


        if datos_posicion is not None:
            # Leer el archivo de posicion
            df_posicion_almacenaje = df_posicion[(df_posicion['Status Posicion'].isin(["DL"])) & (df_posicion['Descripcion Articulo'].isna())]
            df_posicion_almacenaje = df_posicion_almacenaje.dropna(subset=["Posicion"])
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
            df_concatenado[["Unidades", "Un.x Bulto"]] = df_concatenado[["Unidades", "Un.x Bulto"]].fillna(0)
            # df_reposicionamiento_almacenaje = df_reposicionamiento_almacenaje[["Posición Destino","Rubro"]]

            df_concatenado['Vencimiento'] = pd.to_datetime(df_concatenado['Vencimiento'], errors='coerce').dt.strftime('%d-%m-%Y')
            # Tamaño de la población
            N_almacenaje = len(df_concatenado)
            # st.write(f"Tamaño df_stock (número de filas en df_stock): {N_almacenaje}")

            
            horas_requeridas_control = round(N_almacenaje/productividad_almacenaje,2)

            if horas_requeridas_control > horas_disponibles:
                # st.warning(f"El resultado es una capacidad de {resultado_almacenaje} posiciones, lo cual es menor al tamaño de muestra esperado ({N}).")
                # df_concatenado_reduced = df_concatenado.sample(n=resultado_almacenaje, random_state=1)
                # st.write(f"Mostrando {resultado_almacenaje} filas seleccionadas aleatoriamente de la muestra:")
                df_concatenado["Posicion"] = df_concatenado["Posicion"].str.rstrip()
                df_concatenado['Ordenar_primero'] = df_concatenado['Posicion'].str.split(' - ').str[0].str[2:4]
                df_concatenado['Ordenar_segundo'] = pd.to_numeric(
                    df_concatenado['Posicion'].str.split(' - ').str[1], errors='coerce'
                )
                df_concatenado = df_concatenado.dropna(subset=['Ordenar_segundo'])
                df_concatenado['Ordenar_segundo'] = df_concatenado['Ordenar_segundo'].astype(int)
                df_concatenado = df_concatenado.sort_values(by=['Ordenar_primero', 'Ordenar_segundo']).drop(columns=['Ordenar_primero', 'Ordenar_segundo'])
                
                df_concatenado = asignar_usuarios(usuarios, df_concatenado)

                st.write(df_concatenado)
            else:
                # st.success(f"¡El resultado es un control de {horas_requeridas_control} horas, lo cual es menor a las horas disponibles ({horas_disponibles})!")
                horas_disponibles = round(horas_disponibles - horas_requeridas_control,2)
                df_concatenado["Posicion"] = df_concatenado["Posicion"].str.rstrip()
                df_concatenado['Ordenar_primero'] = df_concatenado['Posicion'].str.split(' - ').str[0].str[2:4]
                df_concatenado['Ordenar_segundo'] = df_concatenado['Posicion'].str.split(' - ').str[1].astype(int)
                df_concatenado = df_concatenado.sort_values(by=['Ordenar_primero', 'Ordenar_segundo']).drop(columns=['Ordenar_primero', 'Ordenar_segundo'])
                
                df_concatenado = asignar_usuarios(usuarios, df_concatenado)
                
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

            # # Botón para descargar el archivo Excel
            # st.download_button(
            #     label="Download data as Excel Almacenaje",
            #     data=excel_file,
            #     file_name="df_merged_almacenaje.xlsx",
            #     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            # )

            if st.button("Actualizar Google Sheets Almacenaje"):
                # Configurar el acceso a la API de Google Sheets con las credenciales
                
                # credentials_info = {
                #     "type": "service_account",
                #     "project_id": "inbound-pattern-429101-c5",
                #     "private_key_id": "9dcc01743c917fb186294a8c6d228d4c2fb005bc",
                #     "private_key": """-----BEGIN PRIVATE KEY-----
                # MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDPvpK+357PGmvc
                # 6jxJTHyKfpUs/2861MGvfClaGMjEw9G8YmeeeH8PAkc/rZxaHpl2zcmpUQfTauxs
                # 0mhbOD42jxRflbdi00yvHVkBBtYdzfvtGwepEUsP26yqOySm6PiVI/XKHWdct61B
                # 28l/VW+mjXDVPiDiMATQRTJi4tYTgC5eSjhnkT4efY7gUMHmO2057cI+jmRob1WV
                # PEEWLGt76R4IGnH/FtoW2B6lPoOb7KefRx2WgHfTu+zsXvqmbGbgRLSlheG4Zb6g
                # h0dZXcyojx5vGgJT3ty4o5XgpA6n9EH2uURDXUBYQ9KE8mcNDM9VK6KQEYeBmIJr
                # QOvMftM1AgMBAAECggEAAn4NSNdS4/vtzVvknLk+SUTmmuklQvARPtBfK1zqZSza
                # cQ1XARha/p3r7ReQCpAFyJinRharmulIrFJJjmmF4HdUnycjIxxNUyH5GJLgJpM1
                # cY1Ad6PNkKZSsKH41iVDCGk3N8mk4tH5rynGKKViwreabZX5sEuQdiEIlRXchgLN
                # ransgsarOU/8+RI2W5JRt7wPAO56WsZc+zeOIyLS7RScibfdi8wMQYZF7PsPB5EG
                # 6ps50hxHWZ18lgLgJO5iK6YZkINHwW8AWDaxonxTgn4eYT8iUDMol8D5i2AXM5x1
                # JnRzhLKnNUdzug4RB7XrcCOsjoDOU2dW1VbXTNkyxQKBgQD4WbO23ktbkl64dmdA
                # ZKhRSRcBfbUf8/+Olp8Dt/PTb53Rjvsm3XK5EUK6t9oMGgL131UuOcKysV1RCyzT
                # I5jjiY5Q3Ws2L0N2IFfxSBI7Di2hxSWLaXgETsMUV0MBfv1TH/8E+3tEtoj26lZY
                # A0GVOrGprEJVNcL3X3T83R3mNwKBgQDWJK8icbaJujm9HfXi9ODcG7YpPYKRcqJa
                # LZclOiccRHIUN4SzouIfB6kp63k96W5Yzm6GeRgaiB/LQNPNTDFO4Q7Zrm7wci9o
                # kzRUHWJcgKl7r8Q+TYXBPJVn0dZe65G5O/d+7cmQn+MUp0Gi5cnYu9eaeKHoJGY0
                # P6vCKhab8wKBgC2cK8k14hkbNJIkDKpi0ha7maIIeC86HIEPYHzKV9lI8m7+F1n3
                # 6Y3bganRAhae4FRPg9FNglhXApBTwRO1wepn5N8tCveUjosvPXduiQqXfAHttwt3
                # fzcrT+B4djHcJKITij5cATOJYnYWa20WjADgGqjSngwQJ5JO0alu4oLZAoGAD138
                # j203mzSY9iBTR+EozcLTVKxMVWGzkuMYqJw+uEGVKiw9wqJatb1X/2EdhzrcJ1VR
                # Cydfem/wUCarzFy+YRm3dhmVbn3TNx7xL2QYbejxwKWBYLMxeQd+9T9SsecXwwIx
                # pZMs1ssSgaXrCOSSkpIQS86CV+VczD0Rd1KL4s8CgYEAhfI92S/3eL6eOkm7yHL1
                # 4331R/gomiO4QehLpyUZfirpqxNO/8BL6f25Jp5cC3dJeNu4xEbbMIMpEpT9C+ZJ
                # 4WWYzDCC43HB8AbA8SgMDz7Vaa6h9zHJolLLrcsDMtiD4JT7VeV4UluWXIaRbg6p
                # XYwWQL2d6uGePDriQHXIUmY=
                # -----END PRIVATE KEY-----""",
                #     "client_email": "google-sheets-api@inbound-pattern-429101-c5.iam.gserviceaccount.com",
                #     "client_id": "107649396128661753097",
                #     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                #     "token_uri": "https://oauth2.googleapis.com/token",
                #     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                #     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/google-sheets-api%40inbound-pattern-429101-c5.iam.gserviceaccount.com",
                #     "universe_domain": "googleapis.com"
                # }

                # st.write(credentials_info)

                # Configurar los scopes correctos
                scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                creds = service_account.Credentials.from_service_account_info(credentials_info, scopes=scopes)

                # st.write(creds)

                # Autenticar cliente de Google Sheets
                client = gspread.authorize(creds)
                # Coloca tu sheet_id aquí
                sheet_id = '1hY3qg_3_6NNqwoFbVy7tfclIXcDRupjbe59IG7lXhsI'  # Reemplaza con tu sheet_id real

                # Abre la hoja de Google usando el ID de la hoja
                sheet = client.open_by_key(sheet_id).sheet1

                df_concatenado = df_concatenado.fillna("0")
                df_concatenado["Tarea Salteada"] = 1
                # Convirtiendo el DataFrame a una lista de listas
                df_values = df_concatenado.values.tolist()
                
                
                # Escribe los datos en el Google Sheet, sobrescribiendo todo
                sheet.clear()  # Borrar el contenido anterior
                sheet.append_row(df_concatenado.columns.tolist())  # Escribe los encabezados
                sheet.append_rows(df_values)  # Escribe los datos del DataFrame

                sheet_id_2 = '1FBkWGCRarYeiAX0zYycd6RJZJZf4vTIBL2oZlfHbC5s'  # Reemplaza con tu sheet_id real
                # Abre la hoja de Google usando el ID de la hoja
                sheet = client.open_by_key(sheet_id_2).sheet1
                
                # Escribe los datos en el Google Sheet, sobrescribiendo todo
                sheet.clear()  # Borrar el contenido anterior
                sheet.append_row(df_concatenado.columns.tolist())  # Escribe los encabezados
                sheet.append_rows(df_values)  # Escribe los datos del DataFrame

                st.success("¡Datos actualizados en Google Sheets con éxito!")


        else:
            st.write("Para realizar el merge, carga ambos archivos: 'Informe Stock con Operacion' y 'Reporte Posicionamiento'.")
else:
    pass

if "Control Parciales" in seleccion: 

    with tab2:

        st.title("Control Parciales")

        # Procesar y mostrar cada archivo si se ha subido
        if datos_stock is not None:
            # Leer el archivo de stock
            df_stock_parciales = df_stock.dropna(subset=["Pallet"])
            df_stock_parciales= df_stock_parciales[df_stock_parciales["Pallet"] != 0]
            df_stock_parciales["Pallet"] = df_stock_parciales["Pallet"].astype(int)
            # Mostrar el DataFrame resultante
            # st.write("Datos de Stock:")
            # st.write(df_stock["Pallet"])
            # st.write(df_stock)

        if datos_reposicionamiento is not None:
            

            df_reposicionamiento_parciales = df_reposicionamiento.dropna(subset=["Pallet"])
            df_reposicionamiento_parciales = df_reposicionamiento_parciales[df_reposicionamiento_parciales["Pallet"] != 0]
            df_reposicionamiento_parciales["Pallet"] = df_reposicionamiento_parciales["Pallet"].astype(int)
            df_reposicionamiento_parciales['Fecha (Fin Movimiento)'] = pd.to_datetime(df_reposicionamiento_parciales['Fecha (Fin Movimiento)'])
            df_reposicionamiento_parciales['Dias_Laborables'] = df_reposicionamiento_parciales['Fecha (Fin Movimiento)'].apply(lambda x: cal.get_working_days_delta(x.date(), datetime.now().date()))
            df_reposicionamiento_parciales['Universo'] = (df_reposicionamiento_parciales['Dias_Laborables'] == 1).astype(int)
            df_reposicionamiento_parciales = df_reposicionamiento_parciales[df_reposicionamiento_parciales['Universo'] == 1]

            df_reposicionamiento_parciales = df_reposicionamiento_parciales[df_reposicionamiento_parciales["Tipo de Movimiento Alt"].isin(["RP"])]

            df_reposicionamiento_parciales = df_reposicionamiento_parciales.groupby('Posición Origen').agg({
                'Bultos': 'sum',
                'Unidades': 'sum',
                'ID Art': 'count',
                "Artículo": "first",
                "Rubro": "first",
                "Tipo de Movimiento Alt": "first"
            }).reset_index()

           

            if datos_stock is not None and datos_reposicionamiento is not None:
            # Realizar el merge de df_stock y df_reposicionamiento según la columna "Pallet"
                df_merged_parciales = pd.merge(df_stock_parciales, df_reposicionamiento_parciales, left_on='Posicion', right_on='Posición Origen', how='inner')
                df_merged_parciales = df_merged_parciales[["Cod.Articulo","Temperatura","Rubro","Entidad","Descripcion Articulo","Pasillo","Columna","Nivel","Sector","Posicion","Bultos_x","Unidades_x","Vencimiento","Un.x Bulto"]]
                df_merged_parciales['Vencimiento'] = pd.to_datetime(df_merged_parciales['Vencimiento'], errors='coerce').dt.strftime('%d-%m-%Y')
                df_merged_parciales = df_merged_parciales.rename(columns={'Bultos_x': 'Bultos', 'Unidades_x': 'Unidades'})
                # Tamaño de la población
                N_parciales = len(df_merged_parciales)
                # st.write(f"Tamaño de df_stock (número de filas en df_merged_parciales): {N_parciales}")


            horas_requeridas_control = round(N_parciales/productividad_parciales,2)

            if horas_requeridas_control > horas_disponibles:
                # st.warning(f"¡El resultado es una control de {horas_requeridas_control} horas, lo cual es menor a las horas disponibles ({horas_disponibles})!")
                N_parciales = int(horas_disponibles*productividad_parciales)
                # st.warning(f"Se pueden controlar {N_parciales} posiciones")
                df_merged_parciales_reduced = df_merged_parciales.sample(n=N_parciales, random_state=1)
                # st.write(f"Mostrando {N_parciales} filas seleccionadas aleatoriamente de la muestra:")
                df_merged_parciales["Posicion"] = df_merged_parciales["Posicion"].str.rstrip()
                df_merged_parciales['Ordenar_primero'] = df_merged_parciales['Posicion'].str.split(' - ').str[0].str[2:4]
                df_merged_parciales['Ordenar_segundo'] = df_merged_parciales['Posicion'].str.split(' - ').str[1].astype(int)
                df_merged_parciales = df_merged_parciales.sort_values(by=['Ordenar_primero', 'Ordenar_segundo']).drop(columns=['Ordenar_primero', 'Ordenar_segundo'])
                
                df_merged_parciales = asignar_usuarios(usuarios, df_merged_parciales)

                st.write(df_merged_parciales)
            else:
                # st.success(f"¡El resultado es una control de {horas_requeridas_control} horas, lo cual es menor a las horas disponibles ({horas_disponibles})!")
                horas_disponibles = round(horas_disponibles - horas_requeridas_control,2)
                df_merged_parciales["Posicion"] = df_merged_parciales["Posicion"].str.rstrip()
                df_merged_parciales['Ordenar_primero'] = df_merged_parciales['Posicion'].str.split(' - ').str[0].str[2:4]
                df_merged_parciales['Ordenar_segundo'] = df_merged_parciales['Posicion'].str.split(' - ').str[1].astype(int)
                df_merged_parciales = df_merged_parciales.sort_values(by=['Ordenar_primero', 'Ordenar_segundo']).drop(columns=['Ordenar_primero', 'Ordenar_segundo'])
                
                df_merged_parciales = asignar_usuarios(usuarios, df_merged_parciales)

                st.write(df_merged_parciales)

            def convert_df_to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
                    writer.close()  # No es necesario el 'save()', cerrando con 'close()' dentro del contexto
                processed_data = output.getvalue()  # Obtener los datos del archivo en formato binario
                return processed_data

            # Crear un archivo Excel de un DataFrame (en este caso df_merged)
            excel_file = convert_df_to_excel(df_merged_parciales)

            # # Botón para descargar el archivo Excel
            # st.download_button(
            #     label="Download data as Excel Parciales",
            #     data=excel_file,
            #     file_name="df_merged_parciales.xlsx",
            #     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            # ) 

            if st.button("Actualizar Google Sheets Parciales"):
                # Configurar el acceso a la API de Google Sheets con las credenciales
                # credentials_info = st.secrets["gcp_service_account"]
                # credentials_info = {
                #     "type": "service_account",
                #     "project_id": "inbound-pattern-429101-c5",
                #     "private_key_id": "9dcc01743c917fb186294a8c6d228d4c2fb005bc",
                #     "private_key": """-----BEGIN PRIVATE KEY-----
                # MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDPvpK+357PGmvc
                # 6jxJTHyKfpUs/2861MGvfClaGMjEw9G8YmeeeH8PAkc/rZxaHpl2zcmpUQfTauxs
                # 0mhbOD42jxRflbdi00yvHVkBBtYdzfvtGwepEUsP26yqOySm6PiVI/XKHWdct61B
                # 28l/VW+mjXDVPiDiMATQRTJi4tYTgC5eSjhnkT4efY7gUMHmO2057cI+jmRob1WV
                # PEEWLGt76R4IGnH/FtoW2B6lPoOb7KefRx2WgHfTu+zsXvqmbGbgRLSlheG4Zb6g
                # h0dZXcyojx5vGgJT3ty4o5XgpA6n9EH2uURDXUBYQ9KE8mcNDM9VK6KQEYeBmIJr
                # QOvMftM1AgMBAAECggEAAn4NSNdS4/vtzVvknLk+SUTmmuklQvARPtBfK1zqZSza
                # cQ1XARha/p3r7ReQCpAFyJinRharmulIrFJJjmmF4HdUnycjIxxNUyH5GJLgJpM1
                # cY1Ad6PNkKZSsKH41iVDCGk3N8mk4tH5rynGKKViwreabZX5sEuQdiEIlRXchgLN
                # ransgsarOU/8+RI2W5JRt7wPAO56WsZc+zeOIyLS7RScibfdi8wMQYZF7PsPB5EG
                # 6ps50hxHWZ18lgLgJO5iK6YZkINHwW8AWDaxonxTgn4eYT8iUDMol8D5i2AXM5x1
                # JnRzhLKnNUdzug4RB7XrcCOsjoDOU2dW1VbXTNkyxQKBgQD4WbO23ktbkl64dmdA
                # ZKhRSRcBfbUf8/+Olp8Dt/PTb53Rjvsm3XK5EUK6t9oMGgL131UuOcKysV1RCyzT
                # I5jjiY5Q3Ws2L0N2IFfxSBI7Di2hxSWLaXgETsMUV0MBfv1TH/8E+3tEtoj26lZY
                # A0GVOrGprEJVNcL3X3T83R3mNwKBgQDWJK8icbaJujm9HfXi9ODcG7YpPYKRcqJa
                # LZclOiccRHIUN4SzouIfB6kp63k96W5Yzm6GeRgaiB/LQNPNTDFO4Q7Zrm7wci9o
                # kzRUHWJcgKl7r8Q+TYXBPJVn0dZe65G5O/d+7cmQn+MUp0Gi5cnYu9eaeKHoJGY0
                # P6vCKhab8wKBgC2cK8k14hkbNJIkDKpi0ha7maIIeC86HIEPYHzKV9lI8m7+F1n3
                # 6Y3bganRAhae4FRPg9FNglhXApBTwRO1wepn5N8tCveUjosvPXduiQqXfAHttwt3
                # fzcrT+B4djHcJKITij5cATOJYnYWa20WjADgGqjSngwQJ5JO0alu4oLZAoGAD138
                # j203mzSY9iBTR+EozcLTVKxMVWGzkuMYqJw+uEGVKiw9wqJatb1X/2EdhzrcJ1VR
                # Cydfem/wUCarzFy+YRm3dhmVbn3TNx7xL2QYbejxwKWBYLMxeQd+9T9SsecXwwIx
                # pZMs1ssSgaXrCOSSkpIQS86CV+VczD0Rd1KL4s8CgYEAhfI92S/3eL6eOkm7yHL1
                # 4331R/gomiO4QehLpyUZfirpqxNO/8BL6f25Jp5cC3dJeNu4xEbbMIMpEpT9C+ZJ
                # 4WWYzDCC43HB8AbA8SgMDz7Vaa6h9zHJolLLrcsDMtiD4JT7VeV4UluWXIaRbg6p
                # XYwWQL2d6uGePDriQHXIUmY=
                # -----END PRIVATE KEY-----""",
                #     "client_email": "google-sheets-api@inbound-pattern-429101-c5.iam.gserviceaccount.com",
                #     "client_id": "107649396128661753097",
                #     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                #     "token_uri": "https://oauth2.googleapis.com/token",
                #     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                #     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/google-sheets-api%40inbound-pattern-429101-c5.iam.gserviceaccount.com",
                #     "universe_domain": "googleapis.com"
                # }

                # st.write(credentials_info)

                # Configurar los scopes correctos
                scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                creds = service_account.Credentials.from_service_account_info(credentials_info, scopes=scopes)

                # st.write(creds)

                # Autenticar cliente de Google Sheets
                client = gspread.authorize(creds)
                # Coloca tu sheet_id aquí
                sheet_id = '1eikx9phIghxyiv1yfFy3ZqqNePWSbhkyvisOzSD37pw'  # Reemplaza con tu sheet_id real

                # Abre la hoja de Google usando el ID de la hoja
                sheet = client.open_by_key(sheet_id).sheet1

                df_merged_parciales = df_merged_parciales.fillna("0")
                df_merged_parciales["Tarea Salteada"] = 1
                # Convirtiendo el DataFrame a una lista de listas
                df_values = df_merged_parciales.values.tolist()
                
                # Escribe los datos en el Google Sheet, sobrescribiendo todo
                sheet.clear()  # Borrar el contenido anterior
                sheet.append_row(df_merged_parciales.columns.tolist())  # Escribe los encabezados
                sheet.append_rows(df_values)  # Escribe los datos del DataFrame

                sheet_id_2 = '1OuRlrf7RR7P1o0FGIGKIWLMjSFo62Aa3NgiEvpTx2Ps'  # Reemplaza con tu sheet_id real
                # Abre la hoja de Google usando el ID de la hoja
                sheet = client.open_by_key(sheet_id_2).sheet1
                
                # Escribe los datos en el Google Sheet, sobrescribiendo todo
                sheet.clear()  # Borrar el contenido anterior
                sheet.append_row(df_merged_parciales.columns.tolist())  # Escribe los encabezados
                sheet.append_rows(df_values)  # Escribe los datos del DataFrame

                st.success("¡Datos actualizados en Google Sheets con éxito!")


else:
    pass



if "Control Recepción" in seleccion: 

    with tab3:

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

            if df_merged_recepcion.empty:
            
                st.warning("⚠️ No existieron Entradas de Pallet en el día de ayer")

            else:

                # Tamaño de la población
                N = len(df_filtered)
                # st.write(f"Tamaño de la población (número de filas en df_filtered): {N}")

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
                tamano_muestra_recepcion = calcular_tamano_muestra(N, z, e, p)
                # st.write(f"El tamaño de muestra necesario es: {tamano_muestra_recepcion}")

                # Seleccionar una muestra aleatoria de tamaño n
                df_sample = df_filtered.sample(n=tamano_muestra_recepcion, random_state=1)

                # Mostrar las columnas solicitadas
                columnas_a_mostrar = [
                    'Entidad', 'Articulo',"Temperatura", 'Descripcion Articulo', 'Posicion', 'Pallet', 'Lote', 
                    'Fecha Ingreso', 'Vencimiento', 'Bultos_x', 'Unidades_x', 'Tipo de Movimiento Alt', 'Rubro',"Un.x Bulto"
                ]
                
                
                df_sample = df_sample[columnas_a_mostrar]

                df_sample['Vencimiento'] = pd.to_datetime(df_sample['Vencimiento'], errors='coerce').dt.strftime('%d-%m-%Y')
                df_sample['Fecha Ingreso'] = pd.to_datetime(df_sample['Fecha Ingreso'], errors='coerce').dt.strftime('%d-%m-%Y')
                df_sample = df_sample.rename(columns={'Bultos_x': 'Bultos', 'Unidades_x': 'Unidades'})

                horas_requeridas_control = round(tamano_muestra_recepcion/productividad_recepcion,2)

                if horas_requeridas_control > horas_disponibles:
                    # st.warning(f"¡El resultado es un control de {horas_requeridas_control} horas, lo cual es mayor a las horas disponibles ({horas_disponibles})!")
                    N_recepcion = int(horas_disponibles*productividad_recepcion)
                    # st.warning(f"Se pueden controlar {N_recepcion} posiciones")
                    df_sample = df_sample.sample(n=N_recepcion, random_state=1)
                    st.write(f"Mostrando {N_recepcion} filas seleccionadas aleatoriamente de la muestra:")
                    df_sample["Posicion"] = df_sample["Posicion"].str.rstrip()
                    df_sample['Ordenar_primero'] = df_sample['Posicion'].str.split(' - ').str[0].str[2:4]
                    df_sample['Ordenar_segundo'] = df_sample['Posicion'].str.split(' - ').str[1].astype(int)
                    df_sample = df_sample.sort_values(by=['Ordenar_primero', 'Ordenar_segundo']).drop(columns=['Ordenar_primero', 'Ordenar_segundo'])
                    
                    df_sample = asignar_usuarios(usuarios, df_sample)
                    
                    st.write(df_sample)
                else:
                    # st.success(f"¡El resultado es un control de {horas_requeridas_control} horas, lo cual es menor a las horas disponibles ({horas_disponibles})!")
                    horas_disponibles = round(horas_disponibles - horas_requeridas_control,2)
                    # st.write("Muestra aleatoria de df_filtrado:")
                    df_sample["Posicion"] = df_sample["Posicion"].str.rstrip()
                    df_sample['Ordenar_primero'] = df_sample['Posicion'].str.split(' - ').str[0].str[2:4]
                    df_sample['Ordenar_segundo'] = df_sample['Posicion'].str.split(' - ').str[1].astype(int)
                    df_sample = df_sample.sort_values(by=['Ordenar_primero', 'Ordenar_segundo']).drop(columns=['Ordenar_primero', 'Ordenar_segundo'])
                    
                    df_sample = asignar_usuarios(usuarios, df_sample)

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

                # # Botón para descargar el archivo Excel
                # st.download_button(
                #     label="Download data as Excel Recepcion",
                #     data=excel_file,
                #     file_name="df_merged_recepcion.xlsx",
                #     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                # )

                if st.button("Actualizar Google Sheets Recepcion"):

                    # Configurar los scopes correctos
                    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                    creds = service_account.Credentials.from_service_account_info(credentials_info, scopes=scopes)

                    # st.write(creds)

                    # Autenticar cliente de Google Sheets
                    client = gspread.authorize(creds)
                    # Coloca tu sheet_id aquí
                    sheet_id = '1tpJAMDbUMANKitwywXEJ3_4Khm-DbJPAPxUbzva75cU'  # Reemplaza con tu sheet_id real

                    # Abre la hoja de Google usando el ID de la hoja
                    sheet = client.open_by_key(sheet_id).sheet1

                    df_sample = df_sample.fillna("0")
                    df_sample["Tarea Salteada"] = 1
                    # Convirtiendo el DataFrame a una lista de listas
                    df_values = df_sample.values.tolist()
                    
                    # Escribe los datos en el Google Sheet, sobrescribiendo todo
                    sheet.clear()  # Borrar el contenido anterior
                    sheet.append_row(df_sample.columns.tolist())  # Escribe los encabezados
                    sheet.append_rows(df_values)  # Escribe los datos del DataFrame

                    sheet_id_2 = '1BFyf3o8jYCleLtKwaMD9b90ZPhJBE8-yXeq74En_B_M'  # Reemplaza con tu sheet_id real
                    # Abre la hoja de Google usando el ID de la hoja
                    sheet = client.open_by_key(sheet_id_2).sheet1
                    
                    # Escribe los datos en el Google Sheet, sobrescribiendo todo
                    sheet.clear()  # Borrar el contenido anterior
                    sheet.append_row(df_sample.columns.tolist())  # Escribe los encabezados
                    sheet.append_rows(df_values)  # Escribe los datos del DataFrame

                    st.success("¡Datos actualizados en Google Sheets con éxito!")

        else:
            st.write("Para realizar el merge, carga ambos archivos: 'Informe Stock con Operacion' y 'Reporte Posicionamiento'.")
    
else:
    pass


if "Control Picking" in seleccion: 

    with tab4:
        

        st.title("Control Picking")

        # Procesar y mostrar cada archivo si se ha subido
        if datos_stock is not None:
            # Leer el archivo de stock
            df_stock_picking = df_stock.dropna(subset=["Pallet"])

            df_stock_picking = df_stock_picking[df_stock_picking["Pallet"] != 0]
            df_stock_picking = df_stock_picking[df_stock_picking['Nivel'] == 1]
            df_stock_picking["Pallet"] = df_stock_picking["Pallet"].astype(int)

            # Suponiendo que df_stock_picking ya está cargado
            df_stock_picking = df_stock_picking.groupby('Posicion').agg({
                'Entidad': 'first',  # Si es única por posición, tomar la primera ocurrencia
                'Consulta': 'first',
                'Articulo': 'first',
                'Presentacion': 'first',
                'Cod.Articulo': 'first',
                'Descripcion Articulo': 'first',
                'Id Deposito': 'first',
                'id Sector': 'first',
                'Pasillo': 'first',
                'Columna': 'first',
                'Nivel': 'first',
                'Sector': 'first',
                'Pallet': 'first',  # Cantidad de pallets distintos en la posición
                'Lote': 'first',  # Cantidad de lotes distintos en la posición
                'Fecha Ingreso': 'first',  # Fecha más antigua de ingreso
                'Vencimiento': 'first',  # Fecha de vencimiento más próxima
                'Dias hasta Vencimiento': 'first',  # Tomar el menor valor (más crítico)
                'Dias Criticidad': 'first',
                'Fecha Criticidad': 'first',  # Fecha más próxima de criticidad
                'Dias hasta Criticidad': 'first',
                'Status Posicion': 'first',  # Si es única por posición
                'Un.x Bulto': 'first',
                'Bultos': 'sum',  # Sumar los bultos totales
                'Unidades': 'sum',  # Sumar unidades totales
                'Unidades Sueltas': 'sum',  # Sumar unidades sueltas totales
                'Temperatura': 'first'  # Promedio de la temperatura
            }).reset_index()

            # Mostrar el DataFrame resultante
            # st.write("Datos de Stock:")
            # st.write(df_stock["Pallet"])
            # st.write(df_stock)


        if datos_reposicionamiento is not None:


            # Leer el archivo de reposicionamiento
            df_reposicionamiento_picking = df_reposicionamiento.dropna(subset=["Pallet"])
            df_reposicionamiento_picking = df_reposicionamiento_picking[df_reposicionamiento_picking["Pallet"] != 0]
            df_reposicionamiento_picking["Pallet"] = df_reposicionamiento_picking["Pallet"].astype(int)
            df_reposicionamiento_picking['Fecha (Fin Movimiento)'] = pd.to_datetime(df_reposicionamiento_picking['Fecha (Fin Movimiento)'])
            df_reposicionamiento_picking['Dias_Laborables'] = df_reposicionamiento_picking['Fecha (Fin Movimiento)'].apply(lambda x: cal.get_working_days_delta(x.date(), datetime.now().date()))
            df_reposicionamiento_picking['Universo'] = (df_reposicionamiento_picking['Dias_Laborables'] == 1).astype(int)
            df_reposicionamiento_picking = df_reposicionamiento_picking[df_reposicionamiento_picking['Universo'] == 1]


            df_reposicionamiento_picking_piu_pib = df_reposicionamiento_picking[df_reposicionamiento_picking["Tipo de Movimiento Alt"].isin(["PIU", "PIB"])]

            # Agrupación y cálculo de acumulados
            df_agrupado_piu_pib = df_reposicionamiento_picking_piu_pib.groupby('Posición Destino').agg({
                'Bultos': 'sum',
                'Unidades': 'sum',
                'ID Art': 'count',
                "Artículo": "first",
                "Rubro": "first",
                "Tipo de Movimiento Alt": "first"
            }).reset_index()

            df_agrupado_piu_pib = df_agrupado_piu_pib.sort_values(by='Bultos', ascending=False)
            df_agrupado_piu_pib['Porcentaje_Acumulado_Bultos'] = df_agrupado_piu_pib['Bultos'].cumsum() / df_agrupado_piu_pib['Bultos'].sum()
            
            df_agrupado_piu_pib = df_agrupado_piu_pib.sort_values(by='ID Art', ascending=False)
            df_agrupado_piu_pib['Porcentaje_Acumulado_ID_Art'] = df_agrupado_piu_pib['ID Art'].cumsum() / df_agrupado_piu_pib['ID Art'].sum()

            # Filtrar top 20% de bultos e ID Art
            df_top_20_bultos_piu_pib = df_agrupado_piu_pib[df_agrupado_piu_pib['Porcentaje_Acumulado_Bultos'] <= 0.80]
            df_top_20_id_art_piu_pib = df_agrupado_piu_pib[df_agrupado_piu_pib['Porcentaje_Acumulado_ID_Art'] <= 0.80]

            # Combinar los resultados
            df_reposicionamiento_picking_piu_pib = pd.concat([df_top_20_bultos_piu_pib, df_top_20_id_art_piu_pib]).drop_duplicates()

            # Repetir el proceso para movimientos "EI" y "SI"
            df_reposicionamiento_picking_ei_si = df_reposicionamiento_picking[df_reposicionamiento_picking["Tipo de Movimiento Alt"].isin(["EI", "SI"])]

            # Agrupar por 'Posición Destino' y calcular la suma de bultos para EI y SI por separado
            df_ei = df_reposicionamiento_picking_ei_si[df_reposicionamiento_picking_ei_si["Tipo de Movimiento Alt"] == "EI"].groupby('Posición Destino')['Bultos'].sum().reset_index().rename(columns={'Bultos': 'Bultos_EI'})
            df_si = df_reposicionamiento_picking_ei_si[df_reposicionamiento_picking_ei_si["Tipo de Movimiento Alt"] == "SI"].groupby('Posición Destino')['Bultos'].sum().reset_index().rename(columns={'Bultos': 'Bultos_SI'})

            # Combinar los datos de EI y SI para la misma posición
            df_ei_si = pd.merge(df_ei, df_si, on='Posición Destino', how='outer').fillna(0)

            # Calcular el módulo de la diferencia entre Bultos_EI y Bultos_SI
            df_ei_si['Diferencia_Modulo_Bultos'] = (df_ei_si['Bultos_EI'] - df_ei_si['Bultos_SI']).abs()


            # Concatenar los resultados de PIU/PIB con EI/SI
            df_reposicionamiento_picking = pd.concat([df_reposicionamiento_picking_piu_pib, df_ei_si]).drop_duplicates()

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

        # if datos_stock is not None and datos_reposicionamiento is not None:

        #     df_agrupado = df_agrupado.sort_values(by='Porcentaje_Acumulado_ID_Art', ascending=False)


        if datos_stock is not None and datos_reposicionamiento is not None:
            df_reposicionamiento_picking = df_reposicionamiento_picking.dropna(subset=["Artículo"])
            # Realizar el merge de df_stock y df_reposicionamiento según la columna "Pallet"
            df_merged_picking = pd.merge(df_stock_picking, df_reposicionamiento_picking, left_on='Posicion', right_on='Posición Destino', how='inner')
            df_merged_picking = df_merged_picking[["Cod.Articulo","Temperatura","Rubro","Entidad","Descripcion Articulo","Pasillo","Columna","Nivel","Sector","Posicion","Bultos_x","Unidades_x","Vencimiento","Un.x Bulto"]]
            df_merged_picking['Vencimiento'] = pd.to_datetime(df_merged_picking['Vencimiento'], errors='coerce').dt.strftime('%d-%m-%Y')
            df_merged_picking = df_merged_picking.rename(columns={'Bultos_x': 'Bultos', 'Unidades_x': 'Unidades'})
            # Tamaño de la población
            N = len(df_stock_picking)
            # st.write(f"Tamaño de la población (número de filas en df_merged_picking): {N}")
            N_picking = len(df_merged_picking)
            # st.write(f"Tamaño de la muestra (número de filas en df_merged_picking): {N_picking}")


            horas_requeridas_control = round(N_picking/productividad_picking,2)

            if horas_requeridas_control > horas_disponibles:
                # st.warning(f"El resultado es un control de {horas_requeridas_control} horas, lo cual es mayor a las horas disponibles ({horas_disponibles})!")
                N_picking = int(horas_disponibles*productividad_picking)
                # st.warning(f"Se pueden controlar {N_picking} posiciones")
                df_merged_picking = df_merged_picking.sample(n=N_picking, random_state=1)
                df_merged_picking['Ordenar_primero'] = df_merged_picking['Posicion'].str.split(' - ').str[0].str[2:4]
                df_merged_picking['Ordenar_segundo'] = df_merged_picking['Posicion'].str.split(' - ').str[1].astype(int)
                df_merged_picking = df_merged_picking.sort_values(by=['Ordenar_primero', 'Ordenar_segundo']).drop(columns=['Ordenar_primero', 'Ordenar_segundo'])
                # st.write(f"Mostrando {N_picking} filas seleccionadas aleatoriamente de la muestra:")

                df_merged_picking = asignar_usuarios(usuarios, df_merged_picking)

                st.write(df_merged_picking)
            else:
                # st.success(f"¡El resultado es un control de {horas_requeridas_control} horas, lo cual es menor a las horas disponibles ({horas_disponibles})!")
                horas_disponibles = round(horas_disponibles - horas_requeridas_control,2)
                df_merged_picking["Posicion"] = df_merged_picking["Posicion"].str.rstrip()
                df_merged_picking['Ordenar_primero'] = df_merged_picking['Posicion'].str.split(' - ').str[0].str[2:4]
                df_merged_picking['Ordenar_segundo'] = df_merged_picking['Posicion'].str.split(' - ').str[1].astype(int)
                df_merged_picking = df_merged_picking.sort_values(by=['Ordenar_primero', 'Ordenar_segundo']).drop(columns=['Ordenar_primero', 'Ordenar_segundo'])
                
                df_merged_picking = asignar_usuarios(usuarios, df_merged_picking)

                st.write(df_merged_picking)
            

            cantidad_filas = len(df_merged_picking)

            # Mostrar el texto en Streamlit con la cantidad de filas
            st.write(f"Cantidad de posiciones a controlar: {cantidad_filas}")


            def convert_df_to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
                    writer.close()  # No es necesario el 'save()', cerrando con 'close()' dentro del contexto
                processed_data = output.getvalue()  # Obtener los datos del archivo en formato binario
                return processed_data

            # Crear un archivo Excel de un DataFrame (en este caso df_merged)
            excel_file = convert_df_to_excel(df_merged_picking)

            # # Botón para descargar el archivo Excel
            # st.download_button(
            #     label="Download data as Excel Picking",
            #     data=excel_file,
            #     file_name="df_merged_picking.xlsx",
            #     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            # )

            if st.button("Actualizar Google Sheets Picking"):
                # Configurar el acceso a la API de Google Sheets con las credenciales
                # credentials_info = st.secrets["gcp_service_account"]
                # credentials_info = {
                #     "type": "service_account",
                #     "project_id": "inbound-pattern-429101-c5",
                #     "private_key_id": "9dcc01743c917fb186294a8c6d228d4c2fb005bc",
                #     "private_key": """-----BEGIN PRIVATE KEY-----
                # MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDPvpK+357PGmvc
                # 6jxJTHyKfpUs/2861MGvfClaGMjEw9G8YmeeeH8PAkc/rZxaHpl2zcmpUQfTauxs
                # 0mhbOD42jxRflbdi00yvHVkBBtYdzfvtGwepEUsP26yqOySm6PiVI/XKHWdct61B
                # 28l/VW+mjXDVPiDiMATQRTJi4tYTgC5eSjhnkT4efY7gUMHmO2057cI+jmRob1WV
                # PEEWLGt76R4IGnH/FtoW2B6lPoOb7KefRx2WgHfTu+zsXvqmbGbgRLSlheG4Zb6g
                # h0dZXcyojx5vGgJT3ty4o5XgpA6n9EH2uURDXUBYQ9KE8mcNDM9VK6KQEYeBmIJr
                # QOvMftM1AgMBAAECggEAAn4NSNdS4/vtzVvknLk+SUTmmuklQvARPtBfK1zqZSza
                # cQ1XARha/p3r7ReQCpAFyJinRharmulIrFJJjmmF4HdUnycjIxxNUyH5GJLgJpM1
                # cY1Ad6PNkKZSsKH41iVDCGk3N8mk4tH5rynGKKViwreabZX5sEuQdiEIlRXchgLN
                # ransgsarOU/8+RI2W5JRt7wPAO56WsZc+zeOIyLS7RScibfdi8wMQYZF7PsPB5EG
                # 6ps50hxHWZ18lgLgJO5iK6YZkINHwW8AWDaxonxTgn4eYT8iUDMol8D5i2AXM5x1
                # JnRzhLKnNUdzug4RB7XrcCOsjoDOU2dW1VbXTNkyxQKBgQD4WbO23ktbkl64dmdA
                # ZKhRSRcBfbUf8/+Olp8Dt/PTb53Rjvsm3XK5EUK6t9oMGgL131UuOcKysV1RCyzT
                # I5jjiY5Q3Ws2L0N2IFfxSBI7Di2hxSWLaXgETsMUV0MBfv1TH/8E+3tEtoj26lZY
                # A0GVOrGprEJVNcL3X3T83R3mNwKBgQDWJK8icbaJujm9HfXi9ODcG7YpPYKRcqJa
                # LZclOiccRHIUN4SzouIfB6kp63k96W5Yzm6GeRgaiB/LQNPNTDFO4Q7Zrm7wci9o
                # kzRUHWJcgKl7r8Q+TYXBPJVn0dZe65G5O/d+7cmQn+MUp0Gi5cnYu9eaeKHoJGY0
                # P6vCKhab8wKBgC2cK8k14hkbNJIkDKpi0ha7maIIeC86HIEPYHzKV9lI8m7+F1n3
                # 6Y3bganRAhae4FRPg9FNglhXApBTwRO1wepn5N8tCveUjosvPXduiQqXfAHttwt3
                # fzcrT+B4djHcJKITij5cATOJYnYWa20WjADgGqjSngwQJ5JO0alu4oLZAoGAD138
                # j203mzSY9iBTR+EozcLTVKxMVWGzkuMYqJw+uEGVKiw9wqJatb1X/2EdhzrcJ1VR
                # Cydfem/wUCarzFy+YRm3dhmVbn3TNx7xL2QYbejxwKWBYLMxeQd+9T9SsecXwwIx
                # pZMs1ssSgaXrCOSSkpIQS86CV+VczD0Rd1KL4s8CgYEAhfI92S/3eL6eOkm7yHL1
                # 4331R/gomiO4QehLpyUZfirpqxNO/8BL6f25Jp5cC3dJeNu4xEbbMIMpEpT9C+ZJ
                # 4WWYzDCC43HB8AbA8SgMDz7Vaa6h9zHJolLLrcsDMtiD4JT7VeV4UluWXIaRbg6p
                # XYwWQL2d6uGePDriQHXIUmY=
                # -----END PRIVATE KEY-----""",
                #     "client_email": "google-sheets-api@inbound-pattern-429101-c5.iam.gserviceaccount.com",
                #     "client_id": "107649396128661753097",
                #     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                #     "token_uri": "https://oauth2.googleapis.com/token",
                #     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                #     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/google-sheets-api%40inbound-pattern-429101-c5.iam.gserviceaccount.com",
                #     "universe_domain": "googleapis.com"
                # }

                # st.write(credentials_info)

                # Configurar los scopes correctos
                scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                creds = service_account.Credentials.from_service_account_info(credentials_info, scopes=scopes)

                # st.write(creds)

                # Autenticar cliente de Google Sheets
                client = gspread.authorize(creds)
                # Coloca tu sheet_id aquí
                sheet_id = '1J0YmuXlCFx_lg5DKGS_o_09nhkJaGVh7PLrjsyV2Nsc'  # Reemplaza con tu sheet_id real

                # Abre la hoja de Google usando el ID de la hoja
                sheet = client.open_by_key(sheet_id).sheet1

                df_merged_picking = df_merged_picking.fillna("0")
                df_merged_picking["Tarea Salteada"] = 1
                # Convirtiendo el DataFrame a una lista de listas
                df_values = df_merged_picking.values.tolist()
                
                # Escribe los datos en el Google Sheet, sobrescribiendo todo
                sheet.clear()  # Borrar el contenido anterior
                sheet.append_row(df_merged_picking.columns.tolist())  # Escribe los encabezados
                sheet.append_rows(df_values)  # Escribe los datos del DataFrame

                sheet_id_2 = '1wan5qrTo_7_oUnXBUXgCuq_oJa24F5U6uhpDOe_LGf8'  # Reemplaza con tu sheet_id real
                # Abre la hoja de Google usando el ID de la hoja
                sheet = client.open_by_key(sheet_id_2).sheet1

                df_merged_picking = df_merged_picking.fillna("0")
                # Convirtiendo el DataFrame a una lista de listas
                df_values = df_merged_picking.values.tolist()
                
                # Escribe los datos en el Google Sheet, sobrescribiendo todo
                sheet.clear()  # Borrar el contenido anterior
                sheet.append_row(df_merged_picking.columns.tolist())  # Escribe los encabezados
                sheet.append_rows(df_values)  # Escribe los datos del DataFrame


                st.success("¡Datos actualizados en Google Sheets con éxito!")



        else:
            st.write("Para realizar el merge, carga ambos archivos: 'Informe Stock con Operacion' y 'Reporte Posicionamiento'.")

else:
    pass

if "Control Total" in seleccion: 

    with tab5:
    
        st.title("Control Total")

        st.write(df_stock)


with tab6:

    st.title("Resultados")


    if "Control Picking" in seleccion:

        st.subheader("Control Picking")

        try:

            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = service_account.Credentials.from_service_account_info(credentials_info, scopes=scopes)
            client = gspread.authorize(creds)
            # Coloca tu sheet_id aquí
            sheet_id = '1wan5qrTo_7_oUnXBUXgCuq_oJa24F5U6uhpDOe_LGf8'  # Reemplaza con tu sheet_id real
            # Abre la hoja de Google usando el ID de la hoja
            sheet = client.open_by_key(sheet_id).sheet1
            # Obtiene todos los registros de la hoja
            data = sheet.get_all_records()
            # Convierte los datos a un DataFrame de pandas
            df_resultado_picking = pd.DataFrame(data)

            total_filas = len(df_resultado_picking)

            # Obtener la cantidad de filas no nulas en la columna 'HoraInicio'
            filas_no_nulas = df_resultado_picking['HoraInicio'].notna() & df_resultado_picking['HoraInicio'].astype(str).str.strip().ne('')
            filas_no_nulas = filas_no_nulas.sum()

            # Calcular el porcentaje de avance
            avance = (filas_no_nulas / total_filas)

            # Mostrar el porcentaje de avance en una barra de progreso en Streamlit
            st.progress(avance)

            # Mostrar el porcentaje en formato de texto
            st.write(f"Porcentaje de avance: {(avance)*100:.2f}%")

            df_resultado_picking = df_resultado_picking.sort_values('HoraFin', ascending=False)
            df_resultado_picking = df_resultado_picking.drop_duplicates(subset=['Cod.Articulo'], keep='first')  # Reemplazá 'ID' por tu columna clave

            # Filtrar las filas con 'Diferencia Unidades' distintas de 0, no nulas y no vacías
            df_resultado_picking = df_resultado_picking[
                df_resultado_picking['Diferencia Unidades'].ne(0) &
                df_resultado_picking['Diferencia Unidades'].notna() &
                df_resultado_picking['Diferencia Unidades'].astype(str).str.strip().ne('')
            ]

            df_resultado_picking_monitoreo = df_resultado_picking[["Entidad","Temperatura","Cod.Articulo","Descripcion Articulo","Posicion","Diferencia Unidades"]]

            st.write(df_resultado_picking_monitoreo)

            if st.button("Recontrolar Picking"):
                
                # Definir las columnas que se van a exportar
                # columnas = ["Cod.Articulo", "Temperatura", "Rubro", "Entidad", "Descripcion Articulo", 
                #              "Pasillo", "Columna", "Nivel", "Sector", "Posicion", "Bultos", "Unidades", 
                #              "Vencimiento", "Un.x Bulto", "Usuario"]
                #  df = df[columnas]
                df_resultado_picking = df_resultado_picking.loc[:, : "Usuario"]

                # ID de las hojas de Google Sheets
                sheet_ids = ["1J0YmuXlCFx_lg5DKGS_o_09nhkJaGVh7PLrjsyV2Nsc",
                    "1wan5qrTo_7_oUnXBUXgCuq_oJa24F5U6uhpDOe_LGf8"
                ]

                # Agregar datos en la última fila de ambas hojas
                for sheet_id in sheet_ids:
                    if agregar_a_google_sheets(df_resultado_picking, sheet_id):
                        st.success(f"¡Datos agregados en la última fila de Google Sheet con éxito!")

        except:
            pass


    if "Control Recepción" in seleccion:

        st.subheader("Control Recepción")

        try:

            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = service_account.Credentials.from_service_account_info(credentials_info, scopes=scopes)
            client = gspread.authorize(creds)
            # Coloca tu sheet_id aquí
            sheet_id = '1BFyf3o8jYCleLtKwaMD9b90ZPhJBE8-yXeq74En_B_M'  # Reemplaza con tu sheet_id real
            # Abre la hoja de Google usando el ID de la hoja
            sheet = client.open_by_key(sheet_id).sheet1
            # Obtiene todos los registros de la hoja
            data = sheet.get_all_records()
            # Convierte los datos a un DataFrame de pandas
            df_resultado_recepcion = pd.DataFrame(data)

            total_filas = len(df_resultado_recepcion)

            # Obtener la cantidad de filas no nulas en la columna 'HoraInicio'
            filas_no_nulas = df_resultado_recepcion['HoraInicio'].notna() & df_resultado_recepcion['HoraInicio'].astype(str).str.strip().ne('')
            filas_no_nulas = filas_no_nulas.sum()

            # Calcular el porcentaje de avance
            avance = (filas_no_nulas / total_filas)

            # Mostrar el porcentaje de avance en una barra de progreso en Streamlit
            st.progress(avance)

            # Mostrar el porcentaje en formato de texto
            st.write(f"Porcentaje de avance: {(avance)*100:.2f}%")

            df_resultado_recepcion = df_resultado_recepcion[
            (df_resultado_recepcion['Diferencia Unidades'].ne(0) & 
            df_resultado_recepcion['Diferencia Unidades'].notna() & 
            df_resultado_recepcion['Diferencia Unidades'].astype(str).str.strip().ne(''))
            |
            (df_resultado_recepcion['Diferencia Fecha Vencimiento'].ne(0) & 
            df_resultado_recepcion['Diferencia Fecha Vencimiento'].notna()& 
            df_resultado_recepcion['Diferencia Unidades'].astype(str).str.strip().ne(''))
            |
            (df_resultado_recepcion['Coincide Lote'].eq("No") & 
            df_resultado_recepcion['Coincide Lote'].notna())& 
            df_resultado_recepcion['Coincide Lote'].astype(str).str.strip().ne('')
            ]

            df_resultado_recepcion_monitoreo = df_resultado_recepcion[["Entidad","Temperatura","Articulo","Descripcion Articulo","Posicion","Diferencia Unidades","Diferencia Fecha Vencimiento","Coincide Lote","Coincide Pallet"]]

            st.write(df_resultado_recepcion_monitoreo)

            if st.button("Recontrolar Recepción"):
                

                # Definir las columnas que se van a exportar
                df_resultado_recepcion = df_resultado_recepcion.loc[:, : "Usuario"]

                # ID de las hojas de Google Sheets
                sheet_ids = ["1tpJAMDbUMANKitwywXEJ3_4Khm-DbJPAPxUbzva75cU",
                    "1BFyf3o8jYCleLtKwaMD9b90ZPhJBE8-yXeq74En_B_M"
                ]

                # Agregar datos en la última fila de ambas hojas
                for sheet_id in sheet_ids:
                    if agregar_a_google_sheets(df_resultado_recepcion, sheet_id):
                        st.success(f"¡Datos agregados en la última fila de Google Sheet con éxito!")

        except:

            pass


    if "Control Parciales" in seleccion:

        st.subheader("Control Parciales")

        try:

            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = service_account.Credentials.from_service_account_info(credentials_info, scopes=scopes)
            client = gspread.authorize(creds)
            # Coloca tu sheet_id aquí
            sheet_id = '1OuRlrf7RR7P1o0FGIGKIWLMjSFo62Aa3NgiEvpTx2Ps'  # Reemplaza con tu sheet_id real
            # Abre la hoja de Google usando el ID de la hoja
            sheet = client.open_by_key(sheet_id).sheet1
            # Obtiene todos los registros de la hoja
            data = sheet.get_all_records()
            # Convierte los datos a un DataFrame de pandas
            df_resultado_parciales = pd.DataFrame(data)

            total_filas = len(df_resultado_parciales)

            # Obtener la cantidad de filas no nulas en la columna 'HoraInicio'
            filas_no_nulas = df_resultado_parciales['HoraInicio'].notna() & df_resultado_parciales['HoraInicio'].astype(str).str.strip().ne('')
            filas_no_nulas = filas_no_nulas.sum()

            # Calcular el porcentaje de avance
            avance = (filas_no_nulas / total_filas)

            # Mostrar el porcentaje de avance en una barra de progreso en Streamlit
            st.progress(avance)

            # Mostrar el porcentaje en formato de texto
            st.write(f"Porcentaje de avance: {(avance)*100:.2f}%")

            df_resultado_parciales_unidades = df_resultado_parciales[
                (df_resultado_parciales['Diferencia Unidades'].ne(0)) & 
                (df_resultado_parciales['Diferencia Unidades'].notna()) & 
                (df_resultado_parciales['Diferencia Unidades'].astype(str).str.strip().ne(''))
            ]

            # Filtro para diferencias en fecha de vencimiento
            df_resultado_parciales_fecha = df_resultado_parciales[
                (df_resultado_parciales['Diferencia Fecha Vencimiento'].ne(0)) & 
                (df_resultado_parciales['Diferencia Fecha Vencimiento'].notna()) & 
                (df_resultado_parciales['Diferencia Fecha Vencimiento'].astype(str).str.strip().ne(''))
            ]

            df_resultado_parciales_concatenado = pd.concat([df_resultado_parciales_unidades, df_resultado_parciales_fecha],ignore_index=True)

            # Eliminar duplicados por la columna "Cod.Articulo"
            df_resultado_parciales_concatenado = df_resultado_parciales_concatenado.drop_duplicates(subset="Cod.Articulo", keep="first")

            df_resultado_parciales_unidades_monitoreo = df_resultado_parciales_unidades[["Entidad","Temperatura","Cod.Articulo","Descripcion Articulo","Posicion","Diferencia Unidades","Diferencia Fecha Vencimiento"]]
            df_resultado_parciales_fecha_monitoreo = df_resultado_parciales_fecha[["Entidad","Temperatura","Cod.Articulo","Descripcion Articulo","Posicion","Diferencia Unidades","Diferencia Fecha Vencimiento"]]

            st.write(df_resultado_parciales_unidades_monitoreo)

            # Botón 1 - Recontrolar Parciales Unidades

            if st.button("Recontrolar Parciales Unidades"):
                df_resultado_parciales_unidades = df_resultado_parciales_unidades.loc[:, : "Usuario"]

                sheet_ids = [
                    "1eikx9phIghxyiv1yfFy3ZqqNePWSbhkyvisOzSD37pw",
                    "1OuRlrf7RR7P1o0FGIGKIWLMjSFo62Aa3NgiEvpTx2Ps"
                ]

                for sheet_id in sheet_ids:
                    if agregar_a_google_sheets(df_resultado_parciales_unidades, sheet_id):
                        st.success(f"¡Datos agregados en la última fila de Google Sheet con éxito!")
            
            st.write(df_resultado_parciales_fecha_monitoreo)
        # Botón 2 - Recontrolar Parciales Fecha
            if st.button("Recontrolar Parciales Fecha"):
                df_resultado_parciales_fecha = df_resultado_parciales_fecha.loc[:, : "Usuario"]

                sheet_ids = [
                    "1eikx9phIghxyiv1yfFy3ZqqNePWSbhkyvisOzSD37pw",
                    "1OuRlrf7RR7P1o0FGIGKIWLMjSFo62Aa3NgiEvpTx2Ps"
                ]

                for sheet_id in sheet_ids:
                    if agregar_a_google_sheets(df_resultado_parciales_fecha, sheet_id):
                        st.success(f"¡Datos agregados en la última fila de Google Sheet con éxito!")
                    # Botón 2 - Recontrolar Parciales Fecha

            if st.button("Recontrolar Todo"):
                df_resultado_parciales_concatenado = df_resultado_parciales_concatenado.loc[:, : "Usuario"]

                sheet_ids = [
                    "1eikx9phIghxyiv1yfFy3ZqqNePWSbhkyvisOzSD37pw",
                    "1OuRlrf7RR7P1o0FGIGKIWLMjSFo62Aa3NgiEvpTx2Ps"
                ]

                for sheet_id in sheet_ids:
                    if agregar_a_google_sheets(df_resultado_parciales_concatenado, sheet_id):
                        st.success(f"¡Datos agregados en la última fila de Google Sheet con éxito!")

        except:

            pass
