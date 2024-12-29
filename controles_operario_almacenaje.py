import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime

# App title
st.title("Escaneo y Control de Almacenaje")

# URL de la hoja de Google Sheets
sheet_url = 'https://docs.google.com/spreadsheets/d/15mDNh1PKS6SjxtGvEasMJvBWxt7BuWOH-IpRKbPHNwA/edit?gid=0#gid=0'

# Extraer el ID de la hoja y obtener el enlace al CSV
sheet_id = sheet_url.split("/d/")[1].split("/")[0]
data_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv'

# Registro de hora de inicio
if "HoraInicio" not in st.session_state:
    st.session_state.HoraInicio = {}

# Función para mostrar la información en formato de carta
def mostrar_carta(data_row,posicion):
    card_html = f"""
    <div style="border:1px solid #ddd; border-radius:8px; padding:16px; margin:16px 0; box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);">
        <div style="padding:10px;">
            <h3 style="margin:0; font-size:1.5em;">{data_row["Posicion"]}</h3>
            <h3 style="margin:0; font-size:1.5em;">Status Posicion: {data_row["Status Posicion"]}</h3>
        </div>
        <div style="padding:16px;">
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


    # Campos de entrada
    # posicion = st.text_input("Escanea la posición", value=st.session_state.escaneada_posicion)
    
    if posicion == data_row['Posicion']:

        if posicion not in st.session_state.HoraInicio:
            hora_inicio = datetime.now()
            st.session_state.HoraInicio[posicion] = hora_inicio.strftime("%d-%m-%Y %H:%M:%S")

        if data_row["Status Posicion"] == "DL":
            
            posicion_libre = st.radio("¿Existe algún Pallet en la posición?", options=["Sí", "No"])
            articulo = 0 
            fecha = 0
            cantidad_bultos = 0
            unidades_bulto = 0
            blister_bulto = 0
            unidades_blister = 0 

        elif data_row["Status Posicion"].isin(["PC,PV"]):
            
            posicion_libre = "No"
            articulo = st.number_input(f"Escanea el artículo para la posición {data_row['Posicion']}", min_value=0,value=None)
            fecha = st.date_input(f"Selecciona la fecha de vencimiento para la posición {data_row['Posicion']}")
            fecha = fecha.strftime("%d-%m-%Y")
            cantidad_bultos = 0
            unidades_bulto = 0
            blister_bulto = 0
            unidades_blister = 0 



        elif data_row["Status Posicion"] == "BL":
            
            posicion_libre = "No"
            # cantidad_confirmada = st.number_input(f"Confirma la cantidad de bultos para la posición {data_row['Posicion']}", min_value=0,value=None)
            fecha = 0
            articulo = 0

            tiene_blister = st.radio("¿Tiene Blister?", options=["Sí", "No"])  

            if tiene_blister == "No":
                cantidad_bultos = st.number_input(f"Confirma la cantidad de BULTO para la posición ", min_value=0,value=None)
                unidades_bulto = st.number_input(f"Confirma la cantidad de UNIDADES POR BULTO para la posición ", min_value=0,value=None)
                blister_bulto = 0
                unidades_blister = 0 

            elif tiene_blister == "Sí":
                cantidad_bultos = st.number_input(f"Confirma la cantidad de BULTOS para la posición ", min_value=0,value=None)
                blister_bulto = st.number_input(f"Confirma la cantidad de BLISTER POR BULTO para la posición ", min_value=0,value=None)
                unidades_blister = st.number_input(f"Confirma la cantidad de UNIDADES POR BLISTER para la posición ", min_value=0,value=None)
                unidades_bulto = 0    
  
    # Campos de entrada
    
        # Actualizar el DataFrame en session_state
        posicion = data_row["Posicion"]
        st.session_state.df.loc[st.session_state.df["Posicion"] == posicion, "Articulo Escaneado"] = articulo
        st.session_state.df.loc[st.session_state.df["Posicion"] == posicion, "Posición Libre"] = posicion_libre
        st.session_state.df.loc[st.session_state.df["Posicion"] == posicion, "Fecha Vencimiento Observada"] = fecha
        st.session_state.df.loc[st.session_state.df["Posicion"] == posicion, "HoraInicio"] = st.session_state.HoraInicio[posicion]
        st.session_state.df.loc[st.session_state.df["Posicion"] == posicion, "Bultos Contados"] = cantidad_bultos
        st.session_state.df.loc[st.session_state.df["Posicion"] == posicion, "Blister por Bulto"] = blister_bulto
        st.session_state.df.loc[st.session_state.df["Posicion"] == posicion, "Unidad por Blister"] = unidades_blister
        st.session_state.df.loc[st.session_state.df["Posicion"] == posicion, "Unidad por Bulto"] = unidades_bulto

        if st.button("Tarea Terminada"):

            hora_fin = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            fecha_control = datetime.now().strftime("%d-%m-%Y")
            st.session_state.df.loc[st.session_state.df["Posicion"] == posicion, "HoraFin"] = hora_fin
            st.session_state.df.loc[st.session_state.df["Posicion"] == posicion, "Fecha"] = fecha_control

            if posicion == current_row_data["Posicion"]:
                st.success("Tarea completada para la posición.")
                # Reinicia la entrada de posición escaneada
                st.session_state.escaneada_posicion = ""  # Reinicia el campo de texto
                # Incrementa la fila actual
                st.session_state.current_row += 1
                st.experimental_rerun()

    else: 
        st.warning("La posición ingresada es incorrecta.")

# Cargar los datos de Google Sheets si no están en session_state
if "df" not in st.session_state:
    st.session_state.df = pd.read_csv(data_url)
    st.session_state.df = st.session_state.df.dropna(subset=['Posicion'])
    st.session_state.df["Posicion"] = st.session_state.df["Posicion"].str.rstrip()
    st.session_state.df['Ordenar_primero'] = st.session_state.df['Posicion'].str.split(' - ').str[0].str[2:4]
    st.session_state.df['Ordenar_segundo'] = st.session_state.df['Posicion'].str.split(' - ').str[1].astype(int)
    st.session_state.df = st.session_state.df.sort_values(by=['Ordenar_primero', 'Ordenar_segundo']).drop(columns=['Ordenar_primero', 'Ordenar_segundo'])
    # st.session_state.df[['Articulo Escaneado','Bultos Contados','Fecha Vencimiento Observada',"Posición Libre"]] = None

# Inicializar la fila actual si no existe
if "current_row" not in st.session_state:
    st.session_state.current_row = 0  # Inicializar la fila actual

if "escaneada_posicion" not in st.session_state:
        st.session_state.escaneada_posicion = ""  # Inicializar el valor como vacío

# Verificar si hay más filas para procesar
if st.session_state.current_row < len(st.session_state.df):
    # Mostrar la información de la fila actual
    

    posicion = st.text_input("Escanea la posición", value=st.session_state.escaneada_posicion)
    current_row_data = st.session_state.df.iloc[st.session_state.current_row]
    mostrar_carta(current_row_data,posicion)


else:
    st.write("Todas las filas han sido procesadas.")

# Botón final para actualizar el Google Sheet con todos los cambios
if st.button("Actualizar Google Sheets"):

    credentials_info = st.secrets["gcp_service_account"]

    # credentials_info = {
    #                 "type": "service_account",
    #                 "project_id": "inbound-pattern-429101-c5",
    #                 "private_key_id": "9dcc01743c917fb186294a8c6d228d4c2fb005bc",
    #                 "private_key": """-----BEGIN PRIVATE KEY-----
    #             MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDPvpK+357PGmvc
    #             6jxJTHyKfpUs/2861MGvfClaGMjEw9G8YmeeeH8PAkc/rZxaHpl2zcmpUQfTauxs
    #             0mhbOD42jxRflbdi00yvHVkBBtYdzfvtGwepEUsP26yqOySm6PiVI/XKHWdct61B
    #             28l/VW+mjXDVPiDiMATQRTJi4tYTgC5eSjhnkT4efY7gUMHmO2057cI+jmRob1WV
    #             PEEWLGt76R4IGnH/FtoW2B6lPoOb7KefRx2WgHfTu+zsXvqmbGbgRLSlheG4Zb6g
    #             h0dZXcyojx5vGgJT3ty4o5XgpA6n9EH2uURDXUBYQ9KE8mcNDM9VK6KQEYeBmIJr
    #             QOvMftM1AgMBAAECggEAAn4NSNdS4/vtzVvknLk+SUTmmuklQvARPtBfK1zqZSza
    #             cQ1XARha/p3r7ReQCpAFyJinRharmulIrFJJjmmF4HdUnycjIxxNUyH5GJLgJpM1
    #             cY1Ad6PNkKZSsKH41iVDCGk3N8mk4tH5rynGKKViwreabZX5sEuQdiEIlRXchgLN
    #             ransgsarOU/8+RI2W5JRt7wPAO56WsZc+zeOIyLS7RScibfdi8wMQYZF7PsPB5EG
    #             6ps50hxHWZ18lgLgJO5iK6YZkINHwW8AWDaxonxTgn4eYT8iUDMol8D5i2AXM5x1
    #             JnRzhLKnNUdzug4RB7XrcCOsjoDOU2dW1VbXTNkyxQKBgQD4WbO23ktbkl64dmdA
    #             ZKhRSRcBfbUf8/+Olp8Dt/PTb53Rjvsm3XK5EUK6t9oMGgL131UuOcKysV1RCyzT
    #             I5jjiY5Q3Ws2L0N2IFfxSBI7Di2hxSWLaXgETsMUV0MBfv1TH/8E+3tEtoj26lZY
    #             A0GVOrGprEJVNcL3X3T83R3mNwKBgQDWJK8icbaJujm9HfXi9ODcG7YpPYKRcqJa
    #             LZclOiccRHIUN4SzouIfB6kp63k96W5Yzm6GeRgaiB/LQNPNTDFO4Q7Zrm7wci9o
    #             kzRUHWJcgKl7r8Q+TYXBPJVn0dZe65G5O/d+7cmQn+MUp0Gi5cnYu9eaeKHoJGY0
    #             P6vCKhab8wKBgC2cK8k14hkbNJIkDKpi0ha7maIIeC86HIEPYHzKV9lI8m7+F1n3
    #             6Y3bganRAhae4FRPg9FNglhXApBTwRO1wepn5N8tCveUjosvPXduiQqXfAHttwt3
    #             fzcrT+B4djHcJKITij5cATOJYnYWa20WjADgGqjSngwQJ5JO0alu4oLZAoGAD138
    #             j203mzSY9iBTR+EozcLTVKxMVWGzkuMYqJw+uEGVKiw9wqJatb1X/2EdhzrcJ1VR
    #             Cydfem/wUCarzFy+YRm3dhmVbn3TNx7xL2QYbejxwKWBYLMxeQd+9T9SsecXwwIx
    #             pZMs1ssSgaXrCOSSkpIQS86CV+VczD0Rd1KL4s8CgYEAhfI92S/3eL6eOkm7yHL1
    #             4331R/gomiO4QehLpyUZfirpqxNO/8BL6f25Jp5cC3dJeNu4xEbbMIMpEpT9C+ZJ
    #             4WWYzDCC43HB8AbA8SgMDz7Vaa6h9zHJolLLrcsDMtiD4JT7VeV4UluWXIaRbg6p
    #             XYwWQL2d6uGePDriQHXIUmY=
    #             -----END PRIVATE KEY-----""",
    #                 "client_email": "google-sheets-api@inbound-pattern-429101-c5.iam.gserviceaccount.com",
    #                 "client_id": "107649396128661753097",
    #                 "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    #                 "token_uri": "https://oauth2.googleapis.com/token",
    #                 "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    #                 "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/google-sheets-api%40inbound-pattern-429101-c5.iam.gserviceaccount.com",
    #                 "universe_domain": "googleapis.com"
    #             }

    # Configurar las credenciales y el cliente de Google Sheets
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = service_account.Credentials.from_service_account_info(credentials_info, scopes=scopes)
    client = gspread.authorize(creds)
    # Coloca tu sheet_id aquí
    sheet_id = '1fiXf-4qL1SkUrZdLQQGENuS_EFd1R6F9RuKwFhL7mFg'  # Reemplaza con tu sheet_id real

    # Abre la hoja de Google usando el ID de la hoja
    sheet = client.open_by_key(sheet_id).sheet1

    st.session_state.df["Unidades Contadas"] = st.session_state.df["Bultos Contados"] * st.session_state.df["Blister por Bulto"] * st.session_state.df["Unidad por Blister"]  * st.session_state.df["Unidad por Blister"] + st.session_state.df["Bultos Contados"] * st.session_state.df["Unidad por Bulto"] 
    st.session_state.df["Diferencia Unidades"] = st.session_state.df["Unidades Contadas"] -  st.session_state.df["Unidades"]


    st.session_state.df['Vencimiento'] = pd.to_datetime(st.session_state.df['Vencimiento'], format='%d-%m-%Y', errors='coerce')
    st.session_state.df['Fecha Vencimiento Observada'] = pd.to_datetime(st.session_state.df['Fecha Vencimiento Observada'], format='%d-%m-%Y', errors='coerce')
    st.session_state.df["Diferencia Fecha Vencimiento"] = (st.session_state.df['Vencimiento'] - st.session_state.df['Fecha Vencimiento Observada']).dt.days
    
    # Convertir todas las fechas a cadenas para evitar problemas de serialización
    st.session_state.df['Vencimiento'] = st.session_state.df['Vencimiento'].dt.strftime('%d-%m-%Y')
    st.session_state.df['Fecha Vencimiento Observada'] = st.session_state.df['Fecha Vencimiento Observada'].dt.strftime('%d-%m-%Y')

    st.session_state.df.fillna(0, inplace=True)
    st.session_state.df = st.session_state.df.loc[:, ~st.session_state.df.columns.str.contains("Unnamed")]
    # Convirtiendo el DataFrame a una lista de listas
    df_values = st.session_state.df.values.tolist()
    
    # Escribe los datos en el Google Sheet, sobrescribiendo todo
    sheet.clear()  # Borrar el contenido anterior
    sheet.append_row(st.session_state.df.columns.tolist())  # Escribe los encabezados
    sheet.append_rows(df_values)  # Escribe los datos del DataFrame

    st.success("¡Datos actualizados en Google Sheets con éxito!")








