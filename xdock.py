import streamlit as st
import pandas as pd

# Configure Streamlit page
st.set_page_config(page_title="Escaneo y Confirmación de Artículos", layout="wide")

# App title
st.title("Escaneo y Confirmación de Artículos")
st.write("Escanea el código del artículo y confirma la cantidad de bultos.")

with st.expander("Carga de archivos"):
    # File uploader for orders
    archivo_pedidos = st.file_uploader("Carga la tabla de pedidos", type=["xlsx", "csv"])

# Function to display data in a card format
def mostrar_carta(data_row):
    card_html = f"""
    <div style="border:1px solid #ddd; border-radius:8px; padding:16px; margin:16px 0; box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);">
        <div style="padding:10px; border-radius:6px 6px 0 0;">
            <h3 style="margin:0; font-size:1.5em;">Detalle de Pedido: {data_row["Nro. de Pedido"]}</h3>
        </div>
        <div style="padding:16px;">
            <p><strong>Artículo:</strong> {data_row["Artículo Código"]}</p>
            <p><strong>Fecha Entrega:</strong> {data_row["Fecha Entrega"]}</p>
            <p><strong>Cliente:</strong> {data_row["Entidad Cliente"]}</p>
            <p><strong>Cantidad Pedida:</strong> {data_row["Cantidad"]}</p>
            <p><strong>Cantidad Confirmada:</strong> {data_row["Cantidad Confirmada"]}</p>
            <p><strong>Cantidad Restante:</strong> {data_row["Diferencia"]}</p>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# Initialize a DataFrame to store confirmed quantities
if archivo_pedidos is not None:
    if 'df_pedidos' not in st.session_state:
        # Load the orders file into session state
        if archivo_pedidos.name.endswith('xlsx'):
            st.session_state.df_pedidos = pd.read_excel(archivo_pedidos)
        elif archivo_pedidos.name.endswith('csv'):
            st.session_state.df_pedidos = pd.read_csv(archivo_pedidos, encoding='ISO-8859-1', sep=';')
        
        # Convert "Nro. de Pedido" to integer and add "Cantidad Confirmada" if missing
        st.session_state.df_pedidos['Nro. de Pedido'] = pd.to_numeric(st.session_state.df_pedidos['Nro. de Pedido'], errors='coerce').fillna(0).astype(int)
        if 'Cantidad Confirmada' not in st.session_state.df_pedidos.columns:
            st.session_state.df_pedidos['Cantidad Confirmada'] = None

# Calculate "Diferencia" column
if 'df_pedidos' in st.session_state:
    st.session_state.df_pedidos['Cantidad Confirmada'].fillna(0, inplace=True)
    st.session_state.df_pedidos['Diferencia'] = st.session_state.df_pedidos['Cantidad'] - st.session_state.df_pedidos['Cantidad Confirmada']

    st.write("Datos del pedido cargado con columna de Diferencia:")
    st.dataframe(st.session_state.df_pedidos)

    # Input for article code scanning
    codigo_articulo = st.text_input("Escanea el código del artículo", max_chars=20)

    if codigo_articulo.isnumeric():
        codigo_articulo = int(codigo_articulo)
        
        # Filter for rows with differences to confirm
        df_resultado = st.session_state.df_pedidos[
            (st.session_state.df_pedidos['Artículo Código'] == codigo_articulo) &
            (st.session_state.df_pedidos['Cantidad'] != st.session_state.df_pedidos['Cantidad Confirmada'])
        ]

        if not df_resultado.empty:
            st.success(f"Artículo {codigo_articulo} encontrado.")
            
            # Display each row in df_resultado
            for index, row in df_resultado.iterrows():
                mostrar_carta(row)
                # Confirm quantity input
                cantidad_confirmada = st.number_input(
                    f"Confirma la cantidad de bultos para el pedido {row['Nro. de Pedido']}",
                    min_value=0,
                    max_value=int(row['Diferencia']),
                    value=int(row['Diferencia']),
                    key=f"cantidad_confirmada_{index}"
                )

                # Unique confirm button per row
                if st.button(f"Confirmar cantidad para el pedido {row['Nro. de Pedido']}", key=f"confirm_button_{index}"):
                    # Update "Cantidad Confirmada" for the specific article in session state
                    st.session_state.df_pedidos.loc[
                        (st.session_state.df_pedidos['Artículo Código'] == codigo_articulo) & 
                        (st.session_state.df_pedidos['Nro. de Pedido'] == row['Nro. de Pedido']),
                        'Cantidad Confirmada'
                    ] = row['Cantidad Confirmada'] + cantidad_confirmada
                    # Recalculate "Diferencia" after updating
                    st.session_state.df_pedidos['Diferencia'] = st.session_state.df_pedidos['Cantidad'] - st.session_state.df_pedidos['Cantidad Confirmada']
                    st.write(f"Cantidad confirmada: {cantidad_confirmada} bultos para el artículo {codigo_articulo} en el pedido {row['Nro. de Pedido']}.")
                    st.write("Tabla actualizada con la cantidad confirmada y diferencia:")
                    st.dataframe(st.session_state.df_pedidos)
        elif codigo_articulo not in st.session_state.df_pedidos['Artículo Código'].values:
            st.error(f"El artículo {codigo_articulo} no se encuentra en la tabla de pedidos.")
        else:
            st.info(f"No quedan artículos por asignar a pedidos para el artículo {codigo_articulo}.")
    elif codigo_articulo:
        st.error("Por favor ingresa un código de artículo numérico.")

    # Group by "Artículo Código" and sum "Diferencia"
    diferencia_por_articulo = st.session_state.df_pedidos.groupby('Artículo Código')['Diferencia'].sum().reset_index()

    # Filter to show only rows where "Diferencia" is greater than 0
    diferencia_por_articulo = diferencia_por_articulo[diferencia_por_articulo['Diferencia'] > 0]

    # Define a function to apply conditional formatting
    def highlight_difference(val):
        color = 'background-color: #ff9999' if val > 0 else ''  # Light red background for differences > 0
        return color

    # Apply the style
    styled_df = diferencia_por_articulo.style.applymap(highlight_difference, subset=['Diferencia'])

    st.write("Suma de diferencias por Artículo Código (diferencia > 0):")
    st.dataframe(styled_df)
